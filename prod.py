#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import argcomplete, argparse
import os
import pyvisa
import sys
import time
import yaml

import nge100

HW = {
    "rs,nge100": nge100.NGE100
}

cfg = None

# Load config file if available
for cfgfile in ["~/.prod.yaml", "~/.config/prod.yaml", "/etc/prod.yaml"]:
    path = os.path.expanduser(cfgfile)
    if not os.path.exists(path):
        continue

    cfg = yaml.load(open(path), Loader=yaml.FullLoader)

    for top in ("devices", "aliases"):
        if top not in cfg:
            cfg[top] = []

    for dev in cfg["devices"]:
        if "ports" not in cfg["devices"][dev]:
            cfg["devices"][dev]["ports"] = []

    break

if not cfg:
    sys.exit("No configuration file found")

def show(dev, port):
    print("on" if dev[port] else "off")

def on(dev, port):
    dev[port] = True

def off(dev, port):
    dev[port] = False

def toggle(dev, port):
    dev[port] = not dev[port]

def cycle(dev, port):
    off(dev, port)
    time.sleep(1)
    on(dev, port)

def pulse(dev, port):
    on(dev, port)
    time.sleep(1)
    off(dev, port)

ops = {
    "show": show,
    "on": on,
    "off": off,
    "toggle": toggle,
    "cycle": cycle,
    "pulse": pulse,
}

def probe(devstr):
    if "compatible" not in cfg["devices"][devstr]:
        sys.exit(devstr + " does not specify any \"compatible\" attribute")

    compat = cfg["devices"][devstr]["compatible"]
    if compat not in HW:
        sys.exit("No driver for " + compat + " devices, required by " + devstr)

    try:
        dev = HW[compat](devstr, cfg["devices"][devstr])
    except:
        return None

    return dev

def showall(color):
    def paint(txt, code):
        if color:
            return "\x1b[" + code + "m" + txt + "\x1b[0m"
        else:
            return txt
    def invert(txt):
        return paint(txt, "7")
    def faint(txt):
        return paint(txt, "2")
    def green(txt):
        return paint(txt, "32")
    def red(txt):
        return paint(txt, "31")

    print(invert("%-30s  %-5s" % ("PORT", "STATE")))

    for devstr in cfg["devices"]:
        dev = probe(devstr)
        if not dev:
            continue

        print(faint(invert("%-37s" % str(dev))))

        for port in dev:
            names = port
            for (alias, target) in cfg["aliases"].items():
                if str(dev) + "/" + port == target:
                    names += " \"" + alias + "\""

            print("%-30s  %-5s" % (names, green("on") if dev[port] else red("off")))

def PortCompleter(**kwargs):
    ports = list(cfg["aliases"].keys())

    for dev in cfg["devices"]:
        for port in cfg["devices"][dev]["ports"]:
                ports.append(dev + "/" + port)

    return ports

class PortParser(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        port = values

        if not port:
            return

        if port in cfg["aliases"]:
            port = cfg["aliases"][port]

        if "/" not in port:
            raise argparse.ArgumentError(self, port + " is not a known alias")

        port = port.split("/")

        if port[0] not in cfg["devices"]:
            raise argparse.ArgumentError(self, port[0] + " is not a known device")
        if port[1] not in cfg["devices"][port[0]]["ports"]:
            raise argparse.ArgumentError(self, port[0] + " has no port named " + port[1])

        namespace.port = port

parser = argparse.ArgumentParser(prog="prod")
parser.add_argument("port", nargs="?", default=None, metavar="DEVICE/PORT|ALIAS",
                    action=PortParser, help="Output to operate on.").completer = PortCompleter
parser.add_argument("cmd", nargs="?", default=None, choices=list(ops.keys()),
                    help="Power cycle, enable, disable or toggle output pin.")
parser.add_argument("-C", dest="color", default=True, action="store_false",
                    help="Disable color in output.")

argcomplete.autocomplete(parser)
args = parser.parse_args()

if not args.port:
    showall(args.color)
    sys.exit()

dev = probe(args.port[0])
if not dev:
    sys.exit("Unable to connect to " % args.port[0])

if not args.cmd:
    args.cmd = "show"

if args.cmd not in ops:
    sys.exit(args.cmd + " is not a known operation")

ops[args.cmd](dev, args.port[1])
