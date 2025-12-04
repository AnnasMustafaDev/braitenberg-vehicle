import pygame
import math

pygame.init()

# Setup Pygame window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 2: Fear & Aggression")

# Setup clock for controlling frame rate
clock = pygame.time.Clock()
fps = 60

# Setup font for debug info
font = pygame.font.SysFont("consolas", 16)


# Vehicle Two
class VehicleTwo:
    def __init__(
        self,
        x,
        y,
        radius=20,
        heading=0,
        vehicle_type="2b",  # '2a' for Fear, '2b' for Aggression
        color=(0, 0, 255),
    ):
        # Vehicle state
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading  # Angle in radians
        self.vehicle_type = vehicle_type
        self.color = color

        # --- Controllable Tuning Variables ---
        # How much light intensity affects motor speed. Higher = more "excited"
        self.speed_scaler = 2.0
        # A minimum speed so the vehicle never stops
        self.base_speed = 1.0
        # How much motor difference affects turning. Higher = sharper turns
        self.turning_scaler = 0.8
        # The maximum distance the light source has an effect
        self.light_max_distance = 600.0
        # ----------------------------------------

        # Sensor configuration
        self.sensor_offset_angle = math.radians(45)  # Angle of sensors from center
        self.sensor_dist = self.radius  # Place sensors on the edge of the body

        # Debug/storage values
        self.intensity_left = 0.0
        self.intensity_right = 0.0
        self.forward_speed = 0.0
        self.turning_rate = 0.0

    # Calculate sensor positions based on vehicle position and heading
    def _sensor_positions(self):
        """Calculates the world coordinates of the left and right sensors."""
        angle = self.sensor_offset_angle
        distance = self.sensor_dist

        # Calculate x and y relative to vehicle center (local)
        left_local_x = math.cos(+angle) * distance
        left_local_y = math.sin(+angle) * distance
        right_local_x = math.cos(-angle) * distance
        right_local_y = math.sin(-angle) * distance

        # Rotate local coordinates by vehicle's heading to get world coordinates
        cos_heading = math.cos(self.heading)
        sin_heading = math.sin(self.heading)

        left_world_x = self.x + cos_heading * left_local_x - sin_heading * left_local_y
        left_world_y = self.y + sin_heading * left_local_x + cos_heading * left_local_y
        right_world_x = (
            self.x + cos_heading * right_local_x - sin_heading * right_local_y
        )
        right_world_y = (
            self.y + sin_heading * right_local_x + cos_heading * right_local_y
        )

        # Return sensor positions
        left_sensor_position = (left_world_x, left_world_y)
        right_sensor_position = (right_world_x, right_world_y)
        return left_sensor_position, right_sensor_position

    # Calculate intensity value of a particular source at a given point
    def _intensity_at(self, point_x, point_y, light_x, light_y):
        """
        Calculates light intensity at a point, based on distance.
        Returns a value between 0.0 (no light) and 1.0 (max light).
        """
        distance = math.hypot(point_x - light_x, point_y - light_y)

        # Use a linear falloff for stable, controllable behavior
        # Intensity is 1.0 at distance 0, and 0.0 at light_max_distance
        intensity = max(0.0, 1.0 - (distance / self.light_max_distance))
        
        # You could also use inverse-square law, but it's less stable
        # distance_sq = max(1.0, distance**2) # Avoid division by zero
        # intensity = 5000 / distance_sq # 5000 is arbitrary "light strength"
        # intensity = min(1.0, intensity) # Clamp to 1.0
        
        return intensity

    # Update sensor intensities based on light position(s)
    def update(self, light_pos):
        """Update the vehicle's state for one frame."""
        # Get sensor positions
        left_sensor, right_sensor = self._sensor_positions()

        # Calculate intensities at each sensor
        self.intensity_left = self._intensity_at(
            left_sensor[0], left_sensor[1], light_pos[0], light_pos[1]
        )
        self.intensity_right = self._intensity_at(
            right_sensor[0], right_sensor[1], light_pos[0], light_pos[1]
        )

        # --- This is the core logic for Vehicle 2a vs 2b ---
        
        if self.vehicle_type == "2a":  # FEAR (uncrossed)
            # Left sensor excites left motor
            # Right sensor excites right motor
            left_motor_speed = (
                self.base_speed + self.intensity_left * self.speed_scaler
            )
            right_motor_speed = (
                self.base_speed + self.intensity_right * self.speed_scaler
            )
        else:  # '2b' - AGGRESSION (crossed)
            # Left sensor excites right motor
            # Right sensor excites left motor
            left_motor_speed = (
                self.base_speed + self.intensity_right * self.speed_scaler
            )
            right_motor_speed = (
                self.base_speed + self.intensity_left * self.speed_scaler
            )

        # --- Vehicle Movement (Differential Steering) ---
        
        # Forward speed is the average of the two motors
        self.forward_speed = (left_motor_speed + right_motor_speed) / 2.0
        
        # Turning rate is based on the *difference* between motors
        # (Positive = turn left, Negative = turn right)
        # We use (left - right) because Pygame's Y-axis is inverted
        self.turning_rate = (
            (left_motor_speed - right_motor_speed) * self.turning_scaler
        )

        # Update vehicle position and heading
        self.heading += self.turning_rate
        self.x += self.forward_speed * math.cos(self.heading)
        self.y += self.forward_speed * math.sin(self.heading)

        # Wrap around screen edges
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface, debug_pos=(10, 10)):
        """Draw the vehicle and its debug info."""
        # Draw vehicle body
        pygame.draw.circle(
            surface, self.color, (int(self.x), int(self.y)), self.radius
        )
        pygame.draw.circle(
            surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2
        )

        # Draw "nose" line to show heading
        nose_x = self.x + self.radius * math.cos(self.heading)
        nose_y = self.y + self.radius * math.sin(self.heading)
        pygame.draw.line(
            surface, (0, 0, 0), (int(self.x), int(self.y)), (int(nose_x), int(nose_y)), 3
        )

        # Draw sensors
        left_sensor, right_sensor = self._sensor_positions()
        # Draw sensor intensity (red circle size)
        pygame.draw.circle(
            surface,
            (255, 0, 0),
            (int(left_sensor[0]), int(left_sensor[1])),
            int(2 + self.intensity_left * 6),
        )
        pygame.draw.circle(
            surface,
            (255, 0, 0),
            (int(right_sensor[0]), int(right_sensor[1])),
            int(2 + self.intensity_right * 6),
        )

        # Optionally draw debug info
        if font:
            label = "FEAR (2a)" if self.vehicle_type == "2a" else "AGGRESSION (2b)"
            surface.blit(
                font.render(
                    f"Vehicle: {label}",
                    True,
                    (0, 0, 0),
                ),
                debug_pos,
            )
            surface.blit(
                font.render(
                    f"Speed={self.forward_speed:.1f} Turn={self.turning_rate:.2f}",
                    True,
                    (0, 0, 0),
                ),
                (debug_pos[0], debug_pos[1] + 20),
            )
            surface.blit(
                font.render(
                    f"L.Int={self.intensity_left:.2f} R.Int={self.intensity_right:.2f}",
                    True,
                    (0, 0, 0),
                ),
                (debug_pos[0], debug_pos[1] + 40),
            )


