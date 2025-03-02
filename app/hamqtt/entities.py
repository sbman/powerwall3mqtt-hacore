"""Module providing classes that map to HA entities as defined for MQTT discovery"""

# All these classes are simple helper classes, so disabling the variable and parameter
# count linting.

# pylint: disable=R0902
# pylint: disable=R0903
# pylint: disable=R0913
# pylint: disable=R0917

class Entity:
    """Base class for Entities"""
    def __init__(self,
            id_prefix,
            name,
            platform,
            template = None,
            device_class = None,
            unit = None,
            state_class = None,
            enabled = True):
        self.prefix = id_prefix
        self.name = name
        self.platform = platform
        self.template = template
        self.device_class = device_class
        self.unit = unit
        self.state_class = state_class
        self.value = None
        self.enabled = enabled

    def get_discovery(self):
        """Function to get the dictionary structure of an MQTT discovery component"""
        unique_id = self.name.lower().replace(' ', '_')
        if self.prefix is not None:
            unique_id = self.prefix + '_' + unique_id
        msg = {}
        msg['p'] = self.platform
        msg['value_template'] = f"{{{{ {self.template} }}}}"
        msg['unique_id'] = unique_id
        msg['name'] = self.name
        if self.device_class is not None:
            msg['device_class'] = self.device_class
        if self.unit is not None:
            msg['unit_of_measurement'] = self.unit
        if self.state_class is not None:
            msg['state_class'] = self.state_class
        if not self.enabled:
            msg['en'] = "false"
        return msg


class ValueEntity(Entity):
    """An entity that can hold a value instead of just get data from a template"""
    def __init__(self,
            id_prefix,
            name,
            platform,
            template = None,
            device_class = None,
            unit = None,
            state_class = None,
            enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform=platform,
            template=template,
            device_class=device_class,
            unit=unit,
            state_class=state_class,
            enabled=enabled)
        if template is None:
            self.template = name.lower().replace(' ', '_')

    def get_discovery(self):
        """Function to get the dictionary structure of an MQTT discovery component"""
        msg = super().get_discovery()
        msg['value_template'] = f"{{{{ value_json.{self.template} }}}}"
        return msg

    def get(self):
        """Function to get the value of the entity"""
        return self.value

    def set(self, value):
        """Function to set the value of the entity"""
        if self.platform == "binary_sensor" and isinstance(value, bool):
            if value:
                self.value = "ON"
            else:
                self.value = "OFF"
        else:
            self.value = value



class Battery(ValueEntity):
    """Class that maps to a Battery entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="sensor",
            template=template,
            device_class="battery",
            unit="%",
            enabled=enabled)


class Connectivity(ValueEntity):
    """Class that maps to a Connectivity entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="binary_sensor",
            template=template,
            device_class="connectivity",
            enabled=enabled)


class Current(ValueEntity):
    """Class that maps to a Current entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="sensor",
            template=template,
            device_class="current",
            unit="A",
            enabled=enabled)


class Duration(ValueEntity):
    """Class that maps to a Duration entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="sensor",
            template=template,
            device_class="duration",
            unit="s",
            enabled=enabled)


class EnergyStorage(ValueEntity):
    """Class that maps to an Energy Storage entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="sensor",
            template=template,
            device_class="energy_storage",
            unit="Wh",
            enabled=enabled)


class PowerTemplate(Entity):
    """Class that maps to a Power entity using a template in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="sensor",
            template=template,
            device_class="power",
            unit="W",
            state_class='measurement',
            enabled=enabled)


class PowerValue(ValueEntity):
    """Class that maps to a Power entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="sensor",
            template=template,
            device_class="power",
            unit="W",
            state_class='measurement',
            enabled=enabled)


class Problem(ValueEntity):
    """Class that maps to a Problem entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="binary_sensor",
            template=template,
            device_class="problem",
            enabled=enabled)


class Running(ValueEntity):
    """Class that maps to a Running entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="binary_sensor",
            template=template,
            device_class="running",
            enabled=enabled)


class Timestamp(ValueEntity):
    """Class that maps to a Timestamp entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="sensor",
            template=template,
            device_class="timestamp",
            enabled=enabled)


class Voltage(ValueEntity):
    """Class that maps to a Voltage entity in HA"""
    def __init__(self, id_prefix, name, template = None, enabled = True):
        super().__init__(
            id_prefix=id_prefix,
            name=name,
            platform="sensor",
            template=template,
            device_class="voltage",
            unit="V",
            enabled=enabled)
