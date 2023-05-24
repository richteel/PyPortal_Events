# SPDX-FileCopyrightText: 2023 Richard Teel for TeelSys
#
# SPDX-License-Identifier: MIT

"""
Sets up the display layout and provides methods for 
updating various items on the display.
"""

import board
import displayio
import vectorio
import adafruit_imageload
import gc
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label


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
    DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    MONTHNAME = ["Jan", "Feb", "Mar", "Apr", "May",
                 "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # **************** STATIC METHODS ******************
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
            return "{} {:2}/{:2}/{} {:2}:{:02} {}".format(
                eventDisplay.DOW[datetime.tm_wday],
                datetime.tm_mon,
                datetime.tm_mday,
                datetime.tm_year,
                h,
                datetime.tm_min,
                amPm
            )

    def pointInside(rect, pt):
        if (pt[0] > rect.x and pt[0] < (rect.x + rect.width) and pt[1] > rect.y and pt[1] < (rect.y + rect.height)):
            # print(f"Point {pt} is in rectangle [({self.topLeftPoint.x}, {self.topLeftPoint.y}), ({self.bottomRightPoint.x}, {self.bottomRightPoint.y})]")
            return True
        else:
            return False

    # **************** CLASS INITIALIZATION ******************
    def __init__(self, imgFolder="", eventImagesFolder="", screen_width=320, screen_height=240):
        self.display = board.DISPLAY
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.statusBarHeight = 20
        self.statusBackcolor = 0xffffff
        self.textBackcolor = 0x1888a8

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

        # ########### Create Screen Objects ###########
        # ------------- 1. Temperature ------------- #
        self.statusTemperature = Label(
            font=self.fontStatus,
            text="",
            color=0x000000,
            background_color=None,
            anchor_point=(0.0, 0.5),
        )
        # ------------- 2. Date & Time ------------- #
        self.statusDateTime = Label(
            font=self.fontStatus,
            text="No Time Info",
            color=0x000000,
            background_color=None,
            anchor_point=(0.5, 0.5),
        )
        # ------------- 3. Wi-Fi Sprites ------------- #
        self.spritesWifi = None
        # Group for the wifi signal stength sprite
        self.gpWifi = displayio.Group()
        # Add the sprite to the Wi-Fi Group
        self.gpWifi.append(self._loadWifiSprites())
        # ------------- 4. Title ------------- #
        self.title = Label(
            font=self.fontLarge,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
        )
        # ------------- 5. Subtitle ------------- #
        self.subtitle = Label(
            font=self.fontMedium,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
        )
        # ************* Count Labels ************* #
        # ------------- 6 & 7. Count Days ------------- #
        self.countDays = Label(
            font=self.fontLarge,
            text="",
            color=0xFFFFFF,
            background_color=None,
            anchor_point=(1.0, 0.0),
        )
        self.countlabelDays = Label(
            font=self.fontMedium,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
        )
        # ------------- 8 & 9. Count Hours ------------- #
        self.countHours = Label(
            font=self.fontLarge,
            text="",
            color=0xFFFFFF,
            background_color=None,
            anchor_point=(1.0, 0.0),
        )
        self.countlabelHours = Label(
            font=self.fontMedium,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
        )
        # ------------- 10 & 11. Count Minutes ------------- #
        self.countMinutes = Label(
            font=self.fontLarge,
            text="",
            color=0xFFFFFF,
            background_color=None,
            anchor_point=(1.0, 0.0),
        )
        self.countlabelMinutes = Label(
            font=self.fontMedium,
            text="",
            color=0xF0C810,
            background_color=None,
            anchor_point=(0.0, 0.0),
        )
        # ------------- 12. Dim Icon ------------- #
        self.gpButtonDim = displayio.Group()    # Group for the backlight dim icon
        # ------------- 13. Brightness Level ------------- #
        self.statusBrightness = Label(
            font=self.fontStatus,
            text="Auto",
            color=0x000000,
            background_color=None,
            anchor_point=(0, 0.5),
            anchored_position=(24, 230),
        )
        # ------------- 14. Event Count ------------- #
        self.statusEventCount = Label(
            font=self.fontStatus,
            text="No Events",
            color=0x000000,
            background_color=None,
            anchor_point=(0.5, 0.5),
        )
        # ------------- 15. Bright Icon ------------- #
        self.gpButtonBright = displayio.Group()
        # ------------- 16. Event Day Text ------------- #
        self.eventDayText = Label(
            font=self.fontLarge,
            text="",
            color=0xFFFFFF,
            background_color=None,
            anchor_point=(0.5, 0.0),
        )
        # ------------- 17. Text Background ------------- #
        self.textBackcolorPallet = displayio.Palette(1)
        self.textBackcolorPallet[0] = self.textBackcolor
        self.textBackground = vectorio.Rectangle(pixel_shader=self.textBackcolorPallet, width=self.screen_width, height=1)

        self.gpWindow = displayio.Group()       # Group to hold all groups
        self.gpBackground = displayio.Group()   # Group for the background image
        self.gpHeader = displayio.Group()       # Group for the header
        self.gpFooter = displayio.Group()       # Group for the footer

        # Load the inital background
        self.changeBackground(self.IMG_FILE_TITLE_BACKGROUND, False)

    def removeGroup(self, grp):
        for i, e in reversed(list(enumerate(grp))):
            grp.pop(i)
        gc.collect()

    def layoutScreen(self):
        self.removeGroup(self.gpFooter)
        self.removeGroup(self.gpHeader)
        self.removeGroup(self.gpBackground)
        self.removeGroup(self.gpWindow)

        # for i, e in reversed(list(enumerate(self.display))):
        # self.display.pop()

        # Load the Header
        self._loadHeader()

        # Load the Footer
        self._loadFooter()

        # Position Labels
        fontHeightMedium = 20
        fontHeightLarge = 36
        spaceY = 0
        spaceX = 4
        posCountY = self.screen_height - (self.statusBarHeight + spaceY + fontHeightLarge) # - 48
        posSubTitleY = posCountY - spaceY - fontHeightMedium
        posTitleY = posSubTitleY - spaceY - fontHeightLarge
        countPosDaysX = 65
        countPosHoursX = 160
        countPosMinsX = 260
        self.title.anchored_position=(8, posTitleY)
        self.subtitle.anchored_position=(8, posSubTitleY)
        self.eventDayText.anchored_position=(self.screen_width/2, posCountY)
        self.countDays.anchored_position=(countPosDaysX, posCountY)
        self.countlabelDays.anchored_position=(countPosDaysX + spaceX, posCountY)
        self.countHours.anchored_position=(countPosHoursX, posCountY)
        self.countlabelHours.anchored_position=(countPosHoursX + spaceX, posCountY)
        self.countMinutes.anchored_position=(countPosMinsX, posCountY)
        self.countlabelMinutes.anchored_position=(countPosMinsX + spaceX, posCountY)
        
        # Size and position text background
        self.textBackground.width = self.screen_width
        self.textBackground.height = (self.screen_height - posTitleY - spaceY - self.statusBarHeight) + 4
        self.textBackground.x = 0
        self.textBackground.y = (posTitleY - spaceY) - 4
        self.textBackground.hidden = True
        

        # ------------- GROUP - gpWindow ------------- #
        self.gpWindow.append(self.gpBackground)
        self.gpWindow.append(self.gpHeader)
        self.gpWindow.append(self.gpFooter)
        self.gpWindow.append(self.textBackground)
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
        self.display.root_group = self.gpWindow

        # ------------- TOUCH AREAS ------------- #
        statusSqButtonWH = 40
        statusTouchSpace = 20
        statusSqButtonAndSpace = statusSqButtonWH + statusTouchSpace
        self.touchTemperature = Rect(0, 0, statusSqButtonWH, statusSqButtonWH)
        self.touchTime = Rect(statusSqButtonAndSpace, 0, self.screen_width - (2 * statusSqButtonAndSpace), statusSqButtonWH)
        self.touchEventPrevious = Rect(0, statusSqButtonAndSpace, (2 * statusSqButtonAndSpace), self.screen_height - (2 * statusSqButtonAndSpace))
        self.touchEventNext = Rect(self.screen_width- (2 * statusSqButtonAndSpace), statusSqButtonAndSpace, (2 * statusSqButtonAndSpace), self.screen_height - (2 * statusSqButtonAndSpace))
        self.touchBrightnessMinus = Rect(0, self.screen_height - statusSqButtonWH, statusSqButtonWH, statusSqButtonWH)
        self.touchBrightnessAuto = Rect(statusSqButtonAndSpace, self.screen_height - statusSqButtonWH, self.screen_width - (2 * statusSqButtonAndSpace), statusSqButtonWH)
        self.touchBrightnessPlus = Rect(self.screen_width - statusSqButtonWH, self.screen_height - statusSqButtonWH, statusSqButtonWH, statusSqButtonWH)

        gc.collect()


    # **************** INTERNAL METHODS ******************
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

        return self.spritesWifi

    def _loadHeader(self):
        # ------------- Header Background Rectangle ------------- #
        rectHead = Rect(0, 0, self.screen_width,
                        self.statusBarHeight, fill=self.statusBackcolor)

        # ------------- LABEL - statusBrightness ------------- #
        self.statusTemperature.anchored_position = (2, self.statusBarHeight/2)

        # ------------- LABEL - statusDateTime ------------- #
        self.statusDateTime.anchored_position = (180, self.statusBarHeight/2)
        if self.screen_width > 320:
            self.statusDateTime.anchored_position = (
                self.screen_width/2, self.statusBarHeight/2)

        # ------------- GROUP - gpWifi ------------- #
        self.gpWifi.x = self.screen_width - self.statusBarHeight
        self.gpWifi.y = 0

        # ------------- Append items to the gpHeader ------------- #
        self.gpHeader.append(rectHead)
        self.gpHeader.append(self.statusTemperature)
        self.gpHeader.append(self.statusDateTime)
        self.gpHeader.append(self.gpWifi)

        return

    def _loadFooter(self):
        footerY = self.screen_height-self.statusBarHeight

        # ------------- Header Background Rectangle ------------- #
        rectFoot = Rect(0, footerY,
                        self.screen_width, self.statusBarHeight, fill=self.statusBackcolor)

        # ------------- GROUP - gpButtonDim ------------- #
        self._set_image(self.gpButtonDim, self.imageFolderPath +
                        "/" + self.IMG_FILE_DIM_ICON, centerImage=False)
        self.gpButtonDim.x = 0
        self.gpButtonDim.y = footerY

        # ------------- LABEL - statusBrightness ------------- #
        self.statusBrightness.anchored_position = (
            self.statusBarHeight + 4, footerY + self.statusBarHeight/2)

        # ------------- LABEL - statusEventCount ------------- #
        self.statusEventCount.anchored_position = (
            self.screen_width/2, footerY + self.statusBarHeight/2)

        # ------------- GROUP - gpButtonBright ------------- #
        self._set_image(self.gpButtonBright,
                        self.imageFolderPath + "/" + self.IMG_FILE_BRIGHT_ICON, centerImage=False)
        self.gpButtonBright.x = self.screen_width - self.statusBarHeight
        self.gpButtonBright.y = footerY

        # ------------- Append items to the gpFooter ------------- #
        self.gpFooter.append(rectFoot)
        self.gpFooter.append(self.gpButtonDim)
        self.gpFooter.append(self.statusBrightness)
        self.gpFooter.append(self.statusEventCount)
        self.gpFooter.append(self.gpButtonBright)

    # This will handle switching Images and Icons
    def _set_image(self, group, filename, x=0, y=0, centerImage=True, backcolor=None):
        """Set the image file for a given goup for display.
        This is most useful for Icons or image slideshows.
            :param group: The chosen group
            :param filename: The filename of the chosen image
        """
        # Remove all items from the group
        if group:
            for i, e in reversed(list(enumerate(group))):
                group.pop(i)
            gc.collect()

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

        imgX = x
        imgY = y

        if centerImage:
            imgX = int((self.screen_width - image.width)/2)
            imgY = int((self.screen_height - image.height)/2)

            if not(backcolor is None) and (imgX > 0 or imgY > 0):
                pallet01 = displayio.Palette(1)
                pallet01[0] = backcolor
                rect = vectorio.Rectangle(
                    pixel_shader=pallet01, 
                    width=self.screen_width, 
                    height=self.screen_height, 
                    x=0, 
                    y=0)
                group.append(rect)
        
        image_sprite.x = imgX
        image_sprite.y = imgY

        group.append(image_sprite)

        return

    # **************** PUBLIC METHODS ******************
    # This function allows us to change the background image
    def changeBackground(self, filename, useEventImageLocation=True, filenameContainsPath=False):
        # ------------- GROUP - gpBackground ------------- #
        fullFileName = self.imageFolderPath + "/" + filename

        if useEventImageLocation:
            fullFileName = self.eventImageFolderPath + "/" + filename
        if filenameContainsPath:
            fullFileName = filename

        try:
            self._set_image(self.gpBackground, fullFileName)
        except Exception as e:
            print(f"ERROR: Failed to load the image {fullFileName}\r\n{e}")
            self._set_image(self.gpBackground,
                            self.imageFolderPath + "/" + self.IMG_FILE_NOT_FOUND)

        return

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

        gc.collect()
