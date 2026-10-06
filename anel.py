import urllib.request

class NetCtrl(object):
    def __init__(self, name, cfg):
        self.name, self.cfg = name, cfg

        if "url" not in cfg:
            raise ValueError(name + " does not specify a URL")

        if "auth" not in cfg:
            cfg["auth"] = "adminanel"

        self.cache = None

    def __fetch(self, op):
        url = self.cfg["url"] + "?" + op + self.cfg["auth"]
        req = urllib.request.urlopen(url)
        return req.read().decode()

    def __all(self):
        if self.cache != None:
            return self.cache
        
        # A header of device info, then "<br>" and "<name>;<state>;<lock>"
        # for each relay, in order
        relays = self.__fetch("Stat-").split("<br>")[1].split(";")
        bits = 0

        for bit, state in enumerate(relays[1::3]):
            if state == "1":
                bits |= 1 << bit

        self.cache = bits
        return bits

    def __str__ (self):
        return self.name

    def __getitem__(self, port):
        return self.get (port)

    def __setitem__(self, port, on):
        return self.set(port, on)

    def __iter__(self):
        return iter(self.cfg["ports"].keys())

    def get(self, port):
        port = int(port) - 1
        return bool((1 << port) & self.__all())

    def set(self, port, on):
        port = int(port) - 1
        bits = self.__all()

        if on:
            bits |= (1 << port)
        else:
            bits &= ~(1 << port)

        self.__fetch(f"Sw-0x{bits:02x},")
        self.cache = bits

