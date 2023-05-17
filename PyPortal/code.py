# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This example will figure out the current local time using the internet, and
then draw out a countdown clock until an event occurs!
Once the event is happening, a new graphic is shown
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
from eventDisplay import eventDisplay


def adjustBacklight(val=-1.0):
    if (backlightAuto):
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

    if backlightAuto:
        eventWindow.statusBrightness.text = "Auto"
    else:
        eventWindow.statusBrightness.text = "{:3.0f} %".format(val * 100.0)

    return val


def adjustTouch(touchTuple):
    MIN_X = 20
    MIN_Y = 18
    MAX_X = 319
    MAX_Y = 230

    x = touchTuple[0] - MIN_X
    y = touchTuple[1] - MIN_Y
    x = x * screen_width/(MAX_X - MIN_X)
    y = y * screen_height/(MAX_Y - MIN_Y)

    if x < 0:
        x = 0
    elif x > screen_width:
        x = screen_width
    if y < 0:
        y = 0
    elif y > screen_height:
        y = screen_height

    return (x, y, touchTuple[2])


def getTime(lastRefreshedTime, secondsToUpdate):
    if pyportal is None:
        return None
    if (not lastRefreshedTime) or (time.monotonic() - lastRefreshedTime) > secondsToUpdate:
        eventWindow.statusDateTime.text = "Updating Time"
        try:
            print("INFO: Getting time from internet!")
            if (not lastRefreshedTime):
                eventWindow.changeBackground(
                    eventWindow.IMG_FILE_CONNECTING_BACKGROUND, False)

            start = time.time()
            pyportal.get_local_time()  # pyportal.get_local_time(false) non-blocking?
            print(f"INFO: Getting time took {time.time() - start} seconds.")
            lastRefreshedTime = time.monotonic()
            print("INFO: Success the time has been set.")
        except RuntimeError as e:
            print(f"WARN: Some error occured, retrying!\r\n{e}")
            if (not lastRefreshedTime):
                eventWindow.changeBackground(
                    eventWindow.IMG_FILE_CONNECT_FAILED_BACKGROUND, False)
        # Use try catch here as there is an error in adafruit_portalbase
        #   File "adafruit_portalbase/network.py", line 208, in get_strftime
        #   AttributeError: 'NoneType' object has no attribute 'get'
        except Exception as e:
            print(f"ERROR: Failed to getTime\r\n{e}")
            eventWindow.changeBackground(
                eventWindow.IMG_FILE_CONNECT_FAILED_BACKGROUND, False)

    removePastEvents()

    return lastRefreshedTime


def loadSdCard():
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

    if len(events) > 0:
        events.sort()


def networkQuality():
    if eventWindow is None:
        return

    retval = -1
    dBm = -100

    if pyportal.network._wifi.is_connected:
        dBm = pyportal.network._wifi.esp.rssi

        if dBm <= -90:
            retval = 0
        elif dBm >= -30:
            retval = 100
        else:
            retval = 2 * (dBm + 100)

    if eventWindow.spritesWifi:
        if dBm >= -30:
            eventWindow.spritesWifi[0] = 4
        elif dBm >= -55:
            eventWindow.spritesWifi[0] = 3
        elif dBm >= -70:
            eventWindow.spritesWifi[0] = 2
        elif dBm >= -90:
            eventWindow.spritesWifi[0] = 1
        else:
            eventWindow.spritesWifi[0] = 0

    return retval


def playTouchSound():
    try:
        pyportal.play_file(cwd + "/touch.wav", True)
    except Exception as e:
        print(f"ERROR: Failed to play touch sound\r\n{e}")

def removePastEvents():
    if len(events) == 0:
        return
    
    global event_index, last_event_index

    removeCount = 0
    currentEvent = events[event_index]

    for i, e in reversed(list(enumerate(events))):
        if e.remainingTime < -86400:
            print(f"INFO: Removing item {i}: {e}")
            events.pop(i)
            removeCount = removeCount + 1

    if removeCount > 0:
        # Does the array pointer point to the same object?
        if currentEvent != events[event_index]:
            for idx, item in enumerate(events):
                if item == currentEvent:
                    event_index = idx
                    break
            last_event_index = -1
        else:
            last_event_index = -1
    
    return removeCount

def updateTemperature(showFahrenheit):
    if (eventWindow is None) or (adt is None):
        return

    # read the temperature sensor
    # tempOffset = -10.5  # Added offset due to the heat from backlight
    tempOffset = -6.6
    temperature = adt.temperature + tempOffset
    tempText = "{0:5.1f}° C".format(temperature)
    # print("INFO: Temperature = " + tempText)

    if showFahrenheit:
        temperature = (temperature * 1.8) + 32
        tempText = "{0:5.1f}° F".format(temperature)
        # print("INFO: Temperature = " + tempText)

    eventWindow.statusTemperature.text = tempText


# Set root locations
cwd = ("/"+__file__).rsplit('/', 1)[0]
sdcardPath = "/sd"

