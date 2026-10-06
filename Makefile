# Install prod as a Python package, and its bash completion

PYTHON  ?= python3
COMPDIR ?= /usr/local/share/bash-completion/completions

all:
	@echo "Run 'sudo make install', or 'sudo make uninstall' to remove prod."

# --root keeps pip out of the system packages, PEP 668
install:
	$(PYTHON) -m pip install --root $(DESTDIR)/ --no-deps --no-build-isolation \
		--no-warn-script-location .
	rm -rf build *.egg-info
	install -Dm0644 prod.bash $(DESTDIR)$(COMPDIR)/prod

uninstall:
	$(PYTHON) -m pip uninstall -y --break-system-packages prod
	rm -f $(DESTDIR)$(COMPDIR)/prod

.PHONY: all install uninstall
