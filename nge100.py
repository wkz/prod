import pyvisa

class NGE100(object):
    def __init__(self, name, cfg):
        self.name, self.cfg = name, cfg

        if "resource" not in cfg:
            raise ValueError(name + " does not specify any resource")

        rm = pyvisa.ResourceManager()
        self.visa = rm.open_resource(cfg["resource"])

        for port in cfg["ports"]:
            self.setup_port(port)

    def __str__ (self):
        return self.name

    def setup_port(self, port):
        pcfg = self.cfg["ports"][port]

        if "voltage" not in pcfg:
            raise ValueError(self.name + "/" + port + " does not specify the output voltage")

        if "current" not in pcfg:
            raise ValueError(self.name + "/" + port + " does not specify the output current limit")

        self.visa.write("INST " + port)
        self.visa.write("Volt " + str(pcfg["voltage"]))
        self.visa.write("Curr " + str(pcfg["current"]))

    def __getitem__(self, port):
        return self.get (port)

    def __setitem__(self, port, on):
        return self.set(port, on)

    def __iter__(self):
        return iter(self.cfg["ports"].keys())

    def get(self, port):
        self.visa.write("INST " + port)
        return True if int(self.visa.query("OUTP?")) else False

    def set(self, port, on):
        self.visa.write("INST " + port)
        self.visa.write("OUTP " + ("ON" if on else "OFF"))

