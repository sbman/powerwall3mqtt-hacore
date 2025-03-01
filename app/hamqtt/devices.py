"""Module providing classes that map to HA devices as used for MQTT discovery"""

import logging

from . import entities

ONLINE = b'online'
OFFLINE = b'offline'

logger = logging.getLogger(__name__)
origin = {}


def _get_item_value(dicts, match_name, match_value, get_value):
    for p in dicts:
        if p.get(match_name).lower() == match_value.lower():
            return p.get(get_value)
    return None


def _get_power(dicts, name):
    return _get_item_value(dicts, 'location', name, 'realPowerW')


class Device:
    """Base class for Devices"""
    def __init__(self, name: str, device_id: str, parent: str = None) -> None:
        self.name = name
        self.device_id = device_id
        self.via = parent
        self._updated = False


    def get_discovery(self, prefix: str, will_topic: str) -> dict:
        """Generates an MQTT discovery message to send to HA"""
        config_topic = f"{prefix}/device/{self.device_id}/config"
        state_topic = f"{prefix}/device/{self.device_id}/state"

        msg = {}
        msg['topic'] = config_topic
        msg['payload'] = {}
        msg['payload']['dev'] = {}
        msg['payload']['dev']['ids'] = self.device_id
        msg['payload']['dev']['name'] = self.name
        if self.via is not None:
            msg['payload']['dev']['via_device'] = self.via
        msg['payload']['state_topic'] = state_topic
        msg['payload']['availability'] = []
        msg['payload']['availability'].append({'topic': state_topic})
        msg['payload']['availability'][0]['value_template'] = '{{ value_json.mqtt_availability }}'
        msg['payload']['availability'].append({'topic': will_topic})
        msg['payload']['o'] = origin
        cmps = {}
        for name, value in vars(self).items():
            if issubclass(type(value), entities.Entity):
                cmps[name] = value.get_discovery()
        msg['payload']['cmps'] = cmps
        return msg


    def recurse(self, item):
        """Recursively build a nested dictionary matching the structure of the device"""
        if issubclass(type(item), entities.Entity):
            return item.get()
        if issubclass(type(item), dict):
            values = {}
            for i in item.keys():
                value = self.recurse(item[i])
                if value is not None:
                    values[i] = value
            if len(values):
                return values
        return None


    def get_state(self, prefix: str) -> dict:
        """Generates an MQTT state message to send to HA"""
        msg = {}
        msg['topic'] = f"{prefix}/device/{self.device_id}/state"
        msg['payload'] = {}
        msg['payload']['mqtt_availability'] = "offline"
        if self._updated:
            msg['payload']['mqtt_availability'] = "online"
        for name, value in vars(self).items():
            if issubclass(type(value), entities.ValueEntity):
                msg['payload'][name] = value.get()
            elif issubclass(type(value), dict):
                value = self.recurse(value)
                if value is not None:
                    msg['payload'][name] = value
        return msg


    def get_updated(self) -> bool:
        """Getter method for updated marker"""
        return self._updated


    def set_name(self, name: str) -> None:
        """Setter method for device name"""
        self.name = name


    def set_updated(self, updated: bool) -> None:
        """Setter method for updated marker"""
        self._updated = updated


