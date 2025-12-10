import pygame
import math

pygame.init()
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 4a: Special Tastes (The Orbiter)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 16)

class Vehicle4a:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.heading = 0
        self.color = (255, 100, 255)
        
        # SENSORS
        self.sensor_angle = math.radians(45)
        self.sensor_dist = 25
        
        # TUNING THE "TASTE" - Bell Curve Parameters
        self.preferred_intensity = 0.5 
        self.curve_width = 0.2
        self.max_motor_speed = 4.0
        self.base_speed = 2.0  # Constant base movement

    def _get_sensor_pos(self):
        lx = self.x + math.cos(self.heading + self.sensor_angle) * self.sensor_dist
        ly = self.y + math.sin(self.heading + self.sensor_angle) * self.sensor_dist
        rx = self.x + math.cos(self.heading - self.sensor_angle) * self.sensor_dist
        ry = self.y + math.sin(self.heading - self.sensor_angle) * self.sensor_dist
        return (lx, ly), (rx, ry)

    def gaussian(self, intensity):
        """
        Bell curve: Returns max value (1.0) when intensity matches preferred.
        Returns lower values when intensity is too high OR too low.
        """
        diff = intensity - self.preferred_intensity
        numerator = -(diff * diff)
        denominator = 2 * (self.curve_width * self.curve_width)
        return math.exp(numerator / denominator)

    def update(self, light_pos):
        l_pos, r_pos = self._get_sensor_pos()
        
        # Calculate distance and intensity for each sensor
        dist_l = math.hypot(l_pos[0] - light_pos[0], l_pos[1] - light_pos[1])
        dist_r = math.hypot(r_pos[0] - light_pos[0], r_pos[1] - light_pos[1])
        
        # Raw intensity (1.0 = very close, 0.0 = far away)
        raw_l = max(0.0, 1.0 - (dist_l / 500.0))
        raw_r = max(0.0, 1.0 - (dist_r / 500.0))
        
        # Apply Gaussian bell curve transformation
        val_l = self.gaussian(raw_l)
        val_r = self.gaussian(raw_r)

        # VEHICLE 4a WIRING: Uncrossed connections
        # Each sensor drives its corresponding motor through bell curve
        # Left sensor -> Left motor (via gaussian)
        # Right sensor -> Right motor (via gaussian)
        left_motor = self.base_speed + (val_l * self.max_motor_speed)
        right_motor = self.base_speed + (val_r * self.max_motor_speed)

        # Differential drive physics
        avg_speed = (left_motor + right_motor) / 2
        # Angular velocity from motor difference
        angular_vel = (right_motor - left_motor) * 0.12
        
        # Update heading and position
        self.heading += angular_vel
        self.x += avg_speed * math.cos(self.heading)
        self.y += avg_speed * math.sin(self.heading)
        
        # Wrap around edges
        self.x %= WIDTH
        self.y %= HEIGHT
        
        return raw_l, raw_r, left_motor, right_motor, val_l, val_r

    def draw(self, surface):
        # Body
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Sensors
        l, r = self._get_sensor_pos()
        pygame.draw.circle(surface, (200,0,0), (int(l[0]), int(l[1])), 6)
        pygame.draw.circle(surface, (200,0,0), (int(r[0]), int(r[1])), 6)
        
        # Direction indicator (nose)
        nx = self.x + math.cos(self.heading) * self.radius
        ny = self.y + math.sin(self.heading) * self.radius
        pygame.draw.line(surface, (0,0,0), (self.x, self.y), (nx, ny), 3)

