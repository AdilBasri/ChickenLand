import pygame
import math
from settings import *

# --- STANDART NPC ---
class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, variant='duck'):
        super().__init__()
        self.variant = variant
        self.frames = []
        
        try:
            if variant == 'duck':
                sheet = pygame.image.load('assets/duck_wolk.png').convert_alpha()
                frame_count = 2
                scale = 1.25
            elif variant == 'seagull':
                sheet = pygame.image.load('assets/seagull_wolk.png').convert_alpha()
                frame_count = 5
                scale = 2.5
            elif variant == 'twi':
                sheet = pygame.image.load('assets/twi_wolk.png').convert_alpha()
                frame_count = 5 
                scale = 0.9
            elif variant == 'tukan':
                sheet = pygame.image.load('assets/tukan_wolk.png').convert_alpha()
                frame_count = 4
                scale = 1.2
            else:
                sheet = pygame.image.load('assets/duck_wolk.png').convert_alpha()
                frame_count = 2
                scale = 1.25

            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            frame_width = sheet_width // frame_count
            
            target_size = int(TILE_SIZE * scale)
            
            for i in range(frame_count):
                surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
                surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
                scaled = pygame.transform.scale(surface, (target_size, target_size))
                
                if variant not in ['tukan']: 
                    scaled = pygame.transform.flip(scaled, True, False)
                
                self.frames.append(scaled)
            
        except FileNotFoundError:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((0, 255, 0))
            self.frames = [s]

        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(midbottom=(x + TILE_SIZE//2, y + TILE_SIZE))
        self.last_update = pygame.time.get_ticks()
        self.idle_image = self.frames[0]

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 200: 
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def draw_scrolled(self, screen, scroll_x):
        self.animate()
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))
            
    def check_proximity(self, player_rect, scroll_x, screen, already_recruited):
        distance = abs(self.rect.centerx - player_rect.centerx)
        if distance < 150 and not already_recruited:
            return True
        return False

# --- YER DÜŞMANI (KÖPEK) ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = self.import_assets()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y + 20))
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 3
        self.last_update = pygame.time.get_ticks()
        self.facing_left = True 
        self.target_player = None
        
        try:
            self.bark_sound = pygame.mixer.Sound('assets/bark.wav')
            self.bark_sound.set_volume(0.4) 
        except: self.bark_sound = None
        self.last_bark_time = 0

    def import_assets(self):
        try:
            sheet = pygame.image.load('assets/dog.png').convert_alpha()
            frames = []
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            frame_width = sheet_width // 3 
            for i in range(3):
                surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
                surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
                scaled = pygame.transform.scale(surface, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 1.5)))
                frames.append(scaled)
            return frames
        except FileNotFoundError:
            return [pygame.Surface((64,64)) for _ in range(3)]

    def find_closest_player(self, party):
        closest = None
        min_dist = 9999
        for p in party:
            if not p.is_dead:
                dist = abs(self.rect.x - p.rect.x)
                if dist < min_dist:
                    min_dist = dist
                    closest = p
        return closest

    def ai_behavior(self, party):
        self.target_player = self.find_closest_player(party)
        
        if self.target_player:
            if abs(self.rect.y - self.target_player.rect.y) < 150:
                distance = self.target_player.rect.x - self.rect.x
                
                if abs(distance) < 800:
                    now = pygame.time.get_ticks()
                    if now - self.last_bark_time > 2000: 
                        if self.bark_sound: self.bark_sound.play()
                        self.last_bark_time = now

                    if distance > 0:
                        self.velocity.x = self.speed
                        self.facing_left = False
                    else:
                        self.velocity.x = -self.speed
                        self.facing_left = True 
                else:
                    self.velocity.x = 0
            else:
                self.velocity.x = 0
        else:
            self.velocity.x = 0

    def update(self, tiles, hazards, party):
        self.ai_behavior(party)
        
        in_water = pygame.sprite.spritecollideany(self, hazards)
        
        if in_water:
            self.velocity.y += GRAVITY * 0.1
            if self.velocity.y > 2:
                self.velocity.y = 2
            self.velocity.x += math.sin(pygame.time.get_ticks() * 0.005) * 0.5
            self.velocity.x *= 0.9
        else:
            self.velocity.y += GRAVITY

        self.rect.x += self.velocity.x
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.x > 0: self.rect.right = tile.rect.left
                if self.velocity.x < 0: self.rect.left = tile.rect.right
        
        self.rect.y += self.velocity.y
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.y > 0: 
                    self.rect.bottom = tile.rect.top
                    self.velocity.y = 0
                elif self.velocity.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.velocity.y = 0
                    
        self.animate()

    def animate(self):
        if self.velocity.x != 0:
            now = pygame.time.get_ticks()
            if now - self.last_update > ANIMATION_SPEED:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.frames)    
        image = self.frames[self.frame_index]
        if not self.facing_left:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

