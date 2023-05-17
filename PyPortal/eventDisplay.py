# SPDX-FileCopyrightText: 2023 Richard Teel for TeelSys
#
# SPDX-License-Identifier: MIT

"""
Sets up the display layout and provides methods for 
updating various items on the display.
"""

import board
import displayio
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from geometryPointRect import pointXY
from geometryPointRect import rectangleTL_BR


# **************** CLASS ******************
class eventDisplay:
    # **************** CONSTANTS ******************
    IMG_FILE_DEFAULT_BACKGROUND = "background.bmp"
    IMG_FILE_DIM_ICON = "bright_decrease.bmp"
    IMG_FILE_BRIGHT_ICON = "bright_increase.bmp"
    IMG_FILE_CONNECT_FAILED_BACKGROUND = "connect_failed.bmp"
    IMG_FILE_CONNECTING_BACKGROUND = "connecting.bmp"
    IMG_FILE_NO_EVENTS_BACKGROUND = "no_events.bmp"
    IMG_FILE_NOT_FOUND = "not_found.bmp"
    IMG_FILE_TITLE_BACKGROUND = "title.bmp"
    IMG_FILE_WIFI_SPRITES = "wifi.bmp"

    def format_datetime(datetime, show24hourFormat):
        if show24hourFormat:
            return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
                datetime.tm_mon,
                datetime.tm_mday,
                datetime.tm_year,
                datetime.tm_hour,
                datetime.tm_min,
                datetime.tm_sec,
            )
        else:
            h = datetime.tm_hour
            amPm = "AM"
            if h >= 12:
                amPm = "PM"
            if h > 12:
                h = h - 12
            return "{:02}/{:02}/{} {:2}:{:02}:{:02} {}".format(
                datetime.tm_mon,
                datetime.tm_mday,
                datetime.tm_year,
                h,
                datetime.tm_min,
                datetime.tm_sec,
                amPm
            )

    def __init__(self, imgFolder="", eventImagesFolder=""):
        self.display = board.DISPLAY

        # **************** FONTS ******************
        self.fontStatus = bitmap_font.load_font(
            imgFolder + "/fonts/Helvetica-Bold-16.bdf")
        self.fontLarge = bitmap_font.load_font(
            imgFolder + "/fonts/MicrosoftSansSerif-36.bdf")
        self.fontMedium = bitmap_font.load_font(
            imgFolder + "/fonts/MicrosoftSansSerif-20.bdf")

        # pre-load glyphs for fast printing
        self.fontStatus.load_glyphs(
            b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-!,. "\'?!')
        # pre-load glyphs for fast printing
        self.fontLarge.load_glyphs(
            b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-!,. "\'?!')
        # pre-load glyphs for fast printing
        self.fontMedium.load_glyphs(
            b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-!,. "\'?!')

        self.imageFolderPath = imgFolder
        self.eventImageFolderPath = eventImagesFolder

        self.spritesWifi = None

        self.gpWindow = displayio.Group()       # Group to hold all groups
        self.gpBackground = displayio.Group()   # Group for the background image
        self.gpHeader = displayio.Group()       # Group for the header
        self.gpFooter = displayio.Group()       # Group for the footer
        # Group for the wifi signal stength sprite
        self.gpWifi = displayio.Group()
        self.gpButtonDim = displayio.Group()    # Group for the backlight dim icon
        # Group for the backlight increase icon
        self.gpButtonBright = displayio.Group()

        # Load the inital background
        self.changeBackground(self.IMG_FILE_TITLE_BACKGROUND, False)

        # Load the Header
        self._loadHeader()

        # Load the Footer
        self._loadFooter()

        # ------------- Title ------------- #
        self.title = Label(
            font=self.fontLarge,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
            anchored_position=(8, 136),
        )

        # ------------- Subtitle ------------- #
        self.subtitle = Label(
            font=self.fontMedium,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
            anchored_position=(8, 170),
        )

        countPosY = 192
        countPosDaysX = 50
        countPosHoursX = 150
        countPosMinsX = 260
        spaceX = 4

        # ------------- Count Labels ------------- #
        self.countlabelDays = Label(
            font=self.fontMedium,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
            anchored_position=(countPosDaysX + spaceX, countPosY),
        )
        self.countlabelHours = Label(
            font=self.fontMedium,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
            anchored_position=(countPosHoursX + spaceX, countPosY),
        )
        self.countlabelMinutes = Label(
            font=self.fontMedium,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
            anchored_position=(countPosMinsX + spaceX, countPosY),
        )

        # ------------- Counts ------------- #
        self.countDays = Label(
            font=self.fontLarge,
            text="",
            color=0xFFFFFF,
            background_color=None,
            anchor_point=(1.0, 0.0),
            anchored_position=(countPosDaysX, countPosY),
        )
        self.countHours = Label(
            font=self.fontLarge,
            text="",
            color=0xFFFFFF,
            background_color=None,
            anchor_point=(1.0, 0.0),
            anchored_position=(countPosHoursX, countPosY),
        )
        self.countMinutes = Label(
            font=self.fontLarge,
            text="",
            color=0xFFFFFF,
            background_color=None,
            anchor_point=(1.0, 0.0),
            anchored_position=(countPosMinsX, countPosY),
        )
        self.eventDayText = Label(
            font=self.fontLarge,
            text="",
            color=0xFFFFFF,
            background_color=None,
            anchor_point=(0.5, 0.0),
            anchored_position=(160, countPosY),
        )

        # ------------- GROUP - gpWindow ------------- #
        self.gpWindow.append(self.gpBackground)
        self.gpWindow.append(self.gpHeader)
        self.gpWindow.append(self.gpFooter)
        self.gpWindow.append(self.title)
        self.gpWindow.append(self.subtitle)
        self.gpWindow.append(self.countlabelDays)
        self.gpWindow.append(self.countlabelHours)
        self.gpWindow.append(self.countlabelMinutes)
        self.gpWindow.append(self.countDays)
        self.gpWindow.append(self.countHours)
        self.gpWindow.append(self.countMinutes)
        self.gpWindow.append(self.eventDayText)
        # Add the Group to the Display
        self.display.show(self.gpWindow)

        # ************** TOUCH AREAS **************
        self.touchTemperature = rectangleTL_BR(pointXY(0, 0), pointXY(40, 40))
        self.touchTime = rectangleTL_BR(pointXY(60, 0), pointXY(260, 40))
        self.touchEventPrevious = rectangleTL_BR(
            pointXY(0, 60), pointXY(150, 180))
        self.touchEventNext = rectangleTL_BR(
            pointXY(170, 60), pointXY(320, 180))
        self.touchBrightnessMinus = rectangleTL_BR(
            pointXY(0, 200), pointXY(40, 240))
        self.touchBrightnessAuto = rectangleTL_BR(
            pointXY(80, 200), pointXY(240, 240))
        self.touchBrightnessPlus = rectangleTL_BR(
            pointXY(280, 200), pointXY(320, 240))

    def clearAllText(self):
        self.title.text = ""
        self.subtitle.text = ""
        self.countDays.text = ""
        self.countlabelDays.text = ""
        self.countHours.text = ""
        self.countlabelHours.text = ""
        self.countMinutes.text = ""
        self.countlabelMinutes.text = ""
        self.eventDayText.text = ""

    def _loadWifiSprites(self):
        # ------------- GROUP - gpWifi ------------- #
        # Create a TileGrid to hold the bitmap
        # Load the sprite sheet (bitmap)
        (sprite_sheet, palette) = adafruit_imageload.load(self.imageFolderPath + "/" + self.IMG_FILE_WIFI_SPRITES,
                                                          bitmap=displayio.Bitmap, palette=displayio.Palette)
        # Create a sprite (tilegrid)
        self.spritesWifi = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                                              width=1,
                                              height=1,
                                              tile_width=20,
                                              tile_height=20)
        # Set sprite location
        self.gpWifi.x = 300
        self.gpWifi.y = 0

        return self.spritesWifi

    def _loadHeader(self):
        # ------------- GROUP - gpHeader ------------- #
        rectHead = Rect(0, 0, 320, 20, fill=0xffffff)
        self.gpHeader.append(rectHead)

        self.statusTemperature = Label(
            font=self.fontStatus,
            text="",
            color=0x000000,
            background_color=None,
            anchor_point=(0.0, 0.5),
            anchored_position=(2, 10),
        )

        self.statusDateTime = Label(
            font=self.fontStatus,
            text="No Time Info",
            color=0x000000,
            background_color=None,
            anchor_point=(0.5, 0.5),
            # anchored_position=(160, 10),
            anchored_position=(180, 10),
        )

        # Add the sprite to the Wi-Fi Group
        self.gpWifi.append(self._loadWifiSprites())

        self.gpHeader.append(self.statusTemperature)
        self.gpHeader.append(self.statusDateTime)
        self.gpHeader.append(self.gpWifi)

        return

    def _loadFooter(self):
        # ------------- GROUP - gpFooter ------------- #
        rectFoot = Rect(0, 220, 320, 20, fill=0xffffff)
        self.gpFooter.append(rectFoot)

        # ------------- GROUP - gpbacklightMinus ------------- #
        self.set_image(self.gpButtonDim, self.imageFolderPath +
                       "/" + self.IMG_FILE_DIM_ICON)
        self.gpButtonDim.x = 0
        self.gpButtonDim.y = 220

        # ------------- GROUP - gpbacklightPlus ------------- #
        self.set_image(self.gpButtonBright,
                       self.imageFolderPath + "/" + self.IMG_FILE_BRIGHT_ICON)
        self.gpButtonBright.x = 300
        self.gpButtonBright.y = 220

        # ------------- Event Count Label ------------- #
        self.statusEventCount = Label(
            font=self.fontStatus,
            text="No Events",
            color=0x000000,
            background_color=None,
            anchor_point=(0.5, 0.5),
            anchored_position=(160, 230),
        )

        # ------------- Brightness Label ------------- #
        self.statusBrightness = Label(
            font=self.fontStatus,
            text="Auto",
            color=0x000000,
            background_color=None,
            anchor_point=(0, 0.5),
            anchored_position=(24, 230),
        )

        self.gpFooter.append(self.gpButtonDim)
        self.gpFooter.append(self.gpButtonBright)
        self.gpFooter.append(self.statusEventCount)
        self.gpFooter.append(self.statusBrightness)

    # This function allows us to change the background image

    def changeBackground(self, filename, useEventImageLocation=True, filenameContainsPath=False):
        # ------------- GROUP - gpBackground ------------- #
        fullFileName = self.imageFolderPath + "/" + filename

        if useEventImageLocation:
            fullFileName = self.eventImageFolderPath + "/" + filename
        if filenameContainsPath:
            fullFileName = filename

        try:
            self.set_image(self.gpBackground, fullFileName)
        except Exception as e:
            print(f"ERROR: Failed to load the image {fullFileName}\r\n{e}")
            self.set_image(self.gpBackground,
                           self.imageFolderPath + "/" + self.IMG_FILE_NOT_FOUND)

        self.gpBackground.x = 0
        self.gpBackground.y = 0

        return

    # This will handle switching Images and Icons
    def set_image(self, group, filename):
        """Set the image file for a given goup for display.
        This is most useful for Icons or image slideshows.
            :param group: The chosen group
            :param filename: The filename of the chosen image
        """
        # print("Set image to ", filename)
        if group:
            group.pop()

        if not filename:
            return  # we're done, no icon desired

        # # CircuitPython 6 & 7 compatible
        # image_file = open(filename, "rb")
        # image = displayio.OnDiskBitmap(image_file)
        # image_sprite = displayio.TileGrid(
        #     image, pixel_shader=getattr(image, "pixel_shader", displayio.ColorConverter())
        # )

        # CircuitPython 7+ compatible
        image = displayio.OnDiskBitmap(filename)
        image_sprite = displayio.TileGrid(
            image, pixel_shader=image.pixel_shader)

        group.append(image_sprite)

        return
