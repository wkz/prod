import inspect
import logging

TIMEOUT = 5

# pymodbus logs failures itself; keep them out of prod's one-line errors
logging.getLogger("pymodbus").addHandler(logging.NullHandler())

class ModbusRelay30CH(object):
    """Waveshare Modbus POE ETH Relay 30CH

    Each relay is a coil, addresses 0-29 for channels 1-30, spoken to
    with Modbus RTU over TCP, the device default."""

    CHANNELS = 30
    PORT = 4196

    def __init__(self, name, cfg):
        self.name, self.cfg = name, cfg

        if "host" not in cfg:
            raise ValueError(name + " does not specify a host")

        from pymodbus.client import ModbusTcpClient
        from pymodbus.exceptions import ModbusException
        self.ModbusException = ModbusException

        self.client = ModbusTcpClient(cfg["host"],
                                      port=int(cfg.get("port", self.PORT)),
                                      framer="rtu",
                                      timeout=float(cfg.get("timeout", TIMEOUT)))
        if not self.client.connect():
            raise ConnectionError(f"{name}: cannot connect to {cfg['host']}")

        # pymodbus 3.10 renamed the unit argument from slave to device_id
        unit = "device_id" if "device_id" in \
            inspect.signature(self.client.read_coils).parameters else "slave"
        self.unit = {unit: int(cfg.get("unit", 1))}
        self.cache = None

    def __transact(self, request, *args, **kwargs):
        try:
            rsp = request(*args, **kwargs, **self.unit)
        except self.ModbusException as e:
            raise ConnectionError(f"{self.name}: {e}") from None

        if rsp.isError():
            raise ConnectionError(f"{self.name}: {rsp}")
        return rsp

    def __all(self):
        if self.cache is None:
            rsp = self.__transact(self.client.read_coils, 0, count=self.CHANNELS)
            self.cache = rsp.bits[:self.CHANNELS]
        return self.cache

    def __coil(self, port):
        coil = int(port) - 1
        if not 0 <= coil < self.CHANNELS:
            raise ValueError(self.name + " has no channel " + str(port))
        return coil

    def __str__(self):
        return self.name

    def __getitem__(self, port):
        return self.get(port)

    def __setitem__(self, port, on):
        return self.set(port, on)

    def __iter__(self):
        return iter(self.cfg["ports"].keys())

    def get(self, port):
        return bool(self.__all()[self.__coil(port)])

    def set(self, port, on):
        coil = self.__coil(port)
        self.__transact(self.client.write_coil, coil, bool(on))
        if self.cache is not None:
            self.cache[coil] = bool(on)