class PowerWall3(Device):
    """A class that maps a Powerwall 3 system component to an HA device"""
    def __init__(self, parent, vin, tedapi) -> None:
        self.tedapi = tedapi

        config = tedapi.get_config()
        logger.debug("config = %r", config)

        self.vin = vin
        self.type = _get_item_value(config['battery_blocks'], 'vin', vin, 'type')
        name = f"{config['site_info']['site_name']} {self.vin.split('--')[1]}"
        device_id = f"{self.type}_{self.vin}"
        super().__init__(name=name, device_id=device_id, parent=parent)


        # Home Assistant Components
        self.battery_capacity = entities.EnergyStorage(device_id, "Battery Capacity")
        self.battery_remaining = entities.EnergyStorage(device_id, "Battery Remaining")

        # Default disable PV String info
        self.strings = {}
        for i in 'ABCDEF':
            key = f"strings['{i}']"
            self.strings[i] = {}
            self.strings[i]['mode'] = entities.ValueEntity(
                device_id,
                f"PV String {i} Mode", 'sensor',
                template = f"{key}.mode",
                enabled = False)
            self.strings[i]['current'] = entities.Current(
                device_id,
                f"PV String {i} Current",
                template = f"{key}.current",
                enabled = False)
            self.strings[i]['voltage'] = entities.Voltage(
                device_id,
                f"PV String {i} Voltage",
                template = f"{key}.voltage",
                enabled = False)
            self.strings[i]['power'] = entities.PowerValue(
                device_id,
                f"PV String {i} Power",
                template = f"{key}.power",
                enabled = False)


    def update(self) -> None:
        """Updates the name and values for all components using data from the PW"""
        self.set_updated(False)
        config = self.tedapi.get_config()
        logger.debug("config = %r", config)

        self.set_name(f"{config['site_info']['site_name']} {self.vin.split('--')[1]}")

        data = self.tedapi.get_pw_vitals(self.vin)
        logger.debug("vitals = %r", data)

        for signal in data['components']['bms'][0]['signals']:
            match signal['name']:
                case "BMS_nominalEnergyRemaining":
                    self.battery_remaining.set(int(signal['value'] * 1000))
                case "BMS_nominalFullPackEnergy":
                    self.battery_capacity.set(int(signal['value'] * 1000))

        for i, item in self.strings.items():
            pv_voltage = 0
            pv_current = 0
            for component in data['components']['pch']:
                signals = component['signals']
                for signal in signals:
                    if signal['name'] == f'PCH_PvState_{i}':
                        item['mode'].set(signal['textValue'])
                    elif signal['name'] == f'PCH_PvVoltage{i}':
                        pv_voltage = round(max(signal['value'], 0), 2)
                        item['voltage'].set(pv_voltage)
                    elif signal['name'] == f'PCH_PvCurrent{i}':
                        pv_current = round(max(signal['value'], 0), 2)
                        item['current'].set(pv_current)
            # Calculate power
            pv_power = pv_voltage * pv_current
            item['power'].set(round(pv_power, 2))
        self.set_updated(True)


    def get_discovery(self, prefix: str, will_topic: str) -> dict:
        """Generates an MQTT discovery message to send to HA"""
        msg = super().get_discovery(prefix=prefix, will_topic=will_topic)
        msg['payload']['dev']['mf'] = 'Tesla'
        msg['payload']['dev']['mdl'] = 'Powerwall3'
        msg['payload']['dev']['mdl_id'] = self.vin.split('--')[0]
        msg['payload']['dev']['sn'] = self.vin.split('--')[1]
        for i, s in self.strings.items():
            for item, value in s.items():
                msg['payload']['cmps'][f"string_{i}_{item}"] = value.get_discovery()
        return msg



