# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This example will figure out the current local time using the internet, and
then draw out a countdown clock until an event occurs!
Once the event is happening, a new graphic is shown

import os
import synthio
import digitalio
import audiocore
import audioio
import array
"""
import math
import time
import board
import busio
import json
import adafruit_adt7410
import adafruit_touchscreen
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from analogio import AnalogIn
from event import event
from secrets import secrets

# Set root locations
cwd = ("/"+__file__).rsplit('/', 1)[0]
imagePathRoot = cwd

# Default Images for Backgrounds
imgConnecting = "connecting.bmp"
imgFailedToConnect = "failedtoconnect.bmp"
imgNoEvents = "noevents.bmp"
imgNotFound = "notfound.bmp"
imgTitle = "title.bmp"

# Other Variables
events = []
# flag to indicate if we should attempt to auto dim the display
autoDimBacklight = True


def adjustBacklight(val=-1.0):
    if (val < 0):
        if not autoDimBacklight:
            return

        # startAutoDimAt = 32768
        minAutoBrightness = 0.01
        MAXIMUM_LUX_BREAKPOINT = 1254.0

        # val = light_sensor.value/startAutoDimAt + minAutoBrightness
        lightReading = light_sensor.value
        lightLuxApprox = (lightReading/65536)*2000
        val = 1.0
        # https://www.analog.com/en/design-notes/a-simple-implementation-of-lcd-brightness-control-using-the-max44009-ambientlight-sensor.html
        if lightLuxApprox < MAXIMUM_LUX_BREAKPOINT:
            val = (9.9323*math.log(lightLuxApprox) + 27.059)/100.0
            # print(f"lightReading = {lightReading} & lightLuxApprox = {lightLuxApprox} & val = {val}")
        # Make certain that the screen is still lit by maintaining min value
        if val < minAutoBrightness:
            val = minAutoBrightness

    # https://learn.adafruit.com/making-a-pyportal-user-interface-displayio/display
    val = max(0, min(1.0, val))
    # board.DISPLAY.auto_brightness = False
    board.DISPLAY.brightness = val


def getTime(lastRefreshedTime, secondsToUpdate):
    if pyportal is None:
        return None
    if (not lastRefreshedTime) or (time.monotonic() - lastRefreshedTime) > secondsToUpdate:
        try:
            print("INFO: Getting time from internet!")
            if (not lastRefreshedTime):
                loadImage(imgConnecting, True)

            start = time.time()
            pyportal.get_local_time()  # pyportal.get_local_time(false) non-blocking?
            print(f"INFO: Getting time took {time.time() - start} seconds.")
            lastRefreshedTime = time.monotonic()
        except RuntimeError as e:
            print(f"WARN: Some error occured, retrying!\r\n{e}")
            if (not lastRefreshedTime):
                loadImage(imgFailedToConnect, True)
        # Use try catch here as there is an error in adafruit_portalbase
        #   File "adafruit_portalbase/network.py", line 208, in get_strftime
        #   AttributeError: 'NoneType' object has no attribute 'get'
        except Exception as e:
            print(f"ERROR: Failed to getTime\r\n{e}")

    return lastRefreshedTime


def loadImage(fileName, useCwd=False):
    try:
        if (useCwd):
            pyportal.set_background(cwd + "/" + fileName)
        else:
            pyportal.set_background(imagePathRoot + "/" + fileName)
    except Exception as e:
        print(f"ERROR: Did not find image {fileName}\r\n{e}")
        pyportal.set_background(cwd + "/" + imgNotFound)


def playTouchSound():
    try:
        pyportal.play_file(cwd + "/touch.wav", True)
    except Exception as e:
        print(f"ERROR: Failed to play touch sound\r\n{e}")


# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(status_neopixel=board.NEOPIXEL,
                    default_bg=imgTitle)

# ------------- Light Sensor Setup ------------- #
light_sensor = AnalogIn(board.LIGHT)
adjustBacklight()

# Fonts
big_font = bitmap_font.load_font(cwd+"/fonts/Helvetica-Bold-36.bdf")
title_font = bitmap_font.load_font(cwd+"/fonts/Arial-36.bdf")
subtitle_font = bitmap_font.load_font(cwd+"/fonts/Arial-20.bdf")

# speed up projects with lots of text by preloading the fonts!
big_font.load_glyphs(b'0123456789')  # pre-load glyphs for fast printing
# pre-load glyphs for fast printing
title_font.load_glyphs(
    b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-!,. "\'?!')
# pre-load glyphs for fast printing
subtitle_font.load_glyphs(
    b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-!,. "\'?!')

# Fonts and locations of text areas
text_color = 0xFFFFFF
days_position = (big_font, 8, 207)
hours_position = (big_font, 110, 207)
minutes_position = (big_font, 220, 207)
title_position = (title_font, 8, 140)
subtitle_position = (subtitle_font, 8, 175)

# Setup the Text Areas
text_areas = []
for pos in (days_position, hours_position, minutes_position, title_position, subtitle_position):
    textarea = Label(pos[0])
    textarea.x = pos[1]
    textarea.y = pos[2]
    textarea.color = text_color
    pyportal.splash.append(textarea)
    text_areas.append(textarea)

# Declare the variable to let us know when the time was last acquired
refresh_time = None

# Touchscreen setup
screen_width = 240
screen_height = 320
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=(
                                          (5200, 59000), (5800, 57000)),
                                      size=(screen_width, screen_height))

# ------------- Inputs and Outputs Setup ------------- #
try:
    # attempt to init. the temperature sensor
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
    adt.high_resolution = True
except ValueError:
    # Did not find ADT7410. Probably running on Titano or Pynt
    adt = None


# Keep track of the current event being displayed
event_index = 0
last_event_index = -1

# load events from SD Card
# Attempt to load config.json from SD Card
try:
    with open("/sd/config.json", "r") as fp:
        x = fp.read()
        # parse x:
        y = json.loads(x)
        secrets["ssid"] = y["secrets"]["ssid"]
        secrets["password"] = y["secrets"]["password"]
        secrets["timezone"] = y["secrets"]["timezone"]
        secrets["aio_username"] = y["secrets"]["aio_username"]
        secrets["aio_key"] = y["secrets"]["aio_key"]

        imagePathRoot = "/sd"

        events.clear()

        for i in range(len(y["events"])):
            # title, subtitle, year, month, day, hour, minute, imageCountDown, imageEventDay, forecolor=0xF0C810):
            events.append(event(y["events"][i]["title"],
                                y["events"][i]["subtitle"],
                                int(y["events"][i]["year"]),
                                int(y["events"][i]["month"]),
                                int(y["events"][i]["day"]),
                                int(y["events"][i]["hour"]),
                                int(y["events"][i]["minute"]),
                                y["events"][i]["imageCountDown"],
                                y["events"][i]["imageEventDay"],
                                int(y["events"][i]["forecolor"])))

except OSError as e:
    print(f"ERROR: Could not read text file.\r\n{e}")


while True:
    touch = ts.touch_point
    # light = light_sensor.value
    adjustBacklight()

    if touch:
        # print(f"INFO: Touched x={ts.touch_point[0]}, y={ts.touch_point[1]}")
        if touch[0] < 150:
            playTouchSound()
            event_index = event_index - 1
            if event_index < 0:
                event_index = len(events) - 1
        elif touch[0] > 170:
            playTouchSound()
            event_index = event_index + 1
            if event_index > len(events) - 1:
                event_index = 0

    # only query the online time once per hour (and on first run)
    refresh_time = getTime(refresh_time, 3600)
    if (refresh_time is None):
        continue

    now = time.localtime()

    # Show the events with countdown
    if event_index != last_event_index:
        if len(events) == 0:
            loadImage(imgNoEvents, True)
            last_event_index = event_index
        else:
            # Remove the text
            for ta in text_areas:
                ta.text = ""
            loadImage(events[event_index].imageCountDown)
            text_areas[3].color = events[event_index].forecolor
            text_areas[3].text = events[event_index].title
            text_areas[4].color = events[event_index].forecolor
            text_areas[4].text = events[event_index].subtitle
            last_event_index = event_index

    if len(events) == 0:
        continue

    remaining = time.mktime(events[event_index].date) - time.mktime(now)
    # remaining = -1
    if remaining < 0:
        # oh, its event time!
        loadImage(events[event_index].imageEventDay)
        continue

    secs_remaining = remaining % 60
    remaining //= 60
    mins_remaining = remaining % 60
    remaining //= 60
    hours_remaining = remaining % 24
    remaining //= 24
    days_remaining = remaining

    text_areas[0].text = '{:>2}'.format(days_remaining)  # set days textarea
    text_areas[1].text = '{:>2}'.format(hours_remaining)  # set hours textarea
    text_areas[2].text = '{:>2}'.format(mins_remaining)  # set minutes textarea
