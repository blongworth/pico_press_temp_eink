# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
Code for E-paper display of pressures in Torr
for NOSAMS DOC line.
"""

"""
Configure the sensor for continuous measurement with rates,
sampling counts and mode optimized for low power, as recommended
in Infineon's datasheet:
https://www.infineon.com/dgdl/Infineon-DPS310-DS-v01_00-EN.pdf
"""

# (disable pylint warnings for adafruit_dps310.{SampleCount,Rate,Mode}.*
# as they are generated dynamically)
# pylint: disable=no-member

import time
import alarm
import board
import busio
import displayio
import terminalio
import adafruit_il0373
from adafruit_dps310 import advanced
from adafruit_display_text import label

# Time between refreshes. No less than 180s
sleep_time = 360

# Setup DPS310
i2c = board.I2C()  # uses board.SCL and board.SDA
dps310 = advanced.DPS310_Advanced(i2c)
dps310.reset()
dps310.pressure_oversample_count = advanced.SampleCount.COUNT_2
dps310.pressure_rate = advanced.Rate.RATE_1_HZ
dps310.temperature_oversample_count = advanced.SampleCount.COUNT_16
dps310.temperature_rate = advanced.Rate.RATE_1_HZ
dps310.mode = advanced.Mode.CONT_PRESTEMP
dps310.wait_temperature_ready()
dps310.wait_pressure_ready()

# Setup display
displayio.release_displays()
spi = busio.SPI(board.SCK, board.MOSI)  # Uses SCK and MOSI
epd_cs = board.D9
epd_dc = board.D10

display_bus = displayio.FourWire(
    spi, command=epd_dc, chip_select=epd_cs, baudrate=1000000
)

time.sleep(1)

# Set text, font, size, and color
WIDTH = 296
HEIGHT = 128
font = terminalio.FONT
BLACK = 0x000000
WHITE = 0xFFFFFF
FOREGROUND_COLOR = BLACK
BACKGROUND_COLOR = WHITE

display = adafruit_il0373.IL0373(
    display_bus,
    width=WIDTH,
    height=HEIGHT,
    rotation=270,
    black_bits_inverted=False,
    color_bits_inverted=False,
    grayscale=True,
    refresh_time=1,
)

g = displayio.Group()

# Set a white background
background_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
# Map colors in a palette
palette = displayio.Palette(1)
palette[0] = BACKGROUND_COLOR

# Create a Tilegrid with the background and put in the displayio group
t = displayio.TileGrid(background_bitmap, pixel_shader=palette)
g.append(t)

# Draw simple text using the built-in font into a displayio group
text_group = displayio.Group(scale=2, x=10, y=10)
temp = "Temperature = %.1f *C" % (dps310.temperature - 1)
torr = dps310.pressure * 0.750062 # Convert hPa to Torr
press = "Pressure = %.0f Torr" % torr
pm20 = torr - 20
pp9 = torr + 9
tm20 = "P - 20 = %.0f Torr" % pm20
tp9 = "P + 9 = %.0f Torr" % pp9
text = temp + "\n" + press + "\n" + tm20 + "\n" + tp9
text_area = label.Label(terminalio.FONT, text=text, color=FOREGROUND_COLOR)
text_group.append(text_area)  # Add this text to the text group
g.append(text_group)

# Place the display group on the screen
display.show(g)

# Refresh the display to have everything show on the display
# NOTE: Do not refresh eInk displays more often than 180 seconds!
display.refresh()

# Create an alarm trigger for deep sleep
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + sleep_time)
# Exit the program, and then deep sleep until the alarm wakes us.
alarm.exit_and_deep_sleep_until_alarms(time_alarm)
