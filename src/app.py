import pygame
from pathlib import Path
import random
import logging as log
import math

log.basicConfig(filename="app.log", level=log.INFO)

pygame.init()

BACKGROUND = (255, 160, 115)
LIGHT_BUTTON = (215, 120, 120)
DARK_BUTTON = (180, 120, 120)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
GREEN = (75, 180, 75)

font = pygame.font.Font(None, 36)

# Set up the screen
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("chemizard")


# data structure helpers
def convert_to_tuples(connections):
    return [(int(x[0]), int(x[1])) for x in connections]


def are_equivalent(connections, current_overlap_indices):
    # Convert connections to tuples
    connections_tuples = set(convert_to_tuples(connections))
    
    # Convert current_overlap_indices to set
    current_overlap_set = set(current_overlap_indices)
    
    # Check if the sets are equivalent
    return connections_tuples == current_overlap_set


# display helpers
def display_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


# Function to display buttons
def draw_button(text, x, y, width, height, active=False):
    color = LIGHT_BUTTON if not active else DARK_BUTTON
    pygame.draw.rect(screen, color, (x, y, width, height))
    display_text(text, BLACK, x + 10, y + 10)


def list_activities():
    activities = sorted([d.name for d in Path("activities/").iterdir() if d.is_dir()])
    return activities


def list_activity_files(activity):
    files = sorted(
        [
            f.name
            for f in Path(f"activities/{activity}/").iterdir()
            if f.is_file() and f.suffix == ".txt"
        ]
    )
    return files


# parser
def parse_hydrocarbon_file(file):
    try:
        with open(file, "r") as f:
            lines = f.readlines()
            elements = "".join(char for char in lines[0].strip() if char in ["c", "h"])
            print("elements: ", elements)
            possible_connections = lines[1].strip().split()
            print("possible_connections: ", possible_connections)
            model_link = lines[2].strip()
        return elements, possible_connections, model_link
    except Exception as e:
        log.error(f"Error parsing file: {e}")
        return None, None, None