# --- HİNDİSTAN CEVİZİ MERMİSİ ---
class Coconut(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        try:
            original_image = pygame.image.load('assets/coco.png').convert_alpha()
            self.image = pygame.transform.scale(original_image, (int(TILE_SIZE*2.0), int(TILE_SIZE*2.0)))
        except FileNotFoundError:
            self.image = pygame.Surface((40, 40))
            self.image.fill((139, 69, 19))
            
        self.rect = self.image.get_rect(center=start_pos)
        
        self.speed = 7
        start_vec = pygame.math.Vector2(start_pos)
        target_vec = pygame.math.Vector2(target_pos)
        if start_vec.distance_to(target_vec) > 0:
            self.velocity = (target_vec - start_vec).normalize() * self.speed
        else:
            self.velocity = pygame.math.Vector2(0, 0)
        
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 3000

    def update(self, tile_group):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        
        if pygame.sprite.spritecollideany(self, tile_group):
            self.kill()
            
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE*5 < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

# --- UÇAN DÜŞMAN (ANAN) ---
class FlyingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = self.import_assets()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.rect.inflate_ip(-self.rect.width * 0.5, -self.rect.height * 0.5)
        
        self.start_x = x
        self.start_y = y
        self.hover_timer = 0
        
        self.last_update = pygame.time.get_ticks()
        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_cooldown = 3000 
        self.detection_radius = 600 
        self.facing_left = True 
        self.active = False 
        
        try:
            self.throw_sound = pygame.mixer.Sound('assets/throw.mp3')
        except: self.throw_sound = None

    def import_assets(self):
        try:
            sheet = pygame.image.load('assets/anan.png').convert_alpha()
            frames = []
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            frame_count = 8
            frame_width = sheet_width // frame_count
            for i in range(frame_count):
                surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
                surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
                scaled = pygame.transform.scale(surface, (int(TILE_SIZE * 2), int(TILE_SIZE * 2)))
                frames.append(scaled)
            return frames
        except FileNotFoundError:
            return [pygame.Surface((64,64)) for _ in range(8)]

    def find_closest_player(self, party):
        closest = None
        min_dist = 9999
        for p in party:
            if not p.is_dead:
                dist = math.sqrt((self.rect.centerx - p.rect.centerx)**2 + (self.rect.centery - p.rect.centery)**2)
                if dist < min_dist:
                    min_dist = dist
                    closest = p
        return closest

    def update(self, party, projectile_group):
        target = self.find_closest_player(party)
        
        if target:
            dist = math.sqrt((self.rect.centerx - target.rect.centerx)**2 + (self.rect.centery - target.rect.centery)**2)
            
            if dist < self.detection_radius:
                self.active = True
            
            if self.active:
                target_x = target.rect.centerx
                target_y = target.rect.top - 250 
                
                self.rect.x += (target_x - self.rect.centerx) * 0.02
                self.rect.y += (target_y - self.rect.centery) * 0.02
                
                if target_x < self.rect.centerx:
                    self.facing_left = True 
                else:
                    self.facing_left = False 
                
                self.hover_timer += 0.03
                self.rect.y += math.sin(self.hover_timer) * 1.0 
                
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > self.shoot_cooldown:
                    self.last_shot_time = now
                    if self.throw_sound: self.throw_sound.play()
                    
                    coconut = Coconut(self.rect.center, target.rect.center)
                    projectile_group.add(coconut)

        self.animate()

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 100: 
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)    
        
        image = self.frames[self.frame_index]
        if not self.facing_left:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def draw_scrolled(self, screen, scroll_x):
        draw_rect = self.image.get_rect(center=(self.rect.centerx - scroll_x, self.rect.centery))
        if -TILE_SIZE*2 < draw_rect.x < SCREEN_WIDTH:
            screen.blit(self.image, draw_rect)

