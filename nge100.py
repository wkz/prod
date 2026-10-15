class NGE100(object):
    def __init__(self, name, cfg):
        self.name, self.cfg = name, cfg

        if "resource" not in cfg:
            raise ValueError(name + " does not specify any resource")

        import pyvisa

        try:
            rm = pyvisa.ResourceManager()
            self.visa = rm.open_resource(cfg["resource"])
        except pyvisa.Error as e:
            raise ConnectionError(f"{name}: {e}") from None

        for port in cfg["ports"]:
            self.setup_port(port)

    def __str__ (self):
        return self.name

    def __cmd(self, cmd, query=False):
        import pyvisa

        try:
            if query:
                return self.visa.query(cmd)
            self.visa.write(cmd)
        except pyvisa.Error as e:
            raise ConnectionError(f"{self.name}: {e}") from None

    def setup_port(self, port):
        pcfg = self.cfg["ports"][port]

        if "voltage" not in pcfg:
            raise ValueError(self.name + "/" + port + " does not specify the output voltage")

        if "current" not in pcfg:
            raise ValueError(self.name + "/" + port + " does not specify the output current limit")

        self.__cmd("INST " + port)
        self.__cmd("Volt " + str(pcfg["voltage"]))
        self.__cmd("Curr " + str(pcfg["current"]))

    def __getitem__(self, port):
        return self.get (port)

    def __setitem__(self, port, on):
        return self.set(port, on)

    def __iter__(self):
        return iter(self.cfg["ports"].keys())

    def get(self, port):
        self.__cmd("INST " + port)
        return bool(int(self.__cmd("OUTP?", query=True)))

    def set(self, port, on):
        self.__cmd("INST " + port)
        self.__cmd("OUTP " + ("ON" if on else "OFF"))

