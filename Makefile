# Install prod as a Python package

PYTHON  ?= python3

all:
	@echo "Run 'sudo make install', or 'sudo make uninstall' to remove prod."

# --root keeps pip out of the system packages, PEP 668
install:
	$(PYTHON) -m pip install --root $(DESTDIR)/ --no-deps --no-build-isolation \
		--no-warn-script-location .
	rm -rf build *.egg-info

uninstall:
	$(PYTHON) -m pip uninstall -y --break-system-packages prod

.PHONY: all install uninstall
