import pygame
import math
from settings import *

# Karakter Ayarları
CHAR_CONFIG = {
    'chicken': {'walk': 'assets/chicken.png', 'jump': 'assets/jump.png', 'frames': (6, 6), 'scale': 2.5, 'offset': 55, 'jump_power': -16, 'gravity_factor': 1.0},
    'duck': {'walk': 'assets/duck_wolk.png', 'jump': 'assets/duck_jump.png', 'frames': (2, 4), 'scale': 1.25, 'offset': 0, 'jump_power': -14, 'gravity_factor': 0.4},
    'seagull': {'walk': 'assets/seagull_wolk.png', 'jump': 'assets/seagull_jump.png', 'frames': (5, 5), 'scale': 2.5, 'offset': 0, 'jump_power': -22, 'gravity_factor': 1.0}
}

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, char_type='chicken', p_index=1):
        super().__init__()
        self.char_type = char_type
        self.p_index = p_index 
        
        config = CHAR_CONFIG.get(char_type, CHAR_CONFIG['chicken'])
        self.scale = config['scale']
        self.visual_offset = config['offset']
        self.base_jump_power = config['jump_power']
        self.gravity_factor = config['gravity_factor']
        
        self.animations = {'walk': [], 'jump': []}
        self.import_character_assets(config['walk'], config['jump'], config['frames'])
        
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
        
        # --- AĞ ATMA (GRAPPLE) DEĞİŞKENLERİ ---
        self.has_grapple = False
        self.grapple_state = 'none' # 'none', 'aiming', 'active'
        self.grapple_angle = 0      # 0-360 derece (0 = Sağ, 180 = Sol)
        self.grapple_point = None 
        self.rope_length = 0      

        # Etiket
        try:
            self.font = pygame.font.Font('assets/font.ttf', 16)
        except:
            self.font = pygame.font.SysFont("Arial", 16, bold=True)
            
        self.label_surf = self.font.render(f"P{self.p_index}", True, (255, 255, 255))
        self.label_bg = pygame.Surface((self.label_surf.get_width() + 4, self.label_surf.get_height() + 4))
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

    def get_input(self, party):
        keys = pygame.key.get_pressed()
        self.acceleration.x = 0
        
        # --- AĞ ATMA KONTROLLERİ ---
        if self.has_grapple:
            # 1. NİŞAN ALMA (Aiming)
            # Eğer Space basılıysa VE şu an havada asılı değilsek -> Nişan al
            if keys[pygame.K_SPACE] and self.grapple_state != 'active':
                self.grapple_state = 'aiming'
                
                # SADECE OKU ÇEVİR (Yürümeyi engellemek için return kullanacağız)
                # Açıyı kontrol et
                if keys[pygame.K_LEFT]: self.grapple_angle += 3
                if keys[pygame.K_RIGHT]: self.grapple_angle -= 3
                
                # Açıyı 0-360 arasında tut (Daha düzgün matematik için)
                self.grapple_angle = self.grapple_angle % 360
                
                # BURADA RETURN YAPIYORUZ:
                # Böylece aşağıdaki yürüme kodları çalışmıyor, karakter olduğu yerde kalıyor.
                # Ancak physics_update çalıştığı için sürtünme (friction) onu yavaşça durdurur.
                return 

            # 2. SALLANMA (Active)
            if self.grapple_state == 'active':
                # Burada Arrow Keys yürütmez, sarkaç kuvveti uygular
                swing_power = 0.8 # Kuvveti biraz artırdım hissedilsin diye
                if keys[pygame.K_LEFT]:
                    self.velocity.x -= swing_power
                if keys[pygame.K_RIGHT]:
                    self.velocity.x += swing_power
                
                if keys[pygame.K_UP]: 
                    self.rope_length -= 3
                    if self.rope_length < 50: self.rope_length = 50
                if keys[pygame.K_DOWN]: 
                    self.rope_length += 3
                    if self.rope_length > ROPE_LENGTH_MAX: self.rope_length = ROPE_LENGTH_MAX
                
                return # Yürümeyi engelle

        # --- NORMAL YÜRÜME (Sadece Ağ kullanmıyorsak buraya gelir) ---
        
        # Eğer buraya geldiysek ve grapple_state 'aiming' ise (yani Space bırakıldı ama henüz fırlatılmadıysa)
        # main.py'deki KEY_UP olayı 'aiming'i 'none' yapana kadar bekleriz.
        # Ama genelde Space bırakıldığı an fırlatılır.
        
        self.carrying_weight = self.calculate_weight_above(party)
        speed_modifier = 1.0
        if self.carrying_weight > 0:
            if not (self.char_type == 'seagull' and self.carrying_weight <= 2):
                speed_modifier = 0.2
        
        target_accel = ACCELERATION * speed_modifier
        
        if keys[pygame.K_RIGHT]:
            self.acceleration.x = target_accel
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.acceleration.x = -target_accel
            self.facing_right = False

    def jump(self):
        # Nişan alırken zıplamayı engelle
        if self.grapple_state == 'aiming':
            return

        # Ağdan kurtulma (Zıplama tuşuyla)
        if self.grapple_state == 'active':
            self.grapple_state = 'none'
            self.velocity.y = -10 # İpten kopunca yukarı fırla
            return

        can_jump = True
        if self.carrying_weight > 0:
            if not (self.char_type == 'seagull' and self.carrying_weight <= 2):
                can_jump = False

        if can_jump and (self.on_ground or self.jump_count < 2):
            self.velocity.y = self.base_jump_power 
            self.on_ground = False
            self.jump_count += 1

    def release_grapple(self):
        """Main.py'den çağrılabilir, manuel bırakma"""
        if self.grapple_state == 'active':
            self.grapple_state = 'none'
            self.velocity.y = -5 # Hafif zıpla

    def apply_gravity(self):
        if self.velocity.y > 0:
            self.acceleration.y = GRAVITY * self.gravity_factor
        else:
            self.acceleration.y = GRAVITY

    def physics_update(self):
        self.apply_gravity()
        self.velocity += self.acceleration
        self.velocity.x *= FRICTION
        
        # --- AĞ FİZİĞİ (Sarkaç) ---
        if self.grapple_state == 'active' and self.grapple_point:
            dx = self.rect.centerx - self.grapple_point[0]
            dy = self.rect.centery - self.grapple_point[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > self.rope_length:
                angle = math.atan2(dy, dx)
                self.rect.centerx = self.grapple_point[0] + math.cos(angle) * self.rope_length
                self.rect.centery = self.grapple_point[1] + math.sin(angle) * self.rope_length
                
                # Momentum Koruması (Teğet Hız)
                nx = dx / dist
                ny = dy / dist
                dot = self.velocity.x * nx + self.velocity.y * ny
                
                # İpi geren hızı iptal et, geri kalanı koru
                if dot > 0:
                    self.velocity.x -= dot * nx
                    self.velocity.y -= dot * ny
                    self.velocity *= 0.99 # Hava direnci

        if abs(self.velocity.x) > MAX_SPEED * 1.5: 
            self.velocity.x = (MAX_SPEED * 1.5) * (1 if self.velocity.x > 0 else -1)
        if abs(self.velocity.x) < 0.1: self.velocity.x = 0

    def fire_grapple(self, tiles):
        rad = math.radians(self.grapple_angle)
        start_x, start_y = self.rect.center
        
        # Daha sık kontrol (5px) - Işınlanma hissini azaltır ve ince duvarları yakalar
        for i in range(0, ROPE_LENGTH_MAX, 5): 
            check_x = start_x + math.cos(rad) * i
            check_y = start_y - math.sin(rad) * i 
            
            for tile in tiles:
                # collidepoint yerine rect collision daha garantidir
                # Küçük bir nokta rect oluşturuyoruz
                point_rect = pygame.Rect(check_x - 2, check_y - 2, 4, 4)
                
                if tile.rect.colliderect(point_rect):
                    self.grapple_state = 'active'
                    self.grapple_point = (check_x, check_y)
                    self.rope_length = i 
                    
                    # Fırlatınca karakteri o yöne hafif çek
                    self.velocity += pygame.math.Vector2(math.cos(rad)*5, -math.sin(rad)*5)
                    return True
        return False

    def check_collisions(self, tiles, hazards, party):
        self.rect.x += self.velocity.x
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.x > 0: self.rect.right = tile.rect.left
                if self.velocity.x < 0: self.rect.left = tile.rect.right
                self.velocity.x = 0
        
        # Pushing
        for other in party:
            if other != self and self.rect.colliderect(other.rect):
                if abs(self.velocity.x) > 0.5:
                    push = self.velocity.x
                    other.rect.x += push
                    # Basit duvar kontrolü
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
                    self.rect.bottom = tile.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.jump_count = 0 
                elif self.velocity.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.velocity.y = 0
        
        # Stacking
        for other in party:
            if other != self and self.rect.colliderect(other.rect):
                if self.velocity.y > 0 and self.rect.bottom < other.rect.bottom:
                    self.rect.bottom = other.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.jump_count = 0

        for hazard in hazards:
            if self.rect.inflate(-20, -20).colliderect(hazard.rect):
                self.is_dead = True
        if self.rect.y > 2000: 
            self.is_dead = True

    def animate(self):
        now = pygame.time.get_ticks()
        if self.grapple_state == 'active':
            self.status = 'jump' 
        elif not self.on_ground:
            self.status = 'jump'
            if now - self.last_update > ANIMATION_SPEED:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.animations['jump'])
        else:
            self.status = 'walk'
            if abs(self.velocity.x) > 0.5:
                if now - self.last_update > ANIMATION_SPEED:
                    self.last_update = now
                    self.frame_index = (self.frame_index + 1) % len(self.animations['walk'])
            else:
                self.frame_index = 0

        if self.frame_index >= len(self.animations[self.status]): self.frame_index = 0
        image = self.animations[self.status][self.frame_index]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def update(self, tiles, hazards, game_state, is_active_player, party):
        if game_state == 'playing' and is_active_player:
            self.get_input(party)
        else:
            self.acceleration.x = 0 
            self.carrying_weight = self.calculate_weight_above(party)

        self.physics_update()
        self.check_collisions(tiles, hazards, party)
        self.animate()

    def draw(self, screen, scroll_x):
        # 1. OK VE İP (Karakterin merkezinden çıksın)
        center_x = self.rect.centerx - scroll_x
        center_y = self.rect.centery

        # A) Kırmızı Ok (Sivri Üçgen)
        if self.grapple_state == 'aiming':
            rad = math.radians(self.grapple_angle)
            arrow_len = 70
            
            # Okun ucu
            end_x = center_x + math.cos(rad) * arrow_len
            end_y = center_y - math.sin(rad) * arrow_len
            
            # Çizgiyi çiz (Gövde)
            pygame.draw.line(screen, ARROW_COLOR, (center_x, center_y), (end_x, end_y), 3)
            
            # Uçtaki Sivri Üçgen
            # Ucun biraz gerisindeki merkez
            head_size = 15
            back_x = end_x - math.cos(rad) * head_size
            back_y = end_y + math.sin(rad) * head_size
            
            # Kanatlar (90 derece dik)
            wing_size = 8
            w1_x = back_x + math.cos(rad + math.pi/2) * wing_size
            w1_y = back_y - math.sin(rad + math.pi/2) * wing_size
            
            w2_x = back_x + math.cos(rad - math.pi/2) * wing_size
            w2_y = back_y - math.sin(rad - math.pi/2) * wing_size
            
            # Poligon (Uç, Kanat1, Kanat2)
            pygame.draw.polygon(screen, ARROW_COLOR, [(end_x, end_y), (w1_x, w1_y), (w2_x, w2_y)])

        # B) Beyaz İp
        if self.grapple_state == 'active' and self.grapple_point:
            grapple_screen_x = self.grapple_point[0] - scroll_x
            grapple_screen_y = self.grapple_point[1]
            pygame.draw.line(screen, ROPE_COLOR, (center_x, center_y), (grapple_screen_x, grapple_screen_y), 2)
            pygame.draw.circle(screen, ROPE_COLOR, (grapple_screen_x, grapple_screen_y), 4)

        # 2. KARAKTER
        image_rect = self.image.get_rect()
        image_rect.centerx = self.rect.centerx - scroll_x
        image_rect.bottom = self.rect.bottom
        image_rect.y += self.visual_offset
        screen.blit(self.image, image_rect)
        
        label_x = self.rect.centerx - scroll_x - (self.label_bg.get_width() // 2)
        label_y = image_rect.top - 25
        screen.blit(self.label_bg, (label_x, label_y))
        screen.blit(self.label_surf, (label_x + 2, label_y + 2))