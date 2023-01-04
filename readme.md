# Rpi Eink pressure display

This is firmware for a pressure and temperature display 
for use with the NOSAMS DOC extraction line.
It updates temperature, pressure and two pressure offsets periodically,
and sleeps between updates.

## Hardware

* Adafruit Feather RP2040
* Adafruit 2.9" Grayscale eInk / ePaper Display FeatherWing
* Adafruit DPS310 Precision Barometric Pressure / Altitude Sensor

## Installation

Install CircuitPython. Currently running on 7.3.0.
Copy `lib` directory to pico. Copy `code_press_temp.py` to `code.py` on pico.

`code_black_display.py` fills the display with a black rectangle
to troubleshoot a fading issue with the Eink display.