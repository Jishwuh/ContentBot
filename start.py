import colorama
from colorama import Fore, Back, Style, init
import os
import sys
import time
import random
import tkinter as tk
from tkinter import simpledialog
import pyfiglet
import json
from color_convert import color
import math

init(autoreset=True)


rgb_to_ansi = {
    (0, 0, 0): Fore.BLACK,
    (255, 0, 0): Fore.RED,
    (0, 255, 0): Fore.GREEN,
    (0, 0, 255): Fore.BLUE,
    (255, 255, 0): Fore.YELLOW,
    (0, 255, 255): Fore.CYAN,
    (255, 0, 255): Fore.MAGENTA,
    (128, 0, 0): Fore.RED,
    (128, 128, 0): Fore.YELLOW,
    (0, 128, 0): Fore.GREEN,
    (128, 0, 128): Fore.MAGENTA,
    (0, 128, 128): Fore.CYAN,
    (128, 128, 128): Fore.WHITE,
    (192, 192, 192): Fore.LIGHTWHITE_EX,
    (255, 128, 0): Fore.LIGHTRED_EX,
    (255, 255, 128): Fore.LIGHTYELLOW_EX,
    (0, 255, 128): Fore.LIGHTGREEN_EX,
    (255, 0, 255): Fore.LIGHTMAGENTA_EX,
    (0, 255, 255): Fore.LIGHTCYAN_EX,
    (128, 128, 128): Fore.LIGHTBLACK_EX
}

def find_nearest_ansi_color(rgb_color, rgb_to_ansi):
    min_distance = math.inf
    nearest_color = None

    for color, ansi in rgb_to_ansi.items():
        distance = math.sqrt(sum((c1-c2)**2 for c1, c2 in zip(color, rgb_color)))
        if distance < min_distance:
            min_distance = distance
            nearest_color = ansi

    return nearest_color

def getRGB(dec):
    rgb = color.ten_to_rgb(dec)
    split_result = rgb.rsplit(',', 1)
    r = split_result[0].replace('rgba(', '')
    r = f"({r})"
    my_tuple = eval(r)
    return my_tuple

def getConfig():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def open_input_box(prompt, default_value=""):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring("Input", prompt, initialvalue=default_value)
    root.destroy()  # Close the hidden window
    return user_input

def typeWriter(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        if char != "\n":
            time.sleep(0.05)
        else:
            time.sleep(0.5)

def cmdSize():
    #Reset the color
    os.system("color 07")
    os.system("mode con cols=100 lines=30")

def print_centered_text(text):
    columns = os.get_terminal_size().columns
    banner = pyfiglet.Figlet(font="big")
    banner_text = banner.renderText(text)
    print(Fore.CYAN + "\n".join(line.center(columns) for line in banner_text.splitlines()))

if __name__ == "__main__":
    cmdSize()
    print_centered_text("ContentBot")
    print_centered_text("Setup")
    typeWriter("Welcome to the ContentBot setup!\n")
    typeWriter("This setup will guide you through the process of setting up ContentBot.\n")
    typeWriter("The All In One Content Creator Discord Bot!\n")
    typeWriter("Let's get started!\n")
    typeWriter("First, we need you to enter your discord bot token.\n")
    #Ask the user if they have their token or if they need a guide
    typeWriter("Do you have your token? (Y/N)\n")
    while True:
        token = input()
        if token == "Y":
            typeWriter("Please enter your token.\n")
            #Open an input box with tkinter
            token = open_input_box("Enter your token: ")
            break
        elif token == "N":
            typeWriter("Please follow this guide to get your token.\n")
            typeWriter("https://discordgsm.com/guide/how-to-get-a-discord-bot-token\n")
            typeWriter("Please enter your token.\n")
            token = open_input_box("Enter your token: ")
            break
        else:
            typeWriter("Please enter a valid option.\n")
            continue
    typeWriter("Great! Now we need your guild ID.\n")
    typeWriter("Please enter your guild ID.\n")
    guild_id = open_input_box("Enter your guild ID: ")
    typeWriter("Great! Now here comes the more complex stuff.")
    typeWriter("Here are the default roles and colors that ContentBot uses.\n")
    cfg = getConfig()
    for i in cfg['roles']:
        # colorRaw = i['color']
        # tup = getRGB(colorRaw)
        # colorGet = find_nearest_ansi_color(rgb_color=tup, rgb_to_ansi=rgb_to_ansi)
        # print(colorGet + i['name'])