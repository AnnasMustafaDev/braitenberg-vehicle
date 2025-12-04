# MODIFIED: This code will use pygame-ce if it's installed
import pygame
import math
import random

# --- Pygame Setup (No changes here) ---
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# MODIFIED: Updated caption
pygame.display.set_caption("Two Vehicles, Two Sources (Pygame-ce)")
clock = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont("consolas", 16)


class VehicleOne:
    # MODIFIED: Added 'color' as an initialization parameter
    def __init__(self, x, y, radius=20, heading=0, max_perturbation=math.radians(1.0), color=(128, 128, 128)):
        # Vehicle state
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.intensity = 0  # Store current intensity
        self.speed = 0      # Store current speed
        self.turning_rate = 0 # Store current turning rate
        
        # MODIFIED: Store the vehicle's color
        self.color = color
        
        self.max_perturbation = max_perturbation

        # Sensor configuration
        self.sensor_dist = self.radius

    # Calculate sensor position based on vehicle position and heading
    def _sensor_position(self):
        # Calculate sensor position relative to world
        sensor_x = self.x + math.cos(self.heading) * self.sensor_dist
        sensor_y = self.y + math.sin(self.heading) * self.sensor_dist
        return (sensor_x, sensor_y)

    # Calculate intensity value of a particular source at a given point
    def _intensity_at(self, point_x, point_y, source_x, source_y):
        distance = math.dist((point_x, point_y), (source_x, source_y))
        # Using inverse-square law
        intensity = 10000 / (distance**2 + 50)
        return intensity

    # MODIFIED: Update now accepts a LIST of source positions
    def update(self, source_positions):
        # Get sensor position
        sensor_pos = self._sensor_position()

        # MODIFIED: Calculate total intensity by summing all sources
        total_intensity = 0
        for source_pos in source_positions:
            total_intensity += self._intensity_at(
                sensor_pos[0], sensor_pos[1], source_pos[0], source_pos[1]
            )
        self.intensity = total_intensity

        # Motor logic for Vehicle 1
        self.speed = self.intensity  # Direct connection!

        # Vehicle 1 has perturbation (Brownian motion)
        self.turning_rate = random.uniform(-self.max_perturbation, self.max_perturbation)

        # Update vehicle position and heading
        self.heading += self.turning_rate
        self.x += self.speed * math.cos(self.heading)
        self.y += self.speed * math.sin(self.heading)

        # Wrap around the screen
        self.x %= WIDTH
        self.y %= HEIGHT

    # MODIFIED: Added 'info_y_offset' to prevent debug text overlap
    def draw(self, surface, info_y_offset=10):
        # Draw vehicle body
        pygame.draw.circle(
            # MODIFIED: Use the stored self.color
            surface, self.color, (int(self.x), int(self.y)), self.radius
        )
        pygame.draw.circle(
            surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2
        )

        # Draw the single sensor
        sensor_pos = self._sensor_position()
        pygame.draw.circle(
            surface, (255, 0, 0), (int(sensor_pos[0]), int(sensor_pos[1])), 5
        )

        # Optionally draw debug info
        if font:
            # MODIFIED: All debug text now uses the info_y_offset
            surface.blit(
                font.render(
                    f"Speed={self.speed:.2f}",
                    True,
                    (0, 0, 0),
                ),
                (10, info_y_offset),
            )
            surface.blit(
                font.render(
                    f"Intensity={self.intensity:.2f}",
                    True,
                    (0, 0, 0),
                ),
                (10, info_y_offset + 20),
            )
            # surface.blit(
            #     font.render(
            #         f"Turning={math.degrees(self.turning_rate):.2f} deg/f", # Show turning in degrees
            #         True,
            #         (0, 0, 0),
            #     ),
            #     (10, info_y_offset + 40),
            # )


# Renamed Light to Source
class Source:
    def __init__(self, x, y, radius=10):
        self.x, self.y = x, y
        self.radius = radius

    def move_source(self, new_position):
        self.x, self.y = new_position

    def pos(self):
        return (self.x, self.y)

    def draw(self, surface):
        pygame.draw.circle(
            surface, (255, 255, 0), (int(self.x), int(self.y)), self.radius
        )
        pygame.draw.circle(
            surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2
        )


# MODIFIED: Create lists for multiple sources and vehicles
sources = [
    Source(WIDTH // 3, HEIGHT // 2, radius=15),
    Source(WIDTH * 2 // 3, HEIGHT // 2, radius=15)
]

vehicles = [
    VehicleOne(
        WIDTH // 2 - 150, 
        HEIGHT // 2, 
        radius=20, 
        max_perturbation=math.radians(1.0),
        color=(100, 100, 100)  # Dark Grey
    ),
    VehicleOne(
        WIDTH // 2 + 150, 
        HEIGHT // 2, 
        radius=20,
        heading=math.pi, # Start facing left
        max_perturbation=math.radians(2.5), # More erratic
        color=(180, 180, 180)  # Light Grey
    )
]

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # MODIFIED: Move sources with the mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left-click
                sources[0].move_source(event.pos)
                print("Left-click: Moved source 1")
            elif event.button == 3: # Right-click
                sources[1].move_source(event.pos)
                print("Right-click: Moved source 2")


    # MODIFIED: Draw all sources
    for source in sources:
        source.draw(screen)

    # MODIFIED: Get a list of all source positions
    source_positions = [s.pos() for s in sources]
    
    # MODIFIED: Update and draw all vehicles
    info_display_offset = 10
    for vehicle in vehicles:
        vehicle.update(source_positions)
        # Pass the offset so debug text doesn't overlap
        vehicle.draw(screen, info_display_offset)
        info_display_offset += 70 # Increment offset for the next vehicle

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()