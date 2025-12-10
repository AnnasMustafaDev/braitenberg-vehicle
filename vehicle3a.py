import pygame
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 3a: The Lover")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 16)

class Vehicle3a:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.heading = 0
        self.color = (100, 100, 255) # Blue for "Cool/Detached"

        # TUNING
        self.base_speed = 3.0
        self.inhibition_scaler = 2.8 
        self.turning_scaler = 0.8
        self.light_max_distance = 400.0
        
        self.sensor_angle = math.radians(45)
        self.sensor_dist = 20

    def _get_sensor_pos(self):
        lx = self.x + math.cos(self.heading + self.sensor_angle) * self.sensor_dist
        ly = self.y + math.sin(self.heading + self.sensor_angle) * self.sensor_dist
        rx = self.x + math.cos(self.heading - self.sensor_angle) * self.sensor_dist
        ry = self.y + math.sin(self.heading - self.sensor_angle) * self.sensor_dist
        return (lx, ly), (rx, ry)

    def update(self, light_pos):
        l_pos, r_pos = self._get_sensor_pos()
        
        dist_l = math.hypot(l_pos[0] - light_pos[0], l_pos[1] - light_pos[1])
        dist_r = math.hypot(r_pos[0] - light_pos[0], r_pos[1] - light_pos[1])
        
        int_l = max(0.0, 1.0 - (dist_l / self.light_max_distance))
        int_r = max(0.0, 1.0 - (dist_r / self.light_max_distance))

        # --- LOGIC: CROSSED INHIBITORY ---
        # Left Sensor inhibits RIGHT Motor
        # Right Sensor inhibits LEFT Motor
        left_motor = max(0, self.base_speed - (int_r * self.inhibition_scaler))
        right_motor = max(0, self.base_speed - (int_l * self.inhibition_scaler))

        speed = (left_motor + right_motor) / 2
        turn = (left_motor - right_motor) * self.turning_scaler
        
        self.heading += turn
        self.x += speed * math.cos(self.heading)
        self.y += speed * math.sin(self.heading)
        
        self.x %= WIDTH
        self.y %= HEIGHT
        return int_l, int_r, left_motor, right_motor

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        l_pos, r_pos = self._get_sensor_pos()
        pygame.draw.circle(surface, (255,0,0), (int(l_pos[0]), int(l_pos[1])), 5)
        pygame.draw.circle(surface, (255,0,0), (int(r_pos[0]), int(r_pos[1])), 5)
        nx = self.x + math.cos(self.heading) * self.radius
        ny = self.y + math.sin(self.heading) * self.radius
        pygame.draw.line(surface, (0,0,0), (self.x, self.y), (nx, ny), 2)

# Main Loop
vehicle = Vehicle3a(WIDTH//2, HEIGHT//2)
light_pos = [WIDTH//2, HEIGHT//2]

running = True
while running:
    screen.fill((220, 220, 220))
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEMOTION: light_pos = event.pos

    pygame.draw.circle(screen, (255, 255, 0), light_pos, 30)
    
    il, ir, ml, mr = vehicle.update(light_pos)
    vehicle.draw(screen)

    info = f"Sensors: {il:.2f} / {ir:.2f} | Motors: {ml:.2f} / {mr:.2f}"
    screen.blit(font.render(info, True, (0,0,0)), (10, 10))
    screen.blit(font.render("3a: UNCROSSED INHIBITORY (Lover)", True, (0,0,0)), (10, 30))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()