import tkinter as tk
import pygame
import sys
import time

cycle = pygame.image.load('images.jpg')

def update_water_level(surface, rect, quality):
    # Draw the full volume
    pygame.draw.rect(surface, (200, 200, 200), rect)  # Grey rectangle for the full volume

    # Calculate the filled portion based on quality
    fill_height = int(rect.height * quality)
    fill_rect = pygame.Rect(rect.left, rect.bottom - fill_height, rect.width, fill_height)

    # Draw the filled portion
    pygame.draw.rect(surface, (255, 255, 0), fill_rect)  # Yellow rectangle for water

def animate_water_level(target_quality, current_quality, speed):
    # Animate the water level
    if current_quality < target_quality:
        current_quality += speed
        if current_quality > target_quality:
            current_quality = target_quality
    elif current_quality > target_quality:
        current_quality -= speed
        if current_quality < target_quality:
            current_quality = target_quality

    animation_complete = current_quality == target_quality
    return current_quality, animation_complete

def move_marker(current_pos, target_pos, speed):
    dx, dy = target_pos[0] - current_pos[0], target_pos[1] - current_pos[1]
    distance = (dx**2 + dy**2)**0.5
    if distance <= speed:
        return target_pos # The marker has reached target position
    else:
        direction = (dx/distance, dy/distance)
        new_pos = current_pos[0] + direction[0] * speed, current_pos[1] + direction[1] * speed
        return new_pos
    

    
def validate_temperatures(boiler_temp, cooler_temp):
    # Define your valid temperature range and validation logic
    valid_range = (28.96, 374.10)
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
            error_label.config(text= f"This simulation can only assess temperatures between 28.96 and 374.10 Celcius \n Also make sure your cooler temperature is less than the hot one")

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
temp = boiler_temperature
ltemp = cooler_temperature

import anim as am

# _____________________________________________________________________________________________--
import anim as am
import numpy as np

carof = am.caref(ltemp, temp)
initpres, initvol, finvol, initent, finent = am.isothermal_addition(temp)
_, _, qual, qual_phase, fin_press, _ = am.adiabatic_expansion(temp, ltemp)
new_qual, new_phase, _, _ = am.isothermal_rejection(temp, ltemp)

steps12 = np.linspace(ltemp, temp, 31)
temp_range1 = steps12[1:100]  # or adjust according to your requirement
temp_range2 = temp_range1[::-1]

phase2 = [((((finent-am.entliq_extrap(i))/(am.entvap_extrap(i) - am.entliq_extrap(i)))*(am.satvap_extrap(i)-am.satliq_extrap(i)))+am.satliq_extrap(i)) for i in temp_range2]
phase4 = [((((initent-am.entliq_extrap(i))/(am.entvap_extrap(i) - am.entliq_extrap(i)))*(am.satvap_extrap(i)-am.satliq_extrap(i)))+ am.satliq_extrap(i)) for i in temp_range1]
press2 = [am.pres_extrap(i) for i in temp_range2]

car_sent = f'Carnot Efficiency: {carof:.2f}'
wpm_sent = f'Work Per Mass: {((temp-ltemp)*(finent - initent)):.2f}'
qpm_sent = f'Heat input per Mass: {((temp + 273.15)*(finent - initent)):.2f}'


# ________________________________________________________________________________________________

# Define the rectangle for phase composition
composition_rect = pygame.Rect(400, 50, 100, 150)



# Define the stop points and the duration of each stop
stop_points = {1: 2, 3: 2, 5: 2, 7: 2}  # Example: stop at points 1 and 3 for 5 seconds each
current_stop_time = None  # Time when the marker arrived at a stop point
marker_active = True  # The marker is active initially

def print_live_graph():
    am.plotter(initvol, finvol, qual_phase, new_phase, initpres, fin_press)
    # Here, you would add your code to display the live graph


