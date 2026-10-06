# prod

Switch power to lab equipment from the command line.  Supported hardware:

 - ANEL NET-CONTROL / NET-PwrCtrl, network controlled relays
 - Rohde & Schwarz NGE100 series power supplies, over VISA

```
$ prod
PORT                            STATE
ac
1 "tact1"                       on
...
$ prod tact1 cycle
```

Usage is `prod [DEVICE/PORT|ALIAS] [show|on|off|toggle|cycle|pulse]`.
Without arguments, prod lists all ports and their state.  Without an
operation, it shows the state of the given port.  `cycle` switches off,
waits one second and switches on again, `pulse` does the opposite.


## Configuration

prod reads the first of `~/.prod.yaml`, `~/.config/prod.yaml` and
`/etc/prod.yaml`:

```yaml
devices:
  ac:
    compatible: anel,net-control
    url: http://192.168.0.244
    auth: adminanel             # user and password, the default
    ports:
      1:
      2:

  psu:
    compatible: rs,nge100
    resource: TCPIP::192.168.0.10::INSTR
    ports:
      1:
        voltage: 12
        current: 2

aliases:
  tact1: ac/1
  tact2: ac/2
```


## Dependencies

On Debian and Ubuntu:

    sudo apt install python3-argcomplete python3-yaml

The NGE100 also needs `python3-pyvisa` and a VISA backend, such as
`python3-pyvisa-py`.  Installing with `make` needs `python3-pip` and
`python3-setuptools`.


## Installing

    sudo make install

This installs prod with pip under `/usr/local`, and its bash completion
in `/usr/local/share/bash-completion/completions`.  The completion is
active in new shells.  Remove it all with `sudo make uninstall`.

To install in a virtual environment of its own instead, with the Python
dependencies from PyPI as listed in `pyproject.toml`:

    pipx install .              # or '.[nge100]' for the NGE100
    cp prod.bash ~/.local/share/bash-completion/completions/prod
