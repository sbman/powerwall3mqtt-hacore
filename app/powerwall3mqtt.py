#!/usr/bin/python3
"""
Powerwall 3 to MQTT for Home Assistant
"""

import json
import logging
import logging.config
import os
import random
import re
import signal
import socket
import sys
import threading
import time

from selectors import DefaultSelector, EVENT_READ
from threading import Condition, RLock

from paho.mqtt import client as mqtt_client
import requests.exceptions
import yaml

import hamqtt.devices
import pytedapi
import pytedapi.exceptions

from hamqtt.devices import OFFLINE


# Generate a Client ID with the publish prefix.
MQTT_ID = f'powerwall3mqtt-{random.randint(0, 1000)}'
WILL_TOPIC = f"{MQTT_ID}/will"

hamqtt.devices.origin['name'] = 'powerwall3mqtt'
#hamqtt.devices.origin['sw'] = '0.0.0'
#hamqtt.devices.origin['url'] = ''


with open("logger.yaml", 'r', encoding="utf-8") as stream:
    try:
        logging.config.dictConfig(yaml.safe_load(stream))
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit(1)

# Setup logging for this module
logger = logging.getLogger(__name__)


class FatalError(Exception):
    """FataError exception used to break from the main run loop"""


class Powerwall3MQTT:
    """Main Powerwall 3 to MQTT application class"""
    def __init__(self):
        self._pause = False
        self._running = True
        self._run_lock = RLock()
        self._loop_wait = Condition(self._run_lock)
        self._update_loop = socket.socketpair()
        self._config = self.loadconfig()

        # Set the logging level
        logging.getHandlerByName('console').setLevel(self._config['log_level'].upper())

        logger.debug("Runtime config:")
        for key in sorted(self._config.keys()):
            if key.find('password') == -1:
                logger.debug("config['%s'] = '%s'", key, self._config[key])
            else:
                redacted = re.sub('.', 'X', self._config[key])
                logger.debug("config['%s'] = '%s'", key, redacted)


    def loadconfig(self) -> dict:
        """Method to load and build a config dictionary"""
        config = {
            'log_level': 'WARNING',
            'tedapi_host': pytedapi.GW_IP,
            'tedapi_password': None,
            'tedapi_poll_interval': 30,
            'tedapi_report_vitals': False,
            'mqtt_base_topic': 'homeassistant',
            'mqtt_host': None,
            'mqtt_port': 1883,
            'mqtt_username': None,
            'mqtt_password': None,
            'mqtt_verify_tls': False,
            'mqtt_ssl': False,
            'mqtt_ca': None,
            'mqtt_cert': None,
            'mqtt_key': None
        }

        # Try to read options.json from HA, but ignore errors
        try:
            with open('/data/options.json', 'r', encoding="utf-8") as options:
                config = config | json.load(options)
        except Exception: # pylint: disable=W0718
            pass

        # Use ENV vars for overrides
        for k, item in config.items():
            value = os.environ.get(f"POWERWALL3MQTT_CONFIG_{k.upper()}", item)
            if isinstance(item, bool):
		config[k] = False if value=="False" else True
            elif isinstance(item,  int):
                config[k] = int(value)
            else:
                config[k] = value

        self.validate(config)
        return config


    def validate(self, config: dict) -> None:
        """Method to validate the required keys are in the config dictionary"""
        if config['tedapi_password'] is None:
            raise FatalError("tedapi_password not set")
        if None in (config['mqtt_host'], config['mqtt_port']):
            raise FatalError("MQTT connection info not set")
        if None in (config['mqtt_username'], config['mqtt_password']):
            raise FatalError("MQTT authentication info not set")
        if config['tedapi_poll_interval'] < 5:
            raise FatalError("Polling Interval must be >= 5")
        if (config['mqtt_cert'] is not None) ^ (config['mqtt_key'] is not None):
            raise FatalError("MQTT Certifcate and Key are both required")



    def connect_mqtt(self):
        """Method used to setup the connection to MQTT"""
        ha_status = socket.socketpair()

        def on_ha_status(client, userdata, message):
            """Callback method to receive online/offline notifications from a topic"""
            # pylint: disable=W0613 # method signature
            if message.payload == b'online':
                ha_status[1].send(b'\1')
            else:
                ha_status[1].send(b'\0')

        def on_connect(client, userdata, flags, rc, properties):
            """Callback method to handle handle MQTT connection events"""
            # pylint: disable=W0613 # method signature
            # pylint: disable=W0212 # userdata is self
            if rc == 0:
                logger.info("Connected to MQTT Broker '%s:%s'",
                    userdata._config['mqtt_host'],
                    userdata._config['mqtt_port'])
                topic = f"{userdata._config['mqtt_base_topic']}/status"
                client.message_callback_add(topic, on_ha_status)
                client.subscribe(topic)
                logger.info("Subscribed to MQTT topic '%s'", topic)
            else:
                logger.error("Failed to connect, return code = %s", rc.getName())

        client = mqtt_client.Client(
            client_id=MQTT_ID,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.user_data_set(self)
        client.will_set(WILL_TOPIC, OFFLINE)
        logger.debug("MQTT will set on '%s' to '%s'", WILL_TOPIC, OFFLINE)
        if self._config['mqtt_ssl']:
            client.tls_set(
                ca_certs=self._config['mqtt_ca'],
                certfile=self._config['mqtt_cert'],
                keyfile=self._config['mqtt_key'])
            client.tls_insecure_set(self._config['mqtt_verify_tls'])
        client.username_pw_set(
            self._config['mqtt_username'],
            self._config['mqtt_password'])
        client.connect(self._config['mqtt_host'], self._config['mqtt_port'])
        return client, ha_status[0]


    def get_pause(self):
        """Method to get the current pause state using the run_lock"""
        with self._run_lock:
            return self._pause


    def get_running(self):
        """Method to get the current run state used the run_lock"""
        with self._run_lock:
            return self._running


    def set_pause(self, pause):
        """Method to set the pause state using the run_lock"""
        with self._run_lock:
            self._pause = pause
            if not pause:
                self._loop_wait.notify()


    def set_running(self, running):
        """Method to set the run state using the run_lock"""
        with self._run_lock:
            self._running = running
            if not running:
                self._loop_wait.notify()


    def discover(self, mqtt, tesla):
        """Method to get Tesla system discovery messages and publish them to MQTT"""
        discovery = tesla.get_discoveries(
                        prefix=self._config['mqtt_base_topic'],
                        will_topic=WILL_TOPIC)
        # Send Discovery
        for message in discovery:
            result = mqtt.publish(message['topic'], json.dumps(message['payload']))
            if result[0] == 0:
                logger.info("Discovery sent to '%s'", message['topic'])
                logger.debug("message = %s", json.dumps(message['payload']))
            else:
                logger.warning("Failed to send '%s' to '%s'", message['topic'], message['payload'])
        logger.info("Sleeping 0.5s to allow HA to process discovery")
        time.sleep(0.5)


    def main_loop(self, shutdown, ha_status, mqtt, tesla):
        """The main program loop"""
        sel = DefaultSelector()
        sel.register(shutdown, EVENT_READ)
        sel.register(ha_status, EVENT_READ)
        sel.register(self._update_loop[0], EVENT_READ)

        while True:
            for key, _ in sel.select():
                try:
                    if key.fileobj == shutdown:
                        shutdown.recv(1)
                        logger.info("Received shutdown signal")
                        self.set_running(False)
                        return
                    if key.fileobj == ha_status:
                        cmd = ha_status.recv(1)
                        if cmd == b'\01':
                            logger.info("Received ha_status online")
                            self.discover(mqtt, tesla)
                            self.set_pause(False)
                        else:
                            logger.info("Received ha_status offline")
                            self.set_pause(True)
                    elif key.fileobj == self._update_loop[0]:
                        self._update_loop[0].recv(1)
                        logger.debug("Processing update from timing_loop")
                        self.update(mqtt, tesla, True)
                except pytedapi.exceptions.TEDAPIRateLimitingException as e:
                    self._config['tedapi_poll_interval'] += 1
                    logger.warning(e)
                    logger.warning(
                        "Increasing poll interval by 1s to %d",
                        self._config['tedapi_poll_interval'])
                except pytedapi.exceptions.TEDAPIException as e:
                    # Likely fatal, bail out
                    self.set_running(False)
                    raise e
                except TimeoutError as e:
                    # Likely lock timeout, skip interval
                    logger.warning(e, exc_info=True)
                except Exception as e: # pylint: disable=W0718
                    # Catchall so the loop keeps going
                    logger.exception(e)


    def run(self):
        """The main program entry point"""
        shutdown = socket.socketpair()

        def catch(signum, frame):
            """Method used to catch signals and notify the main loop to shutdown"""
            # pylint: disable=W0613 # method signature
            shutdown[1].send(b'\0')

        # Setup signal handling
        signal.signal(signal.SIGINT, catch)
        signal.signal(signal.SIGTERM, catch)

        # Connect to remote services
        mqtt, ha_status = self.connect_mqtt()
        try:
            tedapi = pytedapi.TeslaEnergyDeviceAPI(
                self._config['tedapi_password'],
                host=self._config['tedapi_host'])
            powerwall = pytedapi.Powerwall3API(
                tedapi,
                cacheexpire=4,
                configexpire=29)
        except requests.exceptions.ConnectionError as e:
            raise FatalError("Unable to connect to Powerwall") from e
        if not tedapi.is_powerwall3():
            raise FatalError("Powerwall appears to be older than Powerwall 3")

        # Populate Tesla info
        tesla = hamqtt.devices.TeslaSystem(
            powerwall,
            self._config['tedapi_report_vitals'])
        logger.info("Powerwall firmware version = %s", tesla.firmware_version)

        mqtt.loop_start()
        try:
            timer = threading.Thread(target=self.timing_loop)
            timer.start()
            try:
                self.discover(mqtt, tesla)
                self.update(mqtt, tesla, True)
                self.main_loop(shutdown=shutdown[0], ha_status=ha_status, mqtt=mqtt, tesla=tesla)
            finally:
                self.set_running(False)
                timer.join()
        finally:
            mqtt.loop_stop()


    def timing_loop(self):
        """A method to run in a separate thread to trigger updates to MQTT"""
        with self._loop_wait:
            while self.get_running():
                self._loop_wait.wait(self._config['tedapi_poll_interval'])
                if not self.get_pause():
                    self._update_loop[1].send(b'\1')


    def update(self, mqtt, tesla, update=False):
        """Method to get Tesla system state messages and publish them to MQTT"""
        if update:
            tesla.update()
        sysstate = tesla.get_states(prefix=self._config['mqtt_base_topic'])
        for message in sysstate:
            result = mqtt.publish(message['topic'], json.dumps(message['payload']))
            if result[0] == 0:
                logger.info("Sent message to '%s'", message['topic'])
                logger.debug("message = %s", json.dumps(message['payload']))
            else:
                logger.warning("Failed to send '%s' to '%s'", message['topic'], message['payload'])



if __name__ == '__main__':
    try:
        app = Powerwall3MQTT()
        app.run()
    except FatalError as e:
        logger.critical("Exiting: %s", e)
        sys.exit(1)
    except Exception as e: # pylint: disable=W0718
        # Catch all so all exceptions get logged properly
        logger.exception(e)
        sys.exit(1)
    finally:
        logging.shutdown()
