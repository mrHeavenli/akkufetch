import dbus

from config import Config


class Battery:
    def __init__(self, path: str, config: Config):
        battery_bus = dbus.SystemBus().get_object("org.freedesktop.UPower", path)
        self.interface = dbus.Interface(battery_bus, "org.freedesktop.DBus.Properties")

        self.config = config

    def __getitem__(self, item) -> str or None:
        value = self.interface.Get("org.freedesktop.UPower.Device", item)
        if type(value) == dbus.Double:
            value = round(value, self.config["system_info.float_precision"])
            if int(value) == value: value = int(value)

        return value
