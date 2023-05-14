# PyPortal_Events
Modification of John Park’s PyPortal Event Countdown Clock project.

I recently purchased an Adafruit PyPortal and looked at using John Park’s project [PyPortal Event Countdown Clock](https://learn.adafruit.com/pyportal-event-countdown-clock "PyPortal Event Countdown Clock") project. It was easy to get it up and running but switching from CircuitPython 4 to 8, proved to cause a bit of a challenge, not with the code, but with the libraries. Some were moved from one file to multiple files in one folder but eventually, I got it all sorted out.

I plan to use the PyPortal on an upcoming cruise, which lead me to some ideas of how to change the code to make it a bit more useful and easier to change events. Below is a list of some of the ideas to be implemented.

- ***(Implemented)*** Allow for multiple events to be tracked.
- ***(Implemented)*** Use touch to change which event is being displayed.
- ***(Implemented)*** Add title and subtitle to the display.
- ***(Implemented)*** Load the events and event images from an SD Card.
	- ***(Implemented)*** Use a JSON file.
	- ***(Implemented)*** Create a webpage to easily modify the JSON.
- ***(Implemented)*** If possible, add the Wi-Fi information to the config file.
- Add a clock option and easily switch between countdown and clock.
- ***(Implemented but may need to change)*** Dim or turn off the backlight if the room is dark.
- Ignore events that have passed. (Date is not today but in the past.)

**IMPORTANT:** The included libraries are CircuitPython 8 libraries. If you are using CircuitPython 4.0, you will need to either change the library files to CircuitPython 4.0 libraries or upgrade to CircuitPython 8.0.<br />*As of May 2023, the Adafruit PyPortal - CircuitPython Powered Internet Display, [Product ID: 4116](https://www.adafruit.com/product/4116 "Product ID: 4116"), is shipped with CircuitPython 4.0.* 

**IMPORTANT:** This code is for a 320x240 pixel screen. If your PyPortal has a different resolution, I do not expect it to display properly. In the next version, I will attempt to address this but currently I do not have any other PyPortal devices to test it on.

## Installation ##

This project has a few folders. To install this on your PyPortal, do the following:

1. Copy the files from the PyPortal folder to your PyPortal over USB
2. Copy the files in the SD_Card folder to the SD Card in the device.<br />*This will need to be done on the PC, as you cannot access the SD Card from the USB Connection.*
3. (Optional) With the SD Card in your PC, open the index.html file in your web browser. (Chrome, Edge, Firefox, Safari, etc.)
	1. Either load the included config.json file to load the sample events or start to create your own events.
	2. If creating your own events, add your own images for the countdown and the day of the event to the SD Card.
	3. Go to the "Secrets" tab and enter the information for your Wi-FI connection, your timezone, and your Adafruit IO Account.
	4. Once changes are made, click on the "Save JSON file" button on either tab and save the JSON file to the SD Card as config.json.
	5. Insert the SD Card into the PyPortal.
	6. Press the reset button on the PyPortal to load the events from the SD Card.

## Next Steps ##

I'm currently working on a different redesign to improve the code and screen layout.

The new layout/version provides the following:

- Status bars on the top and bottom.
- Top status shows a clock, event count of N, and a bar indicator for Wi-Fi strength.
- Bottom status allows manually changing the brightness of the display or setting it to auto. It also displays the backlight brightness as a percentage.
- Will ignore events in the past.
- May use only one image for both the countdown and the day of the event. (May use different images but not certain yet.)