# --- YENİ KARAKTER: YILAN ---
class Snake(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.state = 'idle' 
        self.facing_left = True
        self.on_ground = False
        self.is_upside_down_in_water = False 
        self.sunk_amount = 0 # Gömülme miktarını takip etmek için

        self.gravity = 0.8
        self.jump_speed_y = -12  
        self.jump_speed_x = 4    
        self.last_jump_time = 0 
        self.jump_cooldown = 3000 
        self.detection_radius = 300 

        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = pygame.math.Vector2(0, 0)

        self.animation_speed = 150
        self.last_update = pygame.time.get_ticks()
        self.frame_index = 0
        
        self.walk_frames = self.load_sheet('assets/snake_wolk.png', frame_count=3, scale=1.5)
        self.jump_frames = self.load_sheet('assets/snake_jump.png', frame_count=5, scale=1.5)

        self.frames = self.walk_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(x + TILE_SIZE // 2, y + TILE_SIZE - 10))
        
        try:
            self.snake_sound = pygame.mixer.Sound('assets/snake.wav')
        except: self.snake_sound = None

    def load_sheet(self, path, frame_count, scale):
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frames = []
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            frame_width = sheet_width // frame_count
            
            for i in range(frame_count):
                surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
                surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
                scaled_surface = pygame.transform.scale(surface, (int(TILE_SIZE * scale), int(TILE_SIZE * scale)))
                frames.append(scaled_surface)
            return frames
        except FileNotFoundError:
            print(f"HATA: {path} dosyası bulunamadı!")
            return [pygame.Surface((TILE_SIZE, TILE_SIZE)) for _ in range(frame_count)]

    def find_closest_player(self, party):
        closest = None
        min_dist = 9999
        for p in party:
            if not p.is_dead:
                dist = math.sqrt((self.rect.centerx - p.rect.centerx)**2 + (self.rect.centery - p.rect.centery)**2)
                if dist < min_dist:
                    min_dist = dist
                    closest = p
        return closest

    def ai_behavior(self, party):
        target = self.find_closest_player(party)
        now = pygame.time.get_ticks()

        if target:
            dist = math.sqrt((self.rect.centerx - target.rect.centerx)**2 + (self.rect.centery - target.rect.centery)**2)
            
            if target.rect.centerx < self.rect.centerx:
                self.facing_left = True
                self.direction.x = -1
            else:
                self.facing_left = False
                self.direction.x = 1

            if self.on_ground and self.state != 'jumping':
                if dist < self.detection_radius:
                    if now - self.last_jump_time > self.jump_cooldown:
                        self.state = 'jumping'
                        if self.snake_sound: self.snake_sound.play()
                        self.velocity.y = self.jump_speed_y
                        self.velocity.x = self.jump_speed_x * self.direction.x
                        self.frames = self.jump_frames 
                        self.frame_index = 0
                else:
                    if self.frames != self.walk_frames:
                        self.frame_index = 0
                        self.frames = self.walk_frames
                    
                    self.state = 'idle'
                    self.velocity.x = 0
        else:
            if self.frames != self.walk_frames:
                self.frame_index = 0
                self.frames = self.walk_frames
            self.state = 'idle'
            self.velocity.x = 0

    def update(self, tiles, hazards, party):
        in_water = pygame.sprite.spritecollideany(self, hazards)
        
        # --- ÖZEL DURUM: SUDA TERS DÖNÜP GÖMÜLME ---
        if self.is_upside_down_in_water:
            # Eğer gömülme miktarı yarım kareden azsa (TILE_SIZE // 2)
            if self.sunk_amount < TILE_SIZE // 2:
                sink_step = 2 # Batma hızı (su içindeki düşme hızıyla benzer)
                self.rect.y += sink_step
                self.sunk_amount += sink_step
            # Gömülme bitince başka bir fizik uygulamıyoruz, sadece animasyonu yeniliyoruz
            self.animate()
            return # Update fonksiyonundan çık, aşağıya gitme

        # --- NORMAL FİZİK DÖNGÜSÜ ---
        if in_water:
            self.state = 'water'
            self.velocity.y += self.gravity * 0.1 
            if self.velocity.y > 2: self.velocity.y = 2
            
            # Suda süzülme hareketi
            self.velocity.x += math.sin(pygame.time.get_ticks() * 0.005) * 0.3
            self.velocity.x *= 0.9 
        else:
            if self.state != 'jumping':
                 self.ai_behavior(party)
            self.velocity.y += self.gravity 

        # X Hareketi
        self.rect.x += self.velocity.x
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.x > 0: self.rect.right = tile.rect.left
                if self.velocity.x < 0: self.rect.left = tile.rect.right
                if self.state == 'jumping':
                    self.state = 'idle'
                    self.last_jump_time = pygame.time.get_ticks()

        # Y Hareketi
        self.rect.y += self.velocity.y
        self.on_ground = False 
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.y > 0: 
                    self.rect.bottom = tile.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    
                    # Eğer suyun dibine çarptıysa ÖLÜ TAKLİDİ modunu aç
                    if in_water:
                        self.is_upside_down_in_water = True
                        self.velocity.x = 0
                        # Burada return yapmıyoruz ki bu frame'i tamamlasın, sonraki frame'de üstteki if bloğuna girecek

                    if self.state == 'jumping':
                        self.state = 'idle'
                        self.last_jump_time = pygame.time.get_ticks()
                elif self.velocity.y < 0: 
                    self.rect.top = tile.rect.bottom
                    self.velocity.y = 0

        # Titreşim önleyici hassas zemin kontrolü
        if not self.on_ground and not self.is_upside_down_in_water:
            self.rect.y += 1
            for tile in tiles:
                if self.rect.colliderect(tile.rect):
                    self.on_ground = True
                    break
            self.rect.y -= 1 

        self.animate()

    def animate(self):
        if self.is_upside_down_in_water:
            image = self.frames[0] 
            flipped_image = pygame.transform.flip(image, not self.facing_left, True)
            self.image = flipped_image
            return 

        now = pygame.time.get_ticks()
        speed = self.animation_speed
        if self.state == 'jumping': speed = 100 
        
        if now - self.last_update > speed:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        
        image = self.frames[self.frame_index]
        
        if not self.facing_left:
            image = pygame.transform.flip(image, True, False)
            
        self.image = image

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))