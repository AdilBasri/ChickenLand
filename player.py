import pygame
import math
import random
from settings import *
from sprites import Particle 

# --- KARAKTER AYARLARI ---
# Tukan Eklendi: Ağır başlangıç, yüksek max hız
CHAR_CONFIG = {
    'chicken': {'walk': 'assets/chicken.png', 'jump': 'assets/jump.png', 'frames': (6, 6), 'scale': 2.5, 'offset': 55, 'jump_power': -16, 'gravity_factor': 1.0, 'max_speed': 8, 'accel': 0.6},
    'duck': {'walk': 'assets/duck_wolk.png', 'jump': 'assets/duck_jump.png', 'frames': (2, 4), 'scale': 1.25, 'offset': 0, 'jump_power': -14, 'gravity_factor': 0.4, 'max_speed': 7, 'accel': 0.6},
    'seagull': {'walk': 'assets/seagull_wolk.png', 'jump': 'assets/seagull_jump.png', 'frames': (5, 5), 'scale': 2.5, 'offset': 0, 'jump_power': -22, 'gravity_factor': 1.0, 'max_speed': 8, 'accel': 0.6},
    'twi': {'walk': 'assets/twi_wolk.png', 'jump': 'assets/twi_jump.png', 'frames': (5, 5), 'scale': 0.9, 'offset': 0, 'jump_power': -15, 'gravity_factor': 0.8, 'max_speed': 9, 'accel': 0.9},
    'tukan': {'walk': 'assets/tukan_wolk.png', 'jump': 'assets/tukan_jump.png', 'frames': (4, 4), 'scale': 1.2, 'offset': 0, 'jump_power': -12, 'gravity_factor': 1.0, 'max_speed': 15, 'accel': 0.15}
}

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, char_type='chicken', p_index=1, input_scheme='ARROWS'):
        super().__init__()
        self.char_type = char_type
        self.p_index = p_index
        self.input_scheme = CONTROLS[input_scheme] 
        self.scheme_name = input_scheme 
        
        # Config Yükle
        config = CHAR_CONFIG.get(char_type, CHAR_CONFIG['chicken'])
        self.scale = config['scale']
        self.visual_offset = config['offset']
        self.base_jump_power = config['jump_power']
        self.gravity_factor = config['gravity_factor']
        self.base_max_speed = config['max_speed']
        self.base_accel = config['accel']
        
        self.animations = {'walk': [], 'jump': []}
        # Frame sayıları configden gelir, Tukan için varsayılan (4,4)
        frames = config.get('frames', (4,4))
        self.import_character_assets(config['walk'], config['jump'], frames)
        
        self.frame_index = 0
        self.status = 'walk'
        self.facing_right = True
        
        self.image = self.animations['walk'][0]
        self.rect = pygame.Rect(x, y, 32, 54)
        
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        
        self.last_update = pygame.time.get_ticks()
        self.on_ground = False
        self.jump_count = 0 
        self.start_pos = (x, y)
        self.is_dead = False
        self.carrying_weight = 0
        
        # --- GAME JUICE ---
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.land_particles_spawned = False 
        
        # --- TAŞIMA SİSTEMİ ---
        self.carrier = None      
        self.ride_offset_x = 0   
        
        # --- AĞ ATMA ---
        self.has_grapple = False
        self.grapple_state = 'none' 
        self.grapple_angle = 0      
        self.grapple_point = None 
        self.rope_length = 0      
        self.reeling = False        

        # Etiket
        try: self.font = pygame.font.Font('assets/font.ttf', 14)
        except: self.font = pygame.font.SysFont("Arial", 14, bold=True)
            
        text = f"P{self.p_index}"
        self.label_surf = self.font.render(text, True, (255, 255, 255))
        self.label_bg = pygame.Surface((self.label_surf.get_width() + 6, self.label_surf.get_height() + 4))
        self.label_bg.fill((0, 0, 0))
        self.label_bg.set_alpha(150)

    def import_character_assets(self, walk_path, jump_path, frame_counts):
        try:
            walk_sheet = pygame.image.load(walk_path).convert_alpha()
            self.animations['walk'] = self.split_sheet(walk_sheet, frame_counts[0]) 
            jump_sheet = pygame.image.load(jump_path).convert_alpha()
            self.animations['jump'] = self.split_sheet(jump_sheet, frame_counts[1])
        except FileNotFoundError:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((255, 0, 0))
            self.animations['walk'] = [s]
            self.animations['jump'] = [s]

    def split_sheet(self, sheet, frame_count):
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        frame_width = sheet_width // frame_count
        target_size = int(TILE_SIZE * self.scale)
        for i in range(frame_count):
            surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
            surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
            scaled_surface = pygame.transform.scale(surface, (target_size, target_size))
            frames.append(scaled_surface)
        return frames

    def calculate_weight_above(self, party):
        weight = 0
        sensor_rect = self.rect.copy()
        sensor_rect.y -= 10
        sensor_rect.height = 10
        for other in party:
            if other != self and sensor_rect.colliderect(other.rect):
                weight += 1 + other.calculate_weight_above(party)
        return weight

    def get_input(self, party, is_active_player):
        keys = pygame.key.get_pressed()
        controls = self.input_scheme 

        # Hareket İzni
        should_move = False
        if self.scheme_name == 'WASD': should_move = True
        elif self.scheme_name == 'ARROWS' and is_active_player: should_move = True
        
        if not should_move:
            self.acceleration.x = 0
            self.reeling = False
            return 

        # Taşıyıcıdan inme
        if (keys[controls['left']] or keys[controls['right']] or 
            keys[controls['up']] or keys[controls['grapple']]):
            self.carrier = None

        self.acceleration.x = 0
        self.reeling = False
        
        # Grapple Active
        if self.grapple_state == 'active':
            if keys[controls['grapple']]:
                self.reeling = True
                self.rope_length -= REEL_SPEED
                if self.rope_length < 30: self.rope_length = 30
            
            swing_power = SWING_FORCE
            if keys[controls['left']]: self.velocity.x -= swing_power
            if keys[controls['right']]: self.velocity.x += swing_power
            if keys[controls['down']]: 
                self.rope_length += 5
                if self.rope_length > ROPE_LENGTH_MAX: self.rope_length = ROPE_LENGTH_MAX
            return 

        # Grapple Aiming
        if self.has_grapple and keys[controls['grapple']]:
            if self.grapple_state == 'none': self.grapple_state = 'aiming'
            
            aim_speed = 3
            if keys[controls['up']]: self.grapple_angle += aim_speed if self.facing_right else -aim_speed
            if keys[controls['down']]: self.grapple_angle -= aim_speed if self.facing_right else -aim_speed
            
            if self.facing_right:
                if self.grapple_angle > 80: self.grapple_angle = 80
                if self.grapple_angle < -80: self.grapple_angle = -80
            else:
                if self.grapple_angle < 0: self.grapple_angle += 360
                if -80 < self.grapple_angle < 80: self.grapple_angle = 135 
                if self.grapple_angle < 100: self.grapple_angle = 100
                if self.grapple_angle > 260: self.grapple_angle = 260
            
            self.velocity.x *= 0.5 
            return

        # HAREKET
        self.carrying_weight = self.calculate_weight_above(party)
        speed_modifier = 1.0
        
        if self.carrying_weight > 0:
            if self.char_type != 'seagull': speed_modifier = 0.2
        
        # Tukan ve diğerleri için accel
        target_accel = self.base_accel * speed_modifier
        
        if keys[controls['right']]:
            self.acceleration.x = target_accel
            self.facing_right = True
            if not (-90 < self.grapple_angle < 90): self.grapple_angle = 45 
        elif keys[controls['left']]:
            self.acceleration.x = -target_accel
            self.facing_right = False
            if (-90 < self.grapple_angle < 90): self.grapple_angle = 135

    def jump(self):
        self.carrier = None 
        if self.grapple_state == 'active':
            self.grapple_state = 'none'
            self.velocity.y = -10
            return
        if self.grapple_state == 'aiming': return 

        can_jump = True
        if self.carrying_weight > 0 and self.char_type != 'seagull': can_jump = False

        if can_jump and (self.on_ground or self.jump_count < 2):
            jump_pwr = self.base_jump_power
            
            # Tukan Momentum Zıplaması: Hız ne kadar yüksekse o kadar güçlü zıplar
            if self.char_type == 'tukan':
                momentum_bonus = abs(self.velocity.x) * 0.4
                jump_pwr -= momentum_bonus # Y yukarı doğru negatif
            
            self.velocity.y = jump_pwr
            self.on_ground = False
            self.jump_count += 1
            self.scale_x = 0.7
            self.scale_y = 1.3

    def apply_gravity(self):
        if self.velocity.y > 0: self.acceleration.y = GRAVITY * self.gravity_factor
        else: self.acceleration.y = GRAVITY

    def physics_update(self):
        self.apply_gravity()
        self.velocity += self.acceleration
        
        if self.grapple_state != 'active':
            # Sürtünme: Tukan için daha az sürtünme (kayma hissi)
            fric = FRICTION
            if self.char_type == 'tukan': fric = 0.96 
            self.velocity.x *= fric
        else:
            self.velocity *= 0.995

        # Grapple Swing Logic
        if self.grapple_state == 'active' and self.grapple_point:
            dx = self.rect.centerx - self.grapple_point[0]
            dy = self.rect.centery - self.grapple_point[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > self.rope_length:
                angle = math.atan2(dy, dx)
                self.rect.centerx = self.grapple_point[0] + math.cos(angle) * self.rope_length
                self.rect.centery = self.grapple_point[1] + math.sin(angle) * self.rope_length
                nx, ny = dx / dist, dy / dist
                dot = self.velocity.x * nx + self.velocity.y * ny
                if dot > 0:
                    self.velocity.x -= dot * nx
                    self.velocity.y -= dot * ny

            if self.reeling:
                pull_strength = 2.0
                angle_to_center = math.atan2(dy, dx)
                self.velocity.x -= math.cos(angle_to_center) * pull_strength
                self.velocity.y -= math.sin(angle_to_center) * pull_strength

        # Max Hız Limiti
        if self.grapple_state != 'active':
            limit = self.base_max_speed
            if abs(self.velocity.x) > limit: 
                self.velocity.x = limit * (1 if self.velocity.x > 0 else -1)
        
        if abs(self.velocity.x) < 0.1: self.velocity.x = 0
        
        # Squash fix
        self.scale_x += (1.0 - self.scale_x) * 0.1
        self.scale_y += (1.0 - self.scale_y) * 0.1

    def fire_grapple(self, tiles):
        if not self.has_grapple: return False
        rad = math.radians(self.grapple_angle)
        start_x, start_y = self.rect.center
        
        step = 10
        for i in range(10, ROPE_LENGTH_MAX, step): 
            check_x = start_x + math.cos(rad) * i
            check_y = start_y - math.sin(rad) * i 
            point_rect = pygame.Rect(check_x - 2, check_y - 2, 4, 4)
            for tile in tiles:
                if tile.rect.colliderect(point_rect):
                    self.grapple_state = 'active'
                    self.grapple_point = (check_x, check_y)
                    self.rope_length = i 
                    self.velocity += pygame.math.Vector2(math.cos(rad)*5, -math.sin(rad)*5)
                    return True
        self.grapple_state = 'none'
        return False

    def check_collisions(self, tiles, hazards, party):
        self.rect.x += self.velocity.x
        hit_box = self.rect.inflate(0, -5) 

        for tile in tiles:
            if hit_box.colliderect(tile.rect):
                if self.velocity.x > 0: self.rect.right = tile.rect.left
                if self.velocity.x < 0: self.rect.left = tile.rect.right
                self.velocity.x = 0 
        
        for other in party:
            if other != self and self.rect.colliderect(other.rect):
                if abs(self.velocity.x) > 0.5:
                    push = self.velocity.x * 0.5 
                    other.rect.x += push
                    for t in tiles:
                        if other.rect.colliderect(t.rect):
                            if push > 0: other.rect.right = t.rect.left
                            if push < 0: other.rect.left = t.rect.right
                else:
                    if self.rect.centerx < other.rect.centerx: self.rect.right = other.rect.left
                    else: self.rect.left = other.rect.right

        self.rect.y += self.velocity.y
        self.on_ground = False
        
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.y > 0: 
                    if self.velocity.y > 5: 
                        self.scale_x = 1.4
                        self.scale_y = 0.6
                        self.land_particles_spawned = True 
                    self.rect.bottom = tile.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.jump_count = 0 
                elif self.velocity.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.velocity.y = 0
        
        for other in party:
            if other != self and self.rect.colliderect(other.rect):
                if self.velocity.y > 0 and self.rect.bottom < other.rect.bottom:
                    self.rect.bottom = other.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.jump_count = 0
                    if self.carrier != other:
                        self.carrier = other
                        self.ride_offset_x = self.rect.centerx - other.rect.centerx

        for hazard in hazards:
            if self.rect.inflate(-20, -20).colliderect(hazard.rect): self.is_dead = True
        
        if self.rect.y > 3000: self.is_dead = True

    def animate(self):
        now = pygame.time.get_ticks()
        if self.grapple_state == 'active': self.status = 'jump' 
        elif not self.on_ground: self.status = 'jump'
        else:
            if abs(self.velocity.x) > 0.1: self.status = 'walk'
            else:
                self.status = 'walk'
                self.frame_index = 0 
        
        if (self.status == 'walk' and abs(self.velocity.x) > 0.1) or self.status == 'jump':
            # Tukan hızlıysa animasyon da hızlansın
            anim_speed = ANIMATION_SPEED
            if self.char_type == 'tukan' and abs(self.velocity.x) > 8:
                anim_speed = 50
            
            if now - self.last_update > anim_speed:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.status])

        if self.frame_index >= len(self.animations[self.status]): self.frame_index = 0
        self.image = self.animations[self.status][self.frame_index]

    def update(self, tiles, hazards, game_state, party, particle_group, is_active_player):
        if self.carrier:
            if self.carrier in party and not self.carrier.is_dead:
                self.rect.bottom = self.carrier.rect.top
                self.rect.centerx = self.carrier.rect.centerx + self.ride_offset_x
                self.velocity = pygame.math.Vector2(0, 0)
                self.on_ground = True
            else: self.carrier = None

        if game_state == 'playing': self.get_input(party, is_active_player)
        else: 
            self.acceleration.x = 0 
            self.carrying_weight = self.calculate_weight_above(party)

        self.physics_update()
        self.check_collisions(tiles, hazards, party)
        self.animate()
        
        if self.on_ground and abs(self.velocity.x) > 1:
            if random.random() < 0.2: 
                offset_x = 10 if self.velocity.x > 0 else -10
                particle_group.add(Particle(self.rect.centerx - offset_x, self.rect.bottom, [random.uniform(-0.5, 0.5), random.uniform(-1, -0.5)], random.randint(2, 4), (220, 220, 220), 20))

        if self.land_particles_spawned:
            self.land_particles_spawned = False
            for _ in range(5):
                particle_group.add(Particle(self.rect.centerx, self.rect.bottom, [random.uniform(-3, 3), random.uniform(-1, -0.1)], random.randint(3, 6), (255, 255, 255), 30))

    def draw(self, screen, scroll_x):
        center_x = self.rect.centerx - scroll_x
        center_y = self.rect.centery

        if self.grapple_state == 'aiming':
            rad = math.radians(self.grapple_angle)
            end_x = center_x + math.cos(rad) * ARROW_LENGTH
            end_y = center_y - math.sin(rad) * ARROW_LENGTH
            pygame.draw.line(screen, (255, 255, 255), (center_x, center_y), (end_x, end_y), 2)
            pygame.draw.circle(screen, ARROW_COLOR, (end_x, end_y), 5)

        if self.grapple_state == 'active' and self.grapple_point:
            grapple_screen_x = self.grapple_point[0] - scroll_x
            grapple_screen_y = self.grapple_point[1]
            color = (255, 100, 100) if self.reeling else ROPE_COLOR
            pygame.draw.line(screen, color, (center_x, center_y), (grapple_screen_x, grapple_screen_y), 3)
            pygame.draw.circle(screen, color, (grapple_screen_x, grapple_screen_y), 5)

        img_to_draw = self.image
        if not self.facing_right: img_to_draw = pygame.transform.flip(img_to_draw, True, False)
            
        new_w = int(img_to_draw.get_width() * self.scale_x)
        new_h = int(img_to_draw.get_height() * self.scale_y)
        scaled_img = pygame.transform.scale(img_to_draw, (new_w, new_h))
        
        draw_rect = scaled_img.get_rect()
        draw_rect.centerx = self.rect.centerx - scroll_x
        draw_rect.bottom = self.rect.bottom
        draw_rect.y += self.visual_offset * self.scale_y 
        
        screen.blit(scaled_img, draw_rect)
        
        label_x = self.rect.centerx - scroll_x - (self.label_bg.get_width() // 2)
        label_y = draw_rect.top - 25
        screen.blit(self.label_bg, (label_x, label_y))
        screen.blit(self.label_surf, (label_x + 3, label_y + 2))