# Check if temperatures are valid before starting Pygame
if boiler_temperature is not None and cooler_temperature is not None:
    # Initialize Pygame
    pygame.init()
    pygame.font.init()  # Initialize font module
    font = pygame.font.SysFont('Arial', 20)  # Choose a font and size
    win = pygame.display.set_mode((500, 500))

    button_color = (0, 200, 0)  # Green color
    button_hover_color = (0, 255, 0)  # Brighter green when hovered
    button_rect = pygame.Rect(350, 450, 150, 50)  # x, y, width, height
    button_text = "Show Live PV Graph"

    def draw_button(surface, font, rect, text, color, hover_color):
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, hover_color, rect)  # Button hover color
        else:
            pygame.draw.rect(surface, color, rect)  # Button normal color

        text_surface = font.render(text, True, (255, 255, 255))  # White text
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

    def render_additional_text(surface, font, text, position, text_color=(255,255,255)):
        text_surface = font.render(text, True, text_color)
        surface.blit(text_surface, position)

    def render_information(surface, font, data, position, bg_color=(255, 255, 255)):
        text_color = (0, 0, 0)  # Black text for visibility
        lines = [f"{key}: {value}" for key, value in data.items()]

        # Calculate the total height for the text area
        total_height = sum(font.get_height() for _ in lines) + len(lines) - 1

        # Clear the old text
        clear_rect = pygame.Rect(position[0], position[1] + 185 , surface.get_width(), total_height + 6)
        pygame.draw.rect(surface, bg_color, clear_rect)

        # Render and blit each line of text
        text_y = position[1]
        for line in lines:
            text_surface = font.render(line, True, text_color)
            surface.blit(text_surface, (position[0], text_y + 187))
            text_y += font.get_height()


    def render_quality_text(surface, font, quality, pressures, temperatures, entropies, quality_index, rect):
        text_color = (255, 0, 0)  # Red for visibility
        bg_color = (255, 255, 255)  # Background color
        
        # Define the texts for each line
        lines = [
            f'x = {quality:.2f}',
            f'Pressure = {pressures[quality_index]}',
            f'Temperature = {temperatures[quality_index]}',
            f'Entropy = {entropies[quality_index]}',
            f'Volumes = {spvolumes[quality_index]}',
        ]
        
        # Starting y position for text
        text_y_position = rect.y + rect.height + 5
        
        # Clear the old text by drawing a rectangle filled with the background color
        clear_rect_height = len(lines) * (font.get_height() + 2)  # Calculate total height needed for text
        clear_rect = pygame.Rect(rect.x - 100, text_y_position, rect.width + 90, clear_rect_height)
        pygame.draw.rect(surface, bg_color, clear_rect)
        
        # Render and blit each line of text
        for line in lines:
            text_surface = font.render(line, True, text_color)
            surface.blit(text_surface, (rect.x - 100, text_y_position))
            text_y_position += font.get_height() + 2  # Move to the next line position


    
    # Path definition
    log_path = [(70,40),(134,40),(206,40),(206,80),(206,120),(140,120),(70,120),(70,80),(70,40)]

    running = True
    marker_position = log_path[0]  # Start at the first position in the path
    current_point = 0  # Current index in the path
    next_point = 1  # Next index in the path
    stop_duration = 5  # Duration of stops in seconds
    stop_end_time = None  # Time when the stop should end
    
    # Starting point
    current_point = 0

    # Define the marker as a simple circle for now
    marker_radius = 5
    marker_color = (255,0,0) # Color

    # Speed of the marker
    speed = 1

    composition_rect = pygame.Rect(400, 50, 100, 150)

    # Define a separate index for accessing quality values
    quality_index = 0

    # Example quality values for different stages
    quality_values = [0, 1 - qual, 1 - new_qual, 1]  # Replace with your actual values
    pressures = [float(f'{initpres:.2f}'), float(f'{fin_press:.2f}'), float(f'{fin_press:.2f}'), float(f'{initpres:.2f}')]
    temperatures = [temp, ltemp, ltemp,temp]
    entropies = [float(f'{finent:.2f}'), float(f'{finent:.2f}'), float(f'{initent:.2f}'),float(f'{initent:.2f}')]
    spvolumes = [float(f'{finvol:.2f}'),float(f'{qual_phase:.2f}'),float(f'{new_phase:.2f}'),float(f'{initvol:.2f}')]
    current_quality = 0
    animation_in_progress = False

    markers_info = {
    (55, 15): {"x": quality_values[3], "pressure": pressures[3], "entropy": entropies[3], "temperature": temperatures[3], "Specific Volume": spvolumes[3]},
    (240, 15): {"x": quality_values[0], "pressure": pressures[0], "entropy": entropies[0], "temperature": temperatures[0], "Specific Volume": spvolumes[0]},
    (275, 140): {"x": quality_values[1], "pressure": pressures[1], "entropy": entropies[1], "temperature": temperatures[1], "Specific Volume": spvolumes[1]},
    (35, 140): {"x": quality_values[2], "pressure": pressures[2], "entropy": entropies[2], "temperature": temperatures[2], "Specific Volume": spvolumes[2]}
}

    not_clicked = True
    
    display_data = None
    # Main loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    # Call the function to display the live graph
                    print_live_graph()

            # Handle clicks for static markers only when the moving marker is not active
            if event.type == pygame.MOUSEBUTTONDOWN and not marker_active:
                mouse_x, mouse_y = event.pos
                for marker_pos, data in markers_info.items():
                    if (mouse_x - marker_pos[0]) ** 2 + (mouse_y - marker_pos[1]) ** 2 <= 10 ** 2:
                        display_data = data
                        update_water_level(win, composition_rect, display_data["x"])
                        break

        win.blit(cycle, (0, 0))  # Blit the image of the turbine

        # Handle marker movement and stopping logic
        if not animation_in_progress and marker_active:
            marker_position = move_marker(marker_position, log_path[current_point], speed)
            if marker_position == log_path[current_point]:
                if current_point in stop_points:
                    # Start the animation if not already in progress and at a stop point
                    if quality_index < len(quality_values):
                        target_quality = quality_values[quality_index]
                        animation_in_progress = True
                        stop_end_time = time.time() + stop_duration
                current_point = (current_point + 1) % len(log_path)  # Move to the next point
                if current_point == 0 and quality_index >= len(quality_values):
                    # If the marker has completed its cycle and all animations, deactivate it
                    marker_active = False

        # Water level animation logic
        if animation_in_progress and (stop_end_time is None or time.time() > stop_end_time):
            current_quality, animation_complete = animate_water_level(target_quality, current_quality, 0.01)
            update_water_level(win, composition_rect, current_quality)
            
            # Render and display the quality text beneath the composition rectangle
            render_quality_text(win, font, current_quality, pressures, temperatures, entropies, quality_index, composition_rect)

            if animation_complete:
                animation_in_progress = False
                quality_index += 1  # Increment quality index after completing the animation


        # Draw the marker only if it's active
        if marker_active:
            pygame.draw.circle(win, marker_color, (int(marker_position[0]), int(marker_position[1])), marker_radius)
        else:
            for position in markers_info.keys():
                pygame.draw.circle(win, (0, 0, 255), position, 10)  # Draw static markers

            # Display information if available
            if display_data:
                render_information(win, font, display_data, (20, 20))
            else:
                # Optionally clear previous information
                render_information(win, font, {key: "" for key in next(iter(markers_info.values())).keys()}, (20, 20))

            pos1 = (0, 400)  # Adjust as needed
            pos2 = (0, 420)
            pos3 = (0, 440)
            render_additional_text(win, font, car_sent, pos1)
            render_additional_text(win, font, wpm_sent, pos2)
            render_additional_text(win, font, qpm_sent, pos3)

            if not_clicked:
                draw_button(win, font, button_rect, button_text, button_color, button_hover_color)



        pygame.display.flip()
        pygame.time.Clock().tick(60)

