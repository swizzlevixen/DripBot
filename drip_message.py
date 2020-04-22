#!/usr/bin/env python

"""
Testing the webhook, or manually send a message as DripBot
"""

import argparse
from matterhook import Webhook

# -------------------------
# Argument setup
# -------------------------

parser = argparse.ArgumentParser(
    prog='python3 dripmessage.py',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description='Send a message to Mattermost as DripBot.')
parser.add_argument(
    '-m',
    '--message',
    type=str,
    help='Message to  be sent to the channel',
    required=True,
    )
parser.add_argument(
    '-c',
    '--channel',
    type=str,
    default="CHANNEL_NAME",
    help='Mattermost channel to send the message to',
    )
parser.add_argument(
    '-u',
    '--username',
    type=str,
    default="DripBot",
    help='User name whence the message came',
    )
parser.add_argument(
    '-i',
    '--iconurl',
    type=str,
    default="location/of/CoffeePot.png",
    help='URL for the icon to display as the user avatar',
    )
parser.add_argument(
    '-t',
    '--test',
    action="store_true",
    help='Test mode: send the message to the "TEST_CHANNEL_NAME"\nchannel as user "DripBot Test"',
    )
args = parser.parse_args()

if args.test is True:
    args.channel = "TEST_CHANNEL_NAME"
    args.username = "DripBot Test"

# -------------------------
# Webhook setup
# -------------------------

# mandatory parameters are url and your webhook API key
dripbot = Webhook('https://mattermost.example.com', 'API_KEY_HERE')
dripbot.username = args.username
dripbot.icon_url = args.iconurl


# -------------------------
# Test log prints
# -------------------------

# print(f"Message: {args.message}")
# print(f"Channel: {args.channel}")
# print(f"User name: {args.username}")
# print(f"Icon Url: {args.iconurl}")
# print(f"Test: {args.test}")

# -------------------------
# Send the message
# -------------------------

# send a message to the API_KEY's channel
# "scratch-area" for testing
dripbot.send(args.message, channel=args.channel)