class TeslaSystem(Device):
    """A class that maps a Powerwall 3 based Tesla Energy system to an HA device"""
    # pylint: disable=R0902
    def __init__(self, tedapi, report_vitals=True) -> None:
        firmware = tedapi.get_firmware_version(details=True)
        logger.debug("firmware = %r", firmware)

        config = tedapi.get_config()
        logger.debug("config = %r", config)

        status = tedapi.get_status()
        logger.debug("status = %r", status)

        device_id = f"TeslaEnergySystem_{config['vin']}"
        super().__init__(name=config['site_info']['site_name'], device_id=device_id)

        self.tedapi = tedapi
        self.report_vitals = report_vitals
        self.serial = firmware['gateway']['serialNumber']
        self.part_number = firmware['gateway']['partNumber']
        self.firmware_version = firmware['version']['text']
        self.vin = config['vin']

        # Home Assistant sensors
        self.battery = entities.Battery(device_id, "Battery")
        self.battery_capacity = entities.EnergyStorage(device_id, "Battery Capacity")
        self.battery_power = entities.PowerValue(device_id, "Battery Power")
        self.battery_remaining = entities.EnergyStorage(device_id, "Battery Remaining")
        self.battery_reserve_hidden = entities.EnergyStorage(device_id,
                                        "Battery Hidden Reserve",
                                        'battery_reserve_hidden')
        self.battery_reserve_user = entities.Battery(device_id,
                                        "Battery Reserve",
                                        'battery_reserve_user')
        self.battery_time_remaining = entities.Duration(device_id, "Battery Time Remaining")
        self.calibration = entities.Running(device_id, "Calibration")
        self.commission_date = entities.Timestamp(device_id, "Commission Date")
        self.grid_power = entities.PowerValue(device_id, "Grid Power")
        self.grid_status = entities.Connectivity(device_id, "Grid Status")
        self.inverter_capacity = entities.PowerValue(device_id, "Inverter Capacity")
        self.load_power = entities.PowerValue(device_id, "Load Power")
        self.solar_power = entities.PowerValue(device_id, "Solar Power")

        # Home Assistant template sensors
        self.battery_power_in = entities.PowerTemplate(
            device_id,
            "Battery Power Charge",
            template = "[ value_json.battery_power | int, 0 ] | min | abs",
            enabled = False
            )
        self.battery_power_out = entities.PowerTemplate(
            device_id,
            "Battery Power Discharge",
            template = "[ value_json.battery_power | int, 0 ] | max",
            enabled = False)
        self.grid_power_in = entities.PowerTemplate(
            device_id,
            "Grid Power Import",
            template = "[ value_json.grid_power | int, 0 ] | max",
            enabled = False)
        self.grid_power_out = entities.PowerTemplate(
            device_id,
            "Grid Power Export",
            template = "[ value_json.grid_power | int, 0 ] | min | abs",
            enabled = False)

        self.powerwalls = {}
        for b in config['battery_blocks']:
            self.powerwalls[b['vin']] = PowerWall3(
                                            parent=device_id,
                                            vin=b['vin'],
                                            tedapi=tedapi)


    def _calc_battery(self) -> int:
        """
        Calculates the apparent battery level after accounting for the
        apparent "hidden" 5% reserve
        """
        return int(self.battery_remaining.get() * 100 / self.battery_capacity.get())


    def _calc_time_remaining(self) -> int:
        """Calculates the runtime remaining based on the apparently battery remaining"""
        return int(round(self.battery_remaining.get() * 3600 / self.load_power.get(), 0))


    def update(self) -> None:
        """Updates the name and values for all components using data from the PWs"""
        self.set_updated(False)

        firmware = self.tedapi.get_firmware_version(details=True)
        config = self.tedapi.get_config()
        status = self.tedapi.get_status()

        self.serial = firmware['gateway']['serialNumber']
        self.part_number = firmware['gateway']['partNumber']
        self.firmware_version = firmware['version']['text']

        # Map config
        site = config['site_info']
        self.set_name(site['site_name'])
        self.commission_date.set(site['battery_commission_date'])
        self.inverter_capacity.set(site['nominal_system_power_ac'] * 1000)
        self.battery_reserve_user.set(int(site['backup_reserve_percent'] * 100 / 105))

        # Map status
        self.grid_status.set("OFF")

        conn = status['esCan']['bus']['ISLANDER']['ISLAND_GridConnection']
        if conn['ISLAND_GridConnected'] == "ISLAND_GridConnected_Connected":
            self.grid_status.set("ON")

        self.calibration.set('OFF')
        if "BatteryCalibration" in status['control']['alerts']['active']:
            self.calibration.set('ON')

        full_pack = status['control']['systemStatus']['nominalFullPackEnergyWh']
        remaining = status['control']['systemStatus']['nominalEnergyRemainingWh']
        self.battery_reserve_hidden.set(int(full_pack / 20))
        self.battery_capacity.set(full_pack - self.battery_reserve_hidden.get())
        self.battery_remaining.set(remaining - self.battery_reserve_hidden.get())

        meter = status['control']['meterAggregates']
        self.grid_power.set(round(_get_power(meter, 'SITE'), 2))
        self.solar_power.set(round(_get_power(meter, 'SOLAR'), 2))
        self.battery_power.set(round(_get_power(meter, 'BATTERY'), 2))
        self.load_power.set(round(_get_power(meter, 'LOAD'), 2))

        self.battery.set(self._calc_battery())
        self.battery_time_remaining.set(self._calc_time_remaining())

        self.set_updated(True)
        if self.report_vitals:
            for item in self.powerwalls.values():
                try:
                    item.update()
                # Catch everything, as we don't want to bailout from here
                except Exception as e: # pylint: disable=W0718
                    logger.warning(
                        "Failed to update Powerwall %s, level metrics: %s",
                        item.vin,
                        e)


    def get_discovery(self, prefix: str, will_topic: str) -> dict:
        """Generates an MQTT discovery message to send to HA"""
        msg = super().get_discovery(prefix=prefix, will_topic=will_topic)
        msg['payload']['dev']['mf'] = 'Tesla'
        msg['payload']['dev']['mdl'] = 'Powerwall3'
        msg['payload']['dev']['mdl_id'] = self.part_number
        msg['payload']['dev']['sw'] = self.firmware_version
        msg['payload']['dev']['sn'] = self.serial
        return msg


    def get_discoveries(self, prefix: str, will_topic: str) -> list:
        """Generates MQTT discovery messages for all nested devices to send to HA"""
        msgs = []
        msgs.append(self.get_discovery(prefix=prefix, will_topic=will_topic))
        for item in self.powerwalls.values():
            msgs.append(item.get_discovery(prefix=prefix, will_topic=will_topic))
        return msgs


    def get_states(self, prefix: str) -> list:
        """Generates MQTT state messages for all nested devices to send to HA"""
        msgs = []
        msgs.append(self.get_state(prefix=prefix))
        if self.report_vitals:
            for item in self.powerwalls.values():
                msgs.append(item.get_state(prefix=prefix))
        return msgs