# Variables for the Events
events = []
# Keep track of the current event being displayed
event_index = 0
last_event_index = -1

# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(status_neopixel=board.NEOPIXEL)

eventWindow = eventDisplay(cwd, sdcardPath)
eventWindow.clearAllText()

# Touchscreen setup
screen_width = 320
screen_height = 240
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

# ------------- Light Sensor Setup ------------- #
light_sensor = AnalogIn(board.LIGHT)
backlightAuto = True
backlightStepSize = 0.1
backlightVal = adjustBacklight()

# display the temperature
temperatureInF = True
updateTemperature(temperatureInF)

# Flag for time display in 24 hour format
timeFormat24 = True

# ------------------ Load Events from SD Card -------------------------
loadSdCard()

# ------------------ Get the time -------------------------
# Declare the variable to let us know when the time was last acquired
refresh_time = None
refresh_time = getTime(refresh_time, 3600)

timeLastSeconds = time.time()

while True:
    # Check for touch events
    touch = ts.touch_point

    if touch:
        touchAdj = adjustTouch(touch)
        touchHandled = False

        if eventWindow.touchTemperature.pointInside(touchAdj):
            temperatureInF = not temperatureInF
            touchHandled = True
        elif eventWindow.touchTime.pointInside(touchAdj):
            timeFormat24 = not timeFormat24
            touchHandled = True
        elif eventWindow.touchEventPrevious.pointInside(touchAdj):
            event_index = event_index - 1
            if event_index < 0:
                event_index = len(events) - 1
            touchHandled = True
        elif eventWindow.touchEventNext.pointInside(touchAdj):
            event_index = event_index + 1
            if event_index > len(events) - 1:
                event_index = 0
            touchHandled = True
        elif eventWindow.touchBrightnessMinus.pointInside(touchAdj):
            backlightAuto = False
            backlightVal = backlightVal - backlightStepSize
            touchHandled = True
        elif eventWindow.touchBrightnessAuto.pointInside(touchAdj):
            backlightAuto = True
            touchHandled = True
        elif eventWindow.touchBrightnessPlus.pointInside(touchAdj):
            backlightAuto = False
            backlightVal = backlightVal + backlightStepSize
            touchHandled = True

        if touchHandled:
            playTouchSound()
            # print(f"{touch} Adj -> {touchAdj}")
            time.sleep(0.5)

    # Check if the display is busy wait for it not being busy before continuing
    """
    if eventWindow.display.busy:
        print("Display is busy")
        continue
    """

    # Update the display once per second
    timeCurrentSeconds = time.time()
    if (timeCurrentSeconds - timeLastSeconds) < 1.0:
        continue

    timeLastSeconds = timeCurrentSeconds

    eventWindow.display.auto_refresh = False
    eventWindow.statusDateTime.text = eventDisplay.format_datetime(
        time.localtime(), timeFormat24)
    networkQuality()
    updateTemperature(temperatureInF)
    backlightVal = adjustBacklight(backlightVal)
    eventWindow.display.auto_refresh = True

    # only query the online time once per hour (and on first run)
    refresh_time = getTime(refresh_time, 3600)

    if (refresh_time is None):
        time.sleep(3)
        continue

    eventWindow.display.auto_refresh = False
    # Show the events with countdown
    if event_index != last_event_index:
        if len(events) == 0:
            eventWindow.changeBackground(
                eventWindow.IMG_FILE_NO_EVENTS_BACKGROUND, False)
            last_event_index = event_index
        else:
            # Remove the textx
            eventWindow.clearAllText()
            eventWindow.statusEventCount.text = f"{event_index + 1} of {len(events)}"
            eventWindow.changeBackground(events[event_index].imageCountDown)
            eventWindow.title.color = events[event_index].forecolor
            eventWindow.title.text = events[event_index].title
            eventWindow.subtitle.color = events[event_index].forecolor
            eventWindow.subtitle.text = events[event_index].subtitle
            events[event_index].remainingUpdate()

            if events[event_index].remainingTime > 0:
                eventWindow.countlabelDays.text = "Days"
                eventWindow.countlabelHours.text = "Hours"
                eventWindow.countlabelMinutes.text = "Mins."

            last_event_index = event_index

    if len(events) == 0:
        eventWindow.display.auto_refresh = True
        continue

    # Update the remaining time
    events[event_index].remainingUpdate()
    if events[event_index].remainingTime <= 0:
        eventWindow.countlabelDays.text = ""
        eventWindow.countlabelHours.text = ""
        eventWindow.countlabelMinutes.text = ""
        eventWindow.countDays.text = "Event Day!!!"
        eventWindow.countHours.text = ""
        eventWindow.countMinutes.text = ""

        eventWindow.display.auto_refresh = True
        continue

    eventWindow.countDays.text = f"{events[event_index].remainingDays}"
    eventWindow.countHours.text = f"{events[event_index].remainingHours}"
    eventWindow.countMinutes.text = f"{events[event_index].remainingMinutes}"
    eventWindow.display.auto_refresh = True