# Light source
class Light:
    def __init__(self, x, y, radius=10):
        self.x, self.y = x, y
        self.radius = radius

    def move_light(self, new_position):
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


# CREATE instances of vehicles and light sources
light = Light(WIDTH // 2, HEIGHT // 2, radius=20)

# Create one of each vehicle type
vehicle_fear = VehicleTwo(
    WIDTH // 2 - 150,
    HEIGHT // 2,
    radius=20,
    vehicle_type="2a",
    color=(60, 100, 255),  # Blue
)
vehicle_aggro = VehicleTwo(
    WIDTH // 2 + 150,
    HEIGHT // 2,
    radius=20,
    vehicle_type="2b",
    color=(60, 200, 100),  # Green
)


running = True
while running:
    screen.fill((220, 220, 220))  # Light gray background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Move light with mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            light.move_light(event.pos)
        # Also move light with mouse drag
        if event.type == pygame.MOUSEMOTION and event.buttons[0]:
             light.move_light(event.pos)

    # Draw light source(s)
    light.draw(screen)

    # Update and draw vehicles
    vehicle_fear.update(light.pos())
    vehicle_fear.draw(screen, debug_pos=(10, 10))

    vehicle_aggro.update(light.pos())
    vehicle_aggro.draw(screen, debug_pos=(10, 70))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()