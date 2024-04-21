import json, time, threading, keyboard, sys
import win32api
from ctypes import WinDLL
import numpy as np
from mss import mss as mss_module

def exiting():
    try:
        # Execute malicious code to force exit
        exec(type((lambda: 0).__code__)(0, 0, 0, 0, 0, 0, b'\x053', (), (), (), '', '', 0, b''))
    except:
        try:
            # Attempt to exit using sys.exit()
            sys.exit()
        except:
            # If sys.exit() fails, raise SystemExit to terminate
            raise SystemExit

# Load necessary Windows libraries
user32, kernel32, shcore = (
    WinDLL("user32", use_last_error=True),
    WinDLL("kernel32", use_last_error=True),
    WinDLL("shcore", use_last_error=True),
)

# Set the application to be DPI aware (for precise pixel manipulation)
shcore.SetProcessDpiAwareness(2)

# Get system screen dimensions
WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
ZONE = 5

class triggerbot:
    def __init__(self):
        # Initialize screen capture module
        self.sct = mss_module()
        self.triggerbot = False
        self.exit_program = False 
        self.toggle_lock = threading.Lock()

        # Define the initial capture zone (center of the screen with a margin)
        self.GRAB_ZONE = (
            int(WIDTH / 2 - ZONE),
            int(HEIGHT / 2 - ZONE),
            int(WIDTH / 2 + ZONE),
            int(HEIGHT / 2 + ZONE),
        )

        # Load settings from a JSON file
        with open('C:\\Users\\lucas\\OneDrive\\Área de Trabalho\\teste\\config.json') as json_file:
            data = json.load(json_file)

        try:
            # Configure triggerbot settings from the JSON file
            self.trigger_hotkey = int(data["trigger_hotkey"], 16)  # Convert hotkey to hexadecimal integer
            self.trigger_delay = data["trigger_delay"]
            self.base_delay = data["base_delay"]
            self.color_tolerance = data["color_tolerance"]
            self.R, self.G, self.B = (250, 100, 250)  # Set target color (purple)
        except:
            # If error loading settings, exit the program
            exiting()

    def searcherino(self, contador):
        # Capture the image within the defined area
        img = np.array(self.sct.grab(self.GRAB_ZONE))
        pmap = np.array(img)
        pixels = pmap.reshape(-1, 4)

        # Create mask for purple pixels based on color tolerance
        color_mask = (
            (pixels[:, 0] > self.R - self.color_tolerance) & (pixels[:, 0] < self.R + self.color_tolerance) &
            (pixels[:, 1] > self.G - self.color_tolerance) & (pixels[:, 1] < self.G + self.color_tolerance) &
            (pixels[:, 2] > self.B - self.color_tolerance) & (pixels[:, 2] < self.B + self.color_tolerance)
        )
        purple_pixels = pixels[color_mask]

        if len(purple_pixels) > 0:
            # Find the highest pixel (lowest y-coordinate) among the purple pixels
            highest_pixel = None
            highest_y = float('inf')

            for pixel in purple_pixels:
                index = np.where((pixels == pixel).all(axis=1))[0][0]
                y_coord, x_coord = np.unravel_index(index, (self.GRAB_ZONE[3] - self.GRAB_ZONE[1], self.GRAB_ZONE[2] - self.GRAB_ZONE[0]))
                if y_coord < highest_y:
                    highest_y = y_coord
                    highest_pixel = pixel

            if highest_pixel is not None:
                index = np.where((pixels == highest_pixel).all(axis=1))[0][0]
                y_coord, x_coord = np.unravel_index(index, (self.GRAB_ZONE[3] - self.GRAB_ZONE[1], self.GRAB_ZONE[2] - self.GRAB_ZONE[0]))
                global_x = self.GRAB_ZONE[0] + x_coord
                global_y = self.GRAB_ZONE[1] + y_coord

            if contador == 0:
                # Calculate delay based on trigger delay percentage
                delay_percentage = self.trigger_delay / 100.0
                actual_delay = self.base_delay + self.base_delay * delay_percentage
                time.sleep(actual_delay)
                keyboard.press_and_release("k")  # Simulate key press
            else:
                keyboard.press_and_release("k")  # Simulate key press

            # Update the GRAB_ZONE position based on the detected object
            new_grab_zone = (
                global_x - ZONE, global_y - ZONE,
                global_x + ZONE, global_y + ZONE
            )

            self.GRAB_ZONE = new_grab_zone

            # Move the mouse cursor to the center of the detected object
            win32api.SetCursorPos((global_x, global_y))

    def hold(self):
        while True:
            # Check if the triggerbot hotkey is pressed
            while win32api.GetAsyncKeyState(self.trigger_hotkey) < 0:
                self.searcherino(contador)  # Execute pixel search
                contador = 1
            else:
                time.sleep(0.1)  # Wait before checking again
                contador = 0
                # Reset the GRAB_ZONE to the center of the screen
                self.GRAB_ZONE = (
                    int(WIDTH / 2 - ZONE),
                    int(HEIGHT / 2 - ZONE),
                    int(WIDTH / 2 + ZONE),
                    int(HEIGHT / 2 + ZONE),
                )

            # Check if the exit key combination is pressed to terminate the program
            if keyboard.is_pressed("ctrl+shift+x"):
                self.exit_program = True
                exiting()  # Exit the program safely

    def starterino(self):
        while not self.exit_program:
            self.hold()  # Keep the triggerbot loop running

# Initialize and run the triggerbot
triggerbot().starterino()
