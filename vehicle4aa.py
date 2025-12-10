import pygame 
import random
import math

# --- 1. SETUP ---
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Consolas', 20)

# --- 2. CONSTANTS ---
FPS = 60 
SCREEN_COLOR = (10, 10, 30)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255) # Vehicle color

# --- VEHICLE 4a PARAMETERS ---
# Peak speed happens at this distance (The "Sweet Spot")
OPTIMAL_DISTANCE = 250.0 
# How wide the "bell curve" of preference is
CURVE_WIDTH = 100.0 
# The maximum speed the vehicle reaches at the sweet spot
MAX_SPEED = 5.0 

# Steering sensitivity
TURN_SENSITIVITY = 0.05


class Source:
    def __init__(self, position, radius, color):
        self.position = pygame.math.Vector2(position)
        self.radius = radius
        self.color = color
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        
        # Draw the "Sweet Spot" ring (where speed is highest)
        # This helps you visualize the non-linear logic
        pygame.draw.circle(surface, (100, 100, 100), self.position, int(OPTIMAL_DISTANCE), 2)
        label = font.render("Peak Speed Zone", True, (150, 150, 150))
        surface.blit(label, self.position + pygame.math.Vector2(-60, -OPTIMAL_DISTANCE - 25))


class Vehicle():
    """Vehicle 4a: Non-Linear 'Bell Curve' Logic."""
    def __init__(self, position, angle):
        self.position = pygame.math.Vector2(position)
        self.angle = angle
        self.color = MAGENTA
        self.radius = 30
        
        self.sensor_distance = 40 
        self.wheel_distance = 30 

        self.speed_L = 0.0
        self.speed_R = 0.0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        end_point = self.position + pygame.math.Vector2(0, -self.radius).rotate(self.angle)
        pygame.draw.line(surface, (255, 255, 255), self.position, end_point, 3)

        # Sensors
        s_L = self._get_sensor_pos(-1)
        s_R = self._get_sensor_pos(1)
        pygame.draw.circle(surface, (0, 255, 0), s_L, 8)
        pygame.draw.circle(surface, (0, 255, 0), s_R, 8)

    def _get_sensor_pos(self, side):
        rel = pygame.math.Vector2(side * self.wheel_distance, -self.sensor_distance)
        return self.position + rel.rotate(self.angle)

    def _gaussian_activation(self, distance):
        """
        The Brain of Vehicle 4a: A Bell Curve.
        Input: Distance
        Output: Speed (Low -> High -> Low)
        """
        # A standard Gaussian formula: e^( - (x - center)^2 / width )
        # This creates a "hill" that peaks when distance == OPTIMAL_DISTANCE
        delta = distance - OPTIMAL_DISTANCE
        activation = math.exp(-(delta**2) / (2 * CURVE_WIDTH**2))
        return activation * MAX_SPEED

    def move_and_think(self, source):
        # 1. SENSE
        sensor_L = self._get_sensor_pos(-1)
        sensor_R = self._get_sensor_pos(1)
        
        dist_L = sensor_L.distance_to(source.position)
        dist_R = sensor_R.distance_to(source.position)
        
        # 2. THINK (Non-Linear / Special Tastes)
        # Instead of 1/distance, we use the Bell Curve function
        speed_signal_L = self._gaussian_activation(dist_L)
        speed_signal_R = self._gaussian_activation(dist_R)

        # Wiring: Crossed (Like Aggressor 2b)
        # Why Crossed? So it turns TOWARD the source to find the sweet spot.
        # Left Sensor -> Right Motor
        # Right Sensor -> Left Motor
        self.speed_L = speed_signal_R
        self.speed_R = speed_signal_L
        
        # 3. STEER & MOVE
        diff = self.speed_L - self.speed_R # Left faster -> Turn Right (Toward)
        self.angle += diff * 5.0 # Higher multiplier for sharper reactions
        
        avg_speed = (self.speed_L + self.speed_R) / 2
        
        move_vector = pygame.math.Vector2(0, -1).rotate(self.angle)
        self.position += move_vector * avg_speed

        # Screen Wrap
        if self.position.x < 0: self.position.x = WIDTH
        if self.position.x > WIDTH: self.position.x = 0
        if self.position.y < 0: self.position.y = HEIGHT
        if self.position.y > HEIGHT: self.position.y = 0


# --- GAME LOOP ---
source = Source(position=(WIDTH / 2, HEIGHT / 2), radius=40, color=YELLOW)
vehicle = Vehicle(position=(100, 100), angle=135) 

running = True
dragging_source = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.math.Vector2(event.pos)
            if source.position.distance_to(mouse_pos) < source.radius:
                dragging_source = source
        if event.type == pygame.MOUSEBUTTONUP:
            dragging_source = None
            
    if dragging_source:
        dragging_source.position = pygame.math.Vector2(pygame.mouse.get_pos())

    vehicle.move_and_think(source)
    
    screen.fill(SCREEN_COLOR)
    source.draw(screen)
    vehicle.draw(screen)
    
    # Debug
    dist = vehicle.position.distance_to(source.position)
    # Visual bar for speed
    bar_width = (vehicle.speed_L + vehicle.speed_R) * 20
    pygame.draw.rect(screen, (0, 255, 0), (10, 40, bar_width, 20))
    
    text_dist = f"Distance: {dist:.0f} (Target: {OPTIMAL_DISTANCE:.0f})"
    text_speed = f"Current Speed: {(vehicle.speed_L + vehicle.speed_R)/2:.2f}"
    
    screen.blit(font.render(text_dist, True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(text_speed, True, (255, 255, 255)), (10, 70))
    screen.blit(font.render("Speed peaks at the grey circle!", True, (150, 150, 150)), (10, 100))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()