# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# Further modified by Matias Andina, 2024
# -*- coding: utf-8 -*-

import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import psutil
import sys

def safe_retrieve(callable_func, *args, **kwargs):
    try:
        result = callable_func(*args, **kwargs)
        return result
    except Exception as e:
        print(f"Error retrieving {callable_func.__name__}: {str(e)}")  # Print error to command line
        return "N/A"

def get_mac(interface = 'wlan0'):
    # This is good for Raspberry PIs, not good for other OS !
    # possible interfaces ['wlan0', 'eth0']
    try:
        mac = open('/sys/class/net/'+interface+'/address').readline()
    except:
        mac = "00:00:00:00:00:00"
    return f"MAC: {mac[0:17]}"

def get_ip():
    cmd = "hostname -I | cut -d' ' -f1"
    ip = safe_retrieve(subprocess.check_output, cmd, shell=True).decode("utf-8")
    return f"IP: {ip}" if ip != "N/A" else "N/A"

def get_cpu_load():
    cpu_load = safe_retrieve(psutil.cpu_percent)
    return f"CPU Load: {cpu_load:.2f}%" if cpu_load != "N/A" else "N/A"

def get_memory_usage():
    memory = safe_retrieve(psutil.virtual_memory)
    if memory != "N/A":
        memory_used = memory.used / (1024**3)
        memory_total = memory.total / (1024**3)
        return f"Mem: {memory_used:.0f}/{memory_total:.0f} Gb"
    return "N/A"

def get_disk_usage():
    disk = safe_retrieve(psutil.disk_usage, '/')
    if disk != "N/A":
        return f"Disk: {disk.used/1024**3:.1f}/{disk.total/1024**3:.1f} GB"
    return "N/A"

def get_cpu_temperature():
    temp_info = safe_retrieve(psutil.sensors_temperatures)
    if temp_info != "N/A" and 'cpu_thermal' in temp_info:
        temp = temp_info['cpu_thermal'][0].current
        return f"CPU Temp: {temp:.1f} C"
    return "N/A"

def get_system_metrics():
    return {
        "MAC": get_mac(),
        "IP": get_ip(),
        "CPU": get_cpu_load(),
        "Mem": get_memory_usage(),
        "Disk": get_disk_usage(),
        "Temp": get_cpu_temperature()
    }


def get_string_coords(font_obj, string):
    '''
    This is a glorified wrapper of font.font.getsize(string), which returns a tupple. 
    We will unpack the first element of such tupple
    '''
    return font_obj.font.getsize(string)[0]

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

try:
    # Setup SPI bus using hardware SPI:
    spi = board.SPI()

    # Create the ST7789 display:
    disp = st7789.ST7789(
        spi,
        cs=cs_pin,
        dc=dc_pin,
        rst=reset_pin,
        baudrate=BAUDRATE,
        width=135,
        height=240,
        x_offset=53,
        y_offset=40,
    )
    print("ST7789 Display Initialized")
    # Turn on the backlight
    backlight = digitalio.DigitalInOut(board.D22)
    backlight.switch_to_output()
    backlight.value = True

except Exception as e:
    print(f"Failed to initialize hardware or SPI: {str(e)}")
    sys.exit(1)  # Exit with error status

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Define the style dictionary for text color
style_key = {
    "MAC": {"fill": "#FFFFFF", "font_size": 18},
    "IP": {"fill": "#FFFFFF", "font_size": 24},
    "CPU": {"fill": "#FFFF00", "font_size": 24},
    "Mem": {"fill": "#00FF00", "font_size": 24},
    "Disk": {"fill": "#0000FF", "font_size": 24},
    "Temp": {"fill": "#FF00FF", "font_size": 24}
}

while True:
    draw.rectangle((0, 0, width, height), outline=0, fill=0)  # Clear the image.
    metrics = get_system_metrics()
    y = top
    y_white_space = 2  # px

    for key, value in metrics.items():
        style = style_key.get(key)
        fill_color = style["fill"]
        font_size = style["font_size"]
        # Alternatively load a TTF font.  Make sure the .ttf font file is in the
        # same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        # we reload the font so that we can pass different font_size if needed
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        
        draw.text((x, y), value, font=font, fill=fill_color)
        y += font.getsize(value)[1] + y_white_space

    disp.image(image, rotation)
    time.sleep(1)