# Main function to run the program
def main():
    current_screen = "title"
    current_activity = ""
    current_elements = None
    current_connections = None

    current_overlap_indices = []
    # all_overlap_indices = []

    clock = pygame.time.Clock()  # Clock object to control frame rate
    fps = 30  # Desired frames per second

    running = True
    dragging = False
    dragged_circle = None
    offset_x = 0
    offset_y = 0
    escape_pressed = False  # Flag to track continuous Escape key presses


    while running:
        screen.fill(BACKGROUND)

        # Title screen
        if current_screen == "title":
            display_text("chemizard", BLACK, screen.get_width() // 2 - 70, 100)

            activities = list_activities()
            for i, activity in enumerate(activities):
                draw_button(
                    activity, screen.get_width() // 2 - 150, 200 + i * 50, 300, 40
                )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, activity in enumerate(activities):
                        if (
                            screen.get_width() // 2 - 150
                            <= event.pos[0]
                            <= screen.get_width() // 2 + 150
                            and 200 + i * 50 <= event.pos[1] <= 240 + i * 50
                        ):
                            current_screen = "activity_select"
                            current_activity = activity
                    if (
                        screen.get_width() // 2 - 50
                        <= event.pos[0]
                        <= screen.get_width() // 2 + 50
                        and screen.get_height() - 100
                        <= event.pos[1]
                        <= screen.get_height() - 60
                    ):
                        running = False  # Quit the program if Quit button is clicked
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    escape_pressed = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    escape_pressed = False

        # Activity selection screen
        elif current_screen == "activity_select":
            display_text(
                f"{current_activity}",
                BLACK,
                screen.get_width() // 2 - 100,
                100,
            )

            draw_button(
                "Back", screen.get_width() // 2 - 50, screen.get_height() - 100, 100, 40
            )  # Back button

            files = list_activity_files(current_activity)
            if files:
                for i, file in enumerate(files):
                    draw_button(
                        file[:-4], screen.get_width() // 2 - 150, 200 + i * 50, 300, 40
                    )

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if (
                            screen.get_width() // 2 - 50
                            <= event.pos[0]
                            <= screen.get_width() // 2 + 50
                            and screen.get_height() - 100
                            <= event.pos[1]
                            <= screen.get_height() - 60
                        ):
                            current_screen = "title"
                        for i, file in enumerate(files):
                            if (
                                screen.get_width() // 2 - 150
                                <= event.pos[0]
                                <= screen.get_width() // 2 + 150
                                and 200 + i * 50 <= event.pos[1] <= 240 + i * 50
                            ):
                                elements, connections, model_link = (
                                    parse_hydrocarbon_file(
                                        f"activities/{current_activity}/{file}"
                                    )
                                )
                                if elements is not None:
                                    current_screen = "activity"
                                    
                                    # Determine the maximum radius among all atoms
                                    max_radius = max(30, 15)  # Maximum radius for 'c' and 'h' atoms

                                    # Generate random coordinates for each element
                                    current_elements = []
                                    current_element_idx = 0
                                    for element in elements:
                                        # Generate initial random coordinates
                                        x = random.randint(max_radius, screen.get_width() - max_radius)
                                        y = random.randint(max_radius, screen.get_height() - max_radius)

                                        # Ensure the initial coordinates do not overlap with existing circles
                                        for existing_element in current_elements:
                                            # Calculate distance between centers
                                            distance = math.sqrt((existing_element[1][0] - x) ** 2 + (existing_element[1][1] - y) ** 2)

                                            # Ensure the distance is greater than the sum of radii
                                            if distance < max_radius * 2:
                                                # Adjust coordinates to prevent overlap
                                                angle = random.uniform(0, 2 * math.pi)
                                                x = existing_element[1][0] + ((max_radius + 30) * 2 + 1) * math.cos(angle)
                                                y = existing_element[1][1] + ((max_radius + 30) * 2 + 1) * math.sin(angle)
                                                break  # Stop checking for overlap once adjusted

                                        # Append the element with its coordinates to the list
                                        current_elements.append([element, [x, y], current_element_idx])
                                        current_element_idx += 1
                                    
                                    # current_connections = connections
                                else:
                                    log.error(
                                        "Parsing failed. Returning to file list."
                                    )
                                    break
                        else:
                            continue
                        break
            else:
                display_text(
                    "No files found", BLACK, screen.get_width() // 2 - 100, 200
                )

        # Activity screen
        elif current_screen == "activity":
            display_text(
                "Activity in progress. Press Escape to return to activity choice.", BLACK, screen.get_width() // 2 - 360, 50
            )

            # Display elements
            if current_elements:
                for element in current_elements:
                    x, y = element[1]
                    radius = 30 if element[0] == 'c' else 15
                    pygame.draw.circle(screen, GRAY, (x, y), radius)
                    display_text(element[0].capitalize(), BLACK, x - 10, y - 10)



            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if any circle is clicked
                    for element in current_elements:
                        x, y = element[1]
                        radius = 30 if element[0] == 'c' else 15
                        if (event.pos[0] - x) ** 2 + (event.pos[1] - y) ** 2 <= radius ** 2:
                            dragging = True
                            dragged_circle = element
                            offset_x = x - event.pos[0]
                            offset_y = y - event.pos[1]
                            break
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False

                    # Check for overlapping circles
                    for i, element1 in enumerate(current_elements):
                        for j, element2 in enumerate(current_elements[i + 1:], start=i + 1):
                            x1, y1 = element1[1]
                            x2, y2 = element2[1]
                            radius1 = 30 if element1[0] == 'c' else 15
                            radius2 = 30 if element2[0] == 'c' else 15

                            # Calculate distance between centers of circles
                            distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

                            # Check for overlap
                            if distance < radius1 + radius2:
                                # Move circles apart
                                overlap = radius1 + radius2 - distance
                                dx = (x2 - x1) * overlap / distance
                                dy = (y2 - y1) * overlap / distance
                                x1 -= dx / 2
                                y1 -= dy / 2
                                x2 += dx / 2
                                y2 += dy / 2

                                # Update positions of circles
                                current_elements[i][1] = [x1, y1]
                                current_elements[j][1] = [x2, y2]

                                # Store indices of circles involved in overlap
                                if (i, j) not in current_overlap_indices:
                                    current_overlap_indices.append((i, j))
                                # all_overlap_indices.extend(current_overlap_indices)

                                log.info(f'current overlap indices: {current_overlap_indices}')

                    # Redraw all circles after updating their positions
                    for element in current_elements:
                        x, y = element[1]
                        radius = 30 if element[0] == 'c' else 15
                        pygame.draw.circle(screen, GRAY, (x, y), radius)
                        display_text(element[0].capitalize(), BLACK, x - 10, y - 10)
                                
                    
                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        dragged_circle[1] = [event.pos[0] + offset_x, event.pos[1] + offset_y]

                # Handle Escape key press
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    escape_pressed = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    escape_pressed = False

            for i, j in current_overlap_indices:
                log.info('itt')
                x1, y1 = current_elements[i][1]
                x2, y2 = current_elements[j][1]
                pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 2)
                # pygame.draw.line(screen, BLACK, (100, 200), (300, 400), 2)



            # check win con
            # log.info(f'elements: {elements}')
            # log.info(f'current_elements: {current_elements}')
            # log.info(f'connections: {connections}')
            # log.info(f'current_overlap_indices: {current_overlap_indices}')
            # log.info(f'match? {are_equivalent(connections, current_overlap_indices)}')

            if are_equivalent(connections, current_overlap_indices):
                display_text("Congrats!", BLACK, screen.get_width() // 2 - 70, 100)                    

            if escape_pressed:
                current_screen = "activity_select"
                escape_pressed = False
                current_overlap_indices = []


                

        pygame.display.flip()
        # pygame.display.update()
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
