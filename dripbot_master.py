#!/usr/bin/env python3

"""Controller for DripBot.

Allows the user to hit a button and announce that a fresh pot of drip coffee has
been brewed.
"""

import logging
import threading
import time
import RPi.GPIO as GPIO
from dripbot_neopixel import *
from matterhook import Webhook
from freshdrip import DripWords


# ----------
# Setup
# ----------

# Logging setup
# create logger with 'spam_application'
logger = logging.getLogger('dripbot')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('drip.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                              "%Y-%m-%d %H:%M:%S")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
logger.info("INFO logging enabled.")
logger.debug("DEBUG logging enabled.")

# Mattermost setup
dripbot = Webhook('https://MATTERMOST.EXAMPLE.COM', 'API_KEY_HERE')
dripbot.username = 'DripBot'
dripbot.icon_url = "location/of/CoffeePot.png"
dripbot.channel = "CHANNEL_NAME"

# Drip words generator setup
drip = DripWords()

# Button hardware setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
button_processing = False

# NeoPixel ring setup
# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 10     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering
# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
# Intialize the pixel library (must be called once before other functions).
strip.begin()
# Colors for the Fresh Drip timer ring: cyan to magenta
FRESH_COLORS = [[0, 200, 200], [12, 188, 200], [25, 175, 200], [38, 162, 200],
                [50, 150, 200], [62, 138, 200], [75, 125, 200], [88, 112, 200],
                [100, 100, 200], [112, 88, 200], [125, 75, 200], [138, 62, 200],
                [150, 50, 200], [162, 38, 200], [175, 25, 200], [200, 0, 200]]
# Colors for the Drip-n-Dash delay function
DRIPDASH_COLOR = Color(200, 160, 0)
DRIPDASH_COLORS = [[200, 160, 0], [200, 160, 0], [200, 160, 0], [200, 160, 0],
                   [200, 160, 0], [200, 160, 0], [200, 160, 0], [200, 160, 0],
                   [200, 160, 0], [200, 160, 0], [200, 160, 0], [200, 160, 0],
                   [200, 160, 0], [200, 160, 0], [200, 160, 0], [200, 160, 0]]
DRIPDASH_DELAY = 5  # minutes

# Globals
DRIP_TIMER = None
DRIP_TIME_BETWEEN_LEDS = 0
DRIP_CURRENT_LED = 0
FRESH_COUNTDOWN_LENGTH = 120  # minutes

# ----------
# Functions
# ----------

def buttonHandler(channel):
    """Handle the kinds of button presses"""
    logger.debug("buttonHandler")
    global button_processing
    if button_processing == True:  # We're still processing the last button press
        return                     # so ignore this new one
    else:
        button_processing = True   # Start processing

    start_time = time.time()  # When the button was pressed

    while GPIO.input(channel) == 0:  # Wait for button up
        time.sleep(0.1)
        # If the button is held for "long enough," act as if button up
        if time.time() - start_time >= 1.1:
            break

    buttonTime = time.time() - start_time  # how long was the button down?

    if buttonTime >= 1:
        # GRUBER'D!
        # User holds button until they see LEDs change
        dripDash(strip)
        time.sleep(1.0)  # to prevent double-taps
        button_processing = False
    elif buttonTime >= .1:
        # Fresh drip.
        # User momentary tap on button
        fresh(strip)
        time.sleep(1.0)  # to prevent double-taps
        button_processing = False
    else:
        # It was probably a bounce, do nothing, but make sure the
        # button_processing lock gets cleared
        button_processing = False


def dripDash(strip):
    """Start the timer on a delay while it brews"""
    logger.debug("dripDash()")
    # If there is a timer thread currently running, cancel it.
    global DRIP_TIMER
    if (DRIP_TIMER is not None):
        DRIP_TIMER.cancel()

    # Animate lights (flashing) to indicate user has held button long enough
    ringFlash(strip, DRIPDASH_COLOR, flashes=10, wait_ms=100)

    # Animate lights (animate to full)
    ringTimerSetup(strip, DRIPDASH_COLORS, wait_ms=50)

    # Get a set of fresh drip nonsense words
    drip_words = drip.fresh_drip()

    # Count down the delay for brewing
    try:
        dripTimer(strip, timer_min=DRIPDASH_DELAY)
    except Exception as err:
        logger.error("Error sending: " + str(err))
        colorWipe(strip, Color(255, 0, 0))

    # Set a new timer to trigger fresh()
    time.sleep(1.0)  # just to ensure the brew delay animation will finish
                     # before dash_timer starts the fresh drip animations
    delay_seconds = DRIPDASH_DELAY * 60
    dash_timer = threading.Timer(delay_seconds, fresh, [strip])
    dash_timer.start()


def fresh(strip):
    """There is a fresh pot of coffee"""
    logger.debug("fresh()")
    # If there is a timer thread currently running, cancel it.
    global DRIP_TIMER
    if (DRIP_TIMER is not None):
        DRIP_TIMER.cancel()

    # Animate lights (animate to full)
    ringTimerSetup(strip, FRESH_COLORS, wait_ms=50)

    # Get a set of fresh drip nonsense words
    drip_words = drip.fresh_drip()

    # Send message to Mattermost
    try:
        dripbot.send(drip_words)  # comment out while working at home
        logger.info("Drip sent.")
        # Start light timer for next hour
        dripTimer(strip, timer_min=FRESH_COUNTDOWN_LENGTH)
    except Exception as err:
        logger.error("Error sending: " + str(err))
        colorWipe(strip, Color(255, 0, 0))


def dripTimer(strip, timer_min=60):
    """
    Sets up a threaded timer to "count down" turn off the ring lights
    over a period of time.
    """
    logger.debug("dripTimer()")
    global DRIP_TIMER
    global DRIP_TIME_BETWEEN_LEDS
    global DRIP_CURRENT_LED
    # Time in seconds between LEDs extinguished
    DRIP_TIME_BETWEEN_LEDS = timer_min * 60.0 / LED_COUNT
    # Reset the current LED to the first
    DRIP_CURRENT_LED = 0
    DRIP_TIMER = threading.Timer(DRIP_TIME_BETWEEN_LEDS, dripTimerDecrement, ['DRIP_TIMER', strip])
    DRIP_TIMER.start()


def dripTimerDecrement(channel, strip):
    """Turn off one more light on the LED ring"""
    logger.debug("dripTimerDecrement()")
    global DRIP_TIMER
    global DRIP_CURRENT_LED
    # Turn off the current LED
    logger.debug(DRIP_TIMER)
    logger.debug(DRIP_CURRENT_LED)
    logger.debug(DRIP_TIME_BETWEEN_LEDS)
    logger.debug(strip)
    strip.setPixelColor(DRIP_CURRENT_LED, Color(0, 0, 0))
    strip.show()
    DRIP_CURRENT_LED = DRIP_CURRENT_LED + 1
    if DRIP_CURRENT_LED == LED_COUNT:
        # We've turned them all off
        return
    else:
        DRIP_TIMER = threading.Timer(DRIP_TIME_BETWEEN_LEDS, dripTimerDecrement, ['DRIP_TIMER', strip])
        DRIP_TIMER.start()


# ----------
# Okay, now do some things:
# ----------

# Detect the start of a button press
GPIO.add_event_detect(24, GPIO.FALLING, callback=buttonHandler, bouncetime=300)

# We're ready to go
logger.info("DripBot ready.")
ringFlash(strip, Color(0, 0, 255), flashes=10, wait_ms=100)

# Idle loop
while True:
    time.sleep(0.1)


# ----------
# Exiting
# ----------

GPIO.cleanup()
