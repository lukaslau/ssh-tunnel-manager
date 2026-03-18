.PHONY: all ui resources clean

all: ui resources

ui: tunnelconfig.py

resources: icons.py

tunnelconfig.py: tunnelconfig.ui
	pyside6-uic -g python $< -o $@

icons.py: icons.qrc
	pyside6-rcc -g python $< -o $@

clean:
	rm -f tunnelconfig.py icons.py