# --- MAIN LOOP ---
vehicle = Vehicle4a(200, 350)
light_pos = [WIDTH//2, HEIGHT//2]

running = True
paused = False

while running:
    screen.fill((240, 240, 240))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        if event.type == pygame.MOUSEMOTION: 
            light_pos = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click - teleport vehicle
                import random
                vehicle.x = random.randint(100, WIDTH-100)
                vehicle.y = random.randint(100, HEIGHT-100)
                vehicle.heading = random.uniform(0, 2*math.pi)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    # Draw light source
    pygame.draw.circle(screen, (255, 255, 0), light_pos, 30)
    pygame.draw.circle(screen, (255, 200, 0), light_pos, 30, 3)
    
    # Draw "sweet spot" orbit ring (where intensity ≈ 0.5)
    # At 250px distance, intensity = 0.5
    pygame.draw.circle(screen, (100, 255, 100), light_pos, 250, 3)
    
    # Draw weaker orbit rings for reference
    pygame.draw.circle(screen, (200, 200, 200), light_pos, 150, 1)
    pygame.draw.circle(screen, (200, 200, 200), light_pos, 350, 1)

    if not paused:
        # Update vehicle
        rl, rr, lm, rm, vl, vr = vehicle.update(light_pos)
    else:
        # Get values without moving
        l_pos, r_pos = vehicle._get_sensor_pos()
        dist_l = math.hypot(l_pos[0] - light_pos[0], l_pos[1] - light_pos[1])
        dist_r = math.hypot(r_pos[0] - light_pos[0], r_pos[1] - light_pos[1])
        rl = max(0.0, 1.0 - (dist_l / 500.0))
        rr = max(0.0, 1.0 - (dist_r / 500.0))
        vl = vehicle.gaussian(rl)
        vr = vehicle.gaussian(rr)
        lm = vehicle.base_speed + (vl * vehicle.max_motor_speed)
        rm = vehicle.base_speed + (vr * vehicle.max_motor_speed)
    
    vehicle.draw(screen)

    # Calculate distance to light
    dist_to_light = math.hypot(vehicle.x - light_pos[0], vehicle.y - light_pos[1])
    avg_intensity = (rl + rr) / 2

    # UI / Debug Info
    ui_text = [
        "Vehicle 4a: 'Special Tastes' - Figure 6 Behavior",
        "Wiring: UNCROSSED (direct) + Gaussian Bell Curve",
        "Sweet Spot: 250px (green ring) where intensity = 0.5",
        f"Distance to light: {dist_to_light:.0f}px | Avg Intensity: {avg_intensity:.2f}",
        "",
        f"Left:  Raw={rl:.2f} → Gauss={vl:.2f} → Motor={lm:.2f}",
        f"Right: Raw={rr:.2f} → Gauss={vr:.2f} → Motor={rm:.2f}",
        "",
        "Controls:",
        "• Move mouse = move light source",
        "• Click = teleport vehicle to random position",
        "• SPACE = pause/unpause"
    ]
    
    y_offset = 10
    for line in ui_text:
        if line == "":
            y_offset += 10
        else:
            text_surface = font.render(line, True, (0,0,0))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 20

    # Draw Gaussian curve visualization
    curve_x, curve_y = WIDTH - 220, 20
    curve_w, curve_h = 200, 100
    
    pygame.draw.rect(screen, (255, 255, 255), (curve_x, curve_y, curve_w, curve_h))
    pygame.draw.rect(screen, (0, 0, 0), (curve_x, curve_y, curve_w, curve_h), 1)
    
    # Draw bell curve
    for i in range(curve_w):
        intensity = i / curve_w
        gauss_val = vehicle.gaussian(intensity)
        px = curve_x + i
        py = curve_y + curve_h - (gauss_val * curve_h)
        pygame.draw.circle(screen, (255, 0, 255), (int(px), int(py)), 1)
    
    # Mark preferred intensity
    pref_x = curve_x + int(vehicle.preferred_intensity * curve_w)
    pygame.draw.line(screen, (0, 255, 0), (pref_x, curve_y), (pref_x, curve_y + curve_h), 2)
    
    # Mark current avg intensity
    curr_x = curve_x + int(avg_intensity * curve_w)
    pygame.draw.line(screen, (255, 0, 0), (curr_x, curve_y), (curr_x, curve_y + curve_h), 1)
    
    label = font.render("Gaussian Response", True, (0,0,0))
    screen.blit(label, (curve_x + 5, curve_y + 5))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()