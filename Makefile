.PHONY: all ui resources clean

all: ui resources

ui: tunnel.py tunnelconfig.py

resources: icons.py

tunnel.py: tunnel.ui
	pyside6-uic $< -o $@

tunnelconfig.py: tunnelconfig.ui
	pyside6-uic $< -o $@

icons.py: icons.qrc
	pyside6-rcc $< -o $@

clean:
	rm -f tunnel.py tunnelconfig.py icons.py
