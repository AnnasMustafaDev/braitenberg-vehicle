import pygame
import math

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 4b: ReLU Logic & Decisions")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 16)
bold_font = pygame.font.SysFont("consolas", 16, bold=True)

# --- COLORS ---
BG_COLOR = (20, 20, 30)  # Dark background to make lights pop
VEHICLE_COLOR = (200, 200, 255)
SENSOR_COLOR = (150, 150, 150)
LIGHT_SOURCE_COLOR = (255, 200, 50)
THRESHOLD_RING_COLOR = (255, 50, 50)

# --- VEHICLE CLASS ---
class Vehicle4b_ReLU:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.heading = 0  # Radians
        
        # SENSOR SETUP
        self.sensor_angle = math.radians(40)
        self.sensor_dist = 25
        
        # --- BRAIN: ReLU PARAMETERS ---
        # The threshold determines "When to make a decision"
        # 0.4 means it ignores light until it's 40% intense
        self.relu_threshold = 0.4  
        
        # The gain determines "How strong is the will to act"
        self.relu_gain = 8.0       
        
        self.max_speed = 6.0
        
        # STATUS FOR LIGHTS (Left Motor, Right Motor)
        self.status_left = False # False = Stopped (Red), True = Moving (Green)
        self.status_right = False

    def _get_sensor_pos(self):
        # Calculate positions of left and right sensors
        lx = self.x + math.cos(self.heading + self.sensor_angle) * self.sensor_dist
        ly = self.y + math.sin(self.heading + self.sensor_angle) * self.sensor_dist
        rx = self.x + math.cos(self.heading - self.sensor_angle) * self.sensor_dist
        ry = self.y + math.sin(self.heading - self.sensor_angle) * self.sensor_dist
        return (lx, ly), (rx, ry)

    def relu_activation(self, intensity):
        """
        The ReLU-like (Rectified Linear Unit) Function.
        Acts as a 'shifted' ReLU. 
        f(x) = max(0, (x - threshold) * gain)
        """
        if intensity <= self.relu_threshold:
            return 0.0  # Cutoff (Pondering/Ignoring)
        else:
            return (intensity - self.relu_threshold) * self.relu_gain

    def update(self, light_pos):
        l_pos, r_pos = self._get_sensor_pos()
        
        # 1. CALCULATE INPUT INTENSITY (Inverse Linear Distance)
        # Max sensing distance is 600px
        max_dist = 600.0
        dist_l = math.hypot(l_pos[0] - light_pos[0], l_pos[1] - light_pos[1])
        dist_r = math.hypot(r_pos[0] - light_pos[0], r_pos[1] - light_pos[1])
        
        raw_l = max(0.0, 1.0 - (dist_l / max_dist))
        raw_r = max(0.0, 1.0 - (dist_r / max_dist))
        
        # 2. APPLY ReLU ACTIVATION (The "Decision")
        val_l = self.relu_activation(raw_l)
        val_r = self.relu_activation(raw_r)
        
        # Update Status Lights (Visualizing the internal state)
        self.status_left = val_l > 0
        self.status_right = val_r > 0

        # 3. MOTOR MAPPING (Crossed Connections = Aggression)
        # Left Sensor -> Right Motor
        # Right Sensor -> Left Motor
        motor_l = val_r
        motor_r = val_l

        # Clamp max speed
        motor_l = min(self.max_speed, motor_l)
        motor_r = min(self.max_speed, motor_r)

        # 4. PHYSICS UPDATE
        speed = (motor_l + motor_r) / 2
        
        # Turning: difference between motors
        turn = (motor_l - motor_r) * 0.15
        
        self.heading += turn
        self.x += speed * math.cos(self.heading)
        self.y += speed * math.sin(self.heading)
        
        # Screen wrap
        self.x %= WIDTH
        self.y %= HEIGHT
        
        return raw_l, raw_r, motor_l, motor_r

    def draw(self, surface):
        # Draw Body
        pygame.draw.circle(surface, VEHICLE_COLOR, (int(self.x), int(self.y)), self.radius)
        
        # Draw Sensors
        l_pos, r_pos = self._get_sensor_pos()
        pygame.draw.circle(surface, SENSOR_COLOR, (int(l_pos[0]), int(l_pos[1])), 6)
        pygame.draw.circle(surface, SENSOR_COLOR, (int(r_pos[0]), int(r_pos[1])), 6)
        
        # Draw Nose Line
        nose_x = self.x + math.cos(self.heading) * self.radius
        nose_y = self.y + math.sin(self.heading) * self.radius
        pygame.draw.line(surface, (0,0,0), (self.x, self.y), (nose_x, nose_y), 3)

        # --- DRAW STATUS LIGHTS (The "Brain" Visualization) ---
        # Left status light (represents left motor activation)
        color_l = (0, 255, 0) if self.status_left else (100, 0, 0) # Green vs Dim Red
        # Right status light
        color_r = (0, 255, 0) if self.status_right else (100, 0, 0)
        
        # Position lights on the rear of the vehicle
        rear_angle = self.heading + math.pi
        off_ang = 0.5
        lx = self.x + math.cos(rear_angle - off_ang) * 15
        ly = self.y + math.sin(rear_angle - off_ang) * 15
        rx = self.x + math.cos(rear_angle + off_ang) * 15
        ry = self.y + math.sin(rear_angle + off_ang) * 15
        
        pygame.draw.circle(surface, (0,0,0), (int(lx), int(ly)), 6) # Bezel
        pygame.draw.circle(surface, color_l, (int(lx), int(ly)), 4) # Light
        
        pygame.draw.circle(surface, (0,0,0), (int(rx), int(ry)), 6) # Bezel
        pygame.draw.circle(surface, color_r, (int(rx), int(ry)), 4) # Light


