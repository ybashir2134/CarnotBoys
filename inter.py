import tkinter as tk
import pygame
import sys

def validate_temperatures(boiler_temp, cooler_temp):
    # Define your valid temperature range and validation logic
    valid_range = (0, 100)
    try:
        boiler_temp = float(boiler_temp)
        cooler_temp = float(cooler_temp)
        return boiler_temp > cooler_temp and valid_range[0] <= boiler_temp <= valid_range[1] and valid_range[0] <= cooler_temp <= valid_range[1]
    except ValueError:
        return False

def runTk():
    root = tk.Tk()
    root.title("Temperature Input")

    tk.Label(root, text="Boiler Temperature:").pack()
    boiler_temp_entry = tk.Entry(root)
    boiler_temp_entry.pack()

    tk.Label(root, text="Cooler Temperature:").pack()
    cooler_temp_entry = tk.Entry(root)
    cooler_temp_entry.pack()

    error_label = tk.Label(root, text="", fg="red")
    error_label.pack()

    temperatures = [None, None]  # To store valid temperature values

    def on_submit():
        if validate_temperatures(boiler_temp_entry.get(), cooler_temp_entry.get()):
            temperatures[0] = float(boiler_temp_entry.get())
            temperatures[1] = float(cooler_temp_entry.get())
            root.destroy()
        else:
            error_label.config(text="Invalid temperatures. Ensure cooler temp is less than boiler temp.")

    submit_btn = tk.Button(root, text="Submit", command=on_submit)
    submit_btn.pack()

    # Handle window close event
    def on_window_close():
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_window_close)

    root.mainloop()
    return temperatures

# Run Tkinter interface and get temperature values
boiler_temperature, cooler_temperature = runTk()

# Check if temperatures are valid before starting Pygame
if boiler_temperature is not None and cooler_temperature is not None:
    # Initialize Pygame
    pygame.init()
    win = pygame.display.set_mode((500, 500))

    # Pygame main loop
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        win.fill((255, 255, 255))  # Fill the window with white color
        pygame.display.update()

    pygame.quit()
