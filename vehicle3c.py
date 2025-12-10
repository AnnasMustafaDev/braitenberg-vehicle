# Wiring: Multisensorial. Behavior:
# Light (Yellow): Aggressive (Turns toward/attacks) -> Crossed Excitatory
# Temp (Red): Fear (Turns away) -> Uncrossed Excitatory
# Oxygen (Blue): Explorer (Likes but unstable) -> Crossed Inhibitory
# Organic (Green): Lover (Stays permanently) -> Uncrossed Inhibitory

# This code creates 4 different "source" objects on the screen. 
# The vehicle sums the inputs from all sensors to decide its movement.

import pygame
import math

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 3c: System of Values")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 14)

class Source:
    def __init__(self, x, y, type_name, color):
        self.x = x
        self.y = y
        self.type = type_name # 'light', 'temp', 'oxygen', 'organic'
        self.color = color
        self.radius = 25
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Label
        text = font.render(self.type[0].upper(), True, (0,0,0))
        surface.blit(text, (self.x-5, self.y-8))

class Vehicle3c:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.heading = 0
        self.color = (200, 200, 200) # Grey/Complex
        
        # Motors start at a base speed
        self.base_speed = 2.0
        self.max_speed = 6.0
        self.turning_scaler = 0.6
        self.sensor_dist = 25
        self.sensor_angle = math.radians(40)
        
        # Sensitivity settings for each sense
        self.sense_range = 350.0
        self.gain_excite = 3.0
        self.gain_inhibit = 2.5

    def _get_sensor_pos(self):
        lx = self.x + math.cos(self.heading + self.sensor_angle) * self.sensor_dist
        ly = self.y + math.sin(self.heading + self.sensor_angle) * self.sensor_dist
        rx = self.x + math.cos(self.heading - self.sensor_angle) * self.sensor_dist
        ry = self.y + math.sin(self.heading - self.sensor_angle) * self.sensor_dist
        return (lx, ly), (rx, ry)

    def calculate_intensity(self, sensor_x, sensor_y, source):
        dist = math.hypot(sensor_x - source.x, sensor_y - source.y)
        return max(0.0, 1.0 - (dist / self.sense_range))

    def update(self, sources):
        l_pos, r_pos = self._get_sensor_pos()
        
        # Initialize motor commands with base speed
        # We process all inputs cumulatively
        lm = self.base_speed
        rm = self.base_speed
        
        # Process every source in the environment
        for s in sources:
            # Calculate intensity for this specific source on Left/Right sensors
            i_l = self.calculate_intensity(l_pos[0], l_pos[1], s)
            i_r = self.calculate_intensity(r_pos[0], r_pos[1], s)
            
            # [cite_start]Apply wiring logic based on source type [cite: 28, 29]
            
            if s.type == 'light': 
                # AGGRESSION (Crossed Excitatory) - Destroys light
                lm += i_r * self.gain_excite
                rm += i_l * self.gain_excite
                
            elif s.type == 'temp':
                # FEAR (Uncrossed Excitatory) - Avoids heat
                lm += i_l * self.gain_excite
                rm += i_r * self.gain_excite
                
            elif s.type == 'oxygen':
                # EXPLORER (Crossed Inhibitory) - Likes O2 but drifts
                lm -= i_r * self.gain_inhibit
                rm -= i_l * self.gain_inhibit
                
            elif s.type == 'organic':
                # LOVER (Uncrossed Inhibitory) - Stays at organic
                lm -= i_l * self.gain_inhibit
                rm -= i_r * self.gain_inhibit

        # Clamp motors (cannot go below 0, optionally cap max speed)
        lm = max(0.0, min(self.max_speed, lm))
        rm = max(0.0, min(self.max_speed, rm))

        # Move
        speed = (lm + rm) / 2
        turn = (lm - rm) * self.turning_scaler
        
        self.heading += turn
        self.x += speed * math.cos(self.heading)
        self.y += speed * math.sin(self.heading)
        
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        nx = self.x + math.cos(self.heading) * self.radius
        ny = self.y + math.sin(self.heading) * self.radius
        pygame.draw.line(surface, (0,0,0), (self.x, self.y), (nx, ny), 2)
        
        # Draw sensor eyes
        l, r = self._get_sensor_pos()
        pygame.draw.circle(surface, (50,50,50), (int(l[0]), int(l[1])), 5)
        pygame.draw.circle(surface, (50,50,50), (int(r[0]), int(r[1])), 5)


# --- SETUP ---
# Create Sources
sources = [
    Source(200, 200, 'light', (255, 255, 0)),    # Yellow (Aggro target)
    Source(800, 200, 'temp', (255, 0, 0)),       # Red (Fear target)
    Source(200, 600, 'oxygen', (0, 100, 255)),   # Blue (Explorer target)
    Source(800, 600, 'organic', (0, 255, 0))     # Green (Lover target)
]

vehicle = Vehicle3c(WIDTH//2, HEIGHT//2)
dragging_source = None

running = True
while running:
    screen.fill((230, 230, 230))
    
    # Event Handling (Mouse drags sources)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for s in sources:
                if math.hypot(event.pos[0]-s.x, event.pos[1]-s.y) < s.radius:
                    dragging_source = s
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_source = None
        elif event.type == pygame.MOUSEMOTION and dragging_source:
            dragging_source.x, dragging_source.y = event.pos

    # Draw Sources
    for s in sources: s.draw(screen)

    # Update Vehicle
    vehicle.update(sources)
    vehicle.draw(screen)

    # UI Instructions
    ui = [
        "Vehicle 3c Logic:",
        "LIGHT (Yellow): Attacks (Crossed Excitatory)",
        "TEMP (Red): Flees (Uncrossed Excitatory)",
        "OXYGEN (Blue): Explores (Crossed Inhibitory)",
        "ORGANIC (Green): Loves (Uncrossed Inhibitory)",
        "Drag circles to move them!"
    ]
    for i, line in enumerate(ui):
        screen.blit(font.render(line, True, (0,0,0)), (10, 10 + i*20))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()