# --- MAIN SETUP ---
vehicle = Vehicle4b_ReLU(100, 100)
light_pos = [WIDTH//2, HEIGHT//2]

running = True
while running:
    screen.fill(BG_COLOR)
    
    # --- EVENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        # Move light source
        if event.type == pygame.MOUSEMOTION:
            if event.buttons[0]: # Click and drag
                light_pos = list(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            light_pos = list(event.pos)

    # --- DRAW LIGHT SOURCE & THRESHOLD BOUNDARY ---
    pygame.draw.circle(screen, LIGHT_SOURCE_COLOR, light_pos, 25)
    
    # CALCULATE VISUAL THRESHOLD RING
    # If threshold is 0.4, that means distance is (1 - 0.4) * max_dist = 0.6 * 600 = 360
    # The vehicle will only react if it enters this circle.
    thresh_px = (1.0 - vehicle.relu_threshold) * 600.0
    pygame.draw.circle(screen, THRESHOLD_RING_COLOR, light_pos, int(thresh_px), 2)
    
    # Draw Label for Threshold
    label = font.render("DECISION BOUNDARY (ReLU Threshold)", True, THRESHOLD_RING_COLOR)
    screen.blit(label, (light_pos[0] - 100, light_pos[1] + int(thresh_px) + 10))

    # --- UPDATE & DRAW VEHICLE ---
    raw_l, raw_r, mot_l, mot_r = vehicle.update(light_pos)
    vehicle.draw(screen)

    # --- UI / TELEMETRY ---
    # Display the math
    ui_y = 10
    
    lines = [
        ("VEHICLE 4b: RELU ACTIVATION", (255, 255, 255)),
        (f"ReLU Threshold: {vehicle.relu_threshold}", (200, 200, 200)),
        (f"Input Left: {raw_l:.2f} -> ReLU -> Motor Right: {mot_r:.2f}", (200, 255, 200) if mot_r > 0 else (255, 100, 100)),
        (f"Input Right: {raw_r:.2f} -> ReLU -> Motor Left:  {mot_l:.2f}", (200, 255, 200) if mot_l > 0 else (255, 100, 100)),
        ("--------------------------------", (255,255,255)),
        ("RED LIGHTS  = 'Pondering' (Input < Threshold)", (255, 100, 100)),
        ("GREEN LIGHTS = 'Decided'   (Input > Threshold)", (100, 255, 100)),
    ]
    
    for text, color in lines:
        surf = font.render(text, True, color)
        screen.blit(surf, (10, ui_y))
        ui_y += 20

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# import pygame
# import math

# pygame.init()
# WIDTH, HEIGHT = 900, 700
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Vehicle 4b: Decisions (The Ponderer)")
# clock = pygame.time.Clock()
# font = pygame.font.SysFont("consolas", 16)

# class Vehicle4b:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#         self.radius = 20
#         self.heading = 0
#         self.color = (100, 0, 150) # Dark Purple/Mysterious
        
#         # SENSORS
#         self.sensor_angle = math.radians(45)
#         self.sensor_dist = 20
        
#         # TUNING THE "DECISION"
#         # The vehicle ignores everything below this intensity.
#         self.threshold = 0.35 
        
#         # Once threshold is met, how fast does it go?
#         self.activation_speed = 4.0 
        
#         # Friction/Minimum activation cost logic
#         self.base_speed = 0.0 # It truly stops when below threshold

#     def _get_sensor_pos(self):
#         lx = self.x + math.cos(self.heading + self.sensor_angle) * self.sensor_dist
#         ly = self.y + math.sin(self.heading + self.sensor_angle) * self.sensor_dist
#         rx = self.x + math.cos(self.heading - self.sensor_angle) * self.sensor_dist
#         ry = self.y + math.sin(self.heading - self.sensor_angle) * self.sensor_dist
#         return (lx, ly), (rx, ry)

#     def threshold_func(self, intensity):
#         """
#         Step function logic.
#         If below threshold -> Output 0
#         If above threshold -> Output increases rapidly
#         """
#         if intensity < self.threshold:
#             return 0.0
#         else:
#             # Linear increase after threshold
#             # (intensity - threshold) scales the remaining range
#             return self.activation_speed * (intensity - self.threshold) * 2.0

#     def update(self, light_pos):
#         l_pos, r_pos = self._get_sensor_pos()
        
#         # Max detection distance 600px
#         max_dist = 600.0
#         dist_l = math.hypot(l_pos[0] - light_pos[0], l_pos[1] - light_pos[1])
#         dist_r = math.hypot(r_pos[0] - light_pos[0], r_pos[1] - light_pos[1])
        
#         raw_l = max(0.0, 1.0 - (dist_l / max_dist))
#         raw_r = max(0.0, 1.0 - (dist_r / max_dist))
        
#         # --- VEHICLE 4b LOGIC: THRESHOLDS ---
#         # We use CROSSED connections here (Fear/Aggression wiring)
#         # But gated by the threshold.
        
#         val_l = self.threshold_func(raw_l)
#         val_r = self.threshold_func(raw_r)

#         # CROSSED wiring: Left sensor drives Right motor
#         left_motor = val_r 
#         right_motor = val_l 

#         # If motors are below a tiny value, clamp to 0 (Simulate Friction)
#         if left_motor < 0.1: left_motor = 0
#         if right_motor < 0.1: right_motor = 0

#         # Movement
#         speed = (left_motor + right_motor) / 2
#         turn = (left_motor - right_motor) * 0.6
        
#         self.heading += turn
#         self.x += speed * math.cos(self.heading)
#         self.y += speed * math.sin(self.heading)
        
#         self.x %= WIDTH
#         self.y %= HEIGHT
        
#         return raw_l, raw_r, left_motor, right_motor

#     def draw(self, surface):
#         # Draw body
#         pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
#         # Draw status light on body: Green if moving, Red if "thinking"
#         status_color = (0, 255, 0) if (self.last_speed > 0) else (255, 0, 0)
#         pygame.draw.circle(surface, status_color, (int(self.x), int(self.y)), 8)

#         # Draw Sensors
#         l, r = self._get_sensor_pos()
#         pygame.draw.circle(surface, (200,200,200), (int(l[0]), int(l[1])), 5)
#         pygame.draw.circle(surface, (200,200,200), (int(r[0]), int(r[1])), 5)
        
#         # Nose
#         nx = self.x + math.cos(self.heading) * self.radius
#         ny = self.y + math.sin(self.heading) * self.radius
#         pygame.draw.line(surface, (0,0,0), (self.x, self.y), (nx, ny), 2)

# # --- MAIN LOOP ---
# vehicle = Vehicle4b(100, 100)
# vehicle.last_speed = 0 # Helper for visual status
# light_pos = [WIDTH//2, HEIGHT//2]

# running = True
# while running:
#     screen.fill((220, 220, 235))
    
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT: running = False
#         if event.type == pygame.MOUSEMOTION: light_pos = event.pos
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             vehicle.x, vehicle.y = 100, 100 # Reset position

#     # Draw Light Source
#     pygame.draw.circle(screen, (255, 200, 0), light_pos, 30)
#     # Draw Threshold Boundary (Visual guide where Activation happens)
#     # Detection limit is 600, Threshold is 0.35.
#     # 0.35 intensity means distance is roughly (1 - 0.35) * 600 = 390
#     pygame.draw.circle(screen, (255, 0, 0), light_pos, 390, 1)

#     # Update Vehicle
#     rl, rr, lm, rm = vehicle.update(light_pos)
#     vehicle.last_speed = lm + rm
#     vehicle.draw(screen)

#     # UI / Debug
#     status = "MOVING" if (lm+rm > 0) else "DECIDING (Wait...)"
#     ui_text = [
#         "Vehicle 4b: 'Decisions'",
#         "Logic: Threshold (Step Function)",
#         f"Status: {status}",
#         f"L-Input: {rl:.2f} | R-Input: {rr:.2f}",
#         f"Threshold Needed: {vehicle.threshold}",
#         "Move light close. Notice it waits, then suddenly attacks."
#     ]
#     for i, line in enumerate(ui_text):
#         screen.blit(font.render(line, True, (0,0,0)), (10, 10 + i*20))

#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()