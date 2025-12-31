import pygame
import sys
import math
from settings import *
from sprites import Tile, Flag, WebItem, WaveGrass
from player import Player
from npcs import NPC, Enemy
from ui import draw_prompt, draw_dialogue_box, MainMenu, WorldMap # YENİ SINIFLAR EKLENDİ
from level_map import LEVEL_1_MAP, LEVEL_2_MAP, LEVEL_3_MAP, LEVEL_4_MAP, LEVEL_5_MAP, LEVEL_6_MAP

# --- GLOBAL DURUMLAR ---
CURRENT_STATE = STATE_MENU # Başlangıç durumu MENÜ
CURRENT_LEVEL_ID = 1

# --- PARTİ SİSTEMİ ---
party = []          
active_index = 0    

# --- EFEKT SİSTEMİ ---
particle_group = pygame.sprite.Group()

# --- GEÇİŞ ANİMASYONU ---
TRANSITION_RADIUS = 0
MAX_RADIUS = int(math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)) 
TRANSITION_SPEED = 25 
TRANSITION_ANGLE = 0
IS_TRANSITIONING = False

# --- UI NESNELERİ ---
main_menu = None
world_map = None

# --- PARALLAX SISTEMI SINIFI ---
class ParallaxBackground:
    def __init__(self):
        self.layers = []
        try:
            sky_img = pygame.image.load('assets/bckg_1.jpg').convert()
            sky_img = pygame.transform.scale(sky_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.layers.append({'image': sky_img, 'speed': 0, 'y': 0, 'width': SCREEN_WIDTH})
        except: pass
        try:
            mountain_img = pygame.image.load('assets/bckg_2.jpg').convert_alpha()
            target_height = int(SCREEN_HEIGHT * 0.6) 
            aspect_ratio = mountain_img.get_width() / mountain_img.get_height()
            target_width = int(target_height * aspect_ratio)
            mountain_img = pygame.transform.scale(mountain_img, (target_width, target_height))
            flipped_mountain = pygame.transform.flip(mountain_img, True, False)
            seamless_width = target_width * 2
            seamless_surface = pygame.Surface((seamless_width, target_height), pygame.SRCALPHA)
            seamless_surface.blit(mountain_img, (0, 0))
            seamless_surface.blit(flipped_mountain, (target_width, 0))
            self.layers.append({'image': seamless_surface, 'speed': 0.2, 'y': SCREEN_HEIGHT - target_height, 'width': seamless_width})
        except: pass
        try:
            cloud_img = pygame.image.load('assets/bckg_3.jpg').convert()
            cloud_img.set_colorkey(cloud_img.get_at((0, 0)))
            target_height = int(SCREEN_HEIGHT * 0.4)
            aspect_ratio = cloud_img.get_width() / cloud_img.get_height()
            target_width = int(target_height * aspect_ratio)
            cloud_img = pygame.transform.scale(cloud_img, (target_width, target_height))
            self.layers.append({'image': cloud_img, 'speed': 0.5, 'y': 50, 'width': target_width})
        except: pass

    def draw(self, screen, scroll_x):
        if not self.layers:
            screen.fill(SKY_BLUE)
            return
        for layer in self.layers:
            img, speed, width, y_pos = layer['image'], layer['speed'], layer['width'], layer['y']
            if speed == 0: screen.blit(img, (0, 0))
            else:
                rel_x = - (scroll_x * speed) % width
                draw_x = rel_x - width
                while draw_x < SCREEN_WIDTH:
                    screen.blit(img, (draw_x, y_pos))
                    draw_x += width

def create_level(level_map, level_num, party_list):
    tiles, hazards, npcs, enemies, flags, web_items, wave_grass = (pygame.sprite.Group() for _ in range(7))
    owned_types = [p.char_type for p in party_list]
    grapple_owned = any(p.has_grapple for p in party_list)

    for r, row in enumerate(level_map):
        for c, cell in enumerate(row):
            x, y = c * TILE_SIZE, r * TILE_SIZE
            if cell == 'X': tiles.add(Tile(x, y, 'grass'))
            elif cell == 'T': 
                tiles.add(Tile(x, y, 'dirt'))
                wave_grass.add(WaveGrass(x, y))
            elif cell == 'K': tiles.add(Tile(x, y, 'box'))
            elif cell == 'W': hazards.add(Tile(x, y, 'water'))
            elif cell == 'N': 
                target = 'duck' 
                if level_num == 4: target = 'seagull'
                if level_num == 6: target = 'twi' 
                if target not in owned_types: npcs.add(NPC(x, y, target))
            elif cell == 'D': enemies.add(Enemy(x, y)) 
            elif cell == 'F': flags.add(Flag(x, y))
            elif cell == 'S': 
                if not grapple_owned: web_items.add(WebItem(x, y)) 
    return tiles, hazards, npcs, enemies, flags, web_items, wave_grass

def reset_game(party_list, level_id):
    start_x, start_y = 200, 500 
    for i, p in enumerate(party_list):
        p.rect.topleft = (start_x - (i * 30), start_y)
        p.velocity = pygame.math.Vector2(0, 0)
        p.is_dead = False
        p.grapple_state = 'none' 
    
    particle_group.empty()
    
    # Harita seçimi
    current_map = LEVEL_1_MAP
    if level_id == 2: current_map = LEVEL_2_MAP
    elif level_id == 3: current_map = LEVEL_3_MAP
    elif level_id == 4: current_map = LEVEL_4_MAP
    elif level_id == 5: current_map = LEVEL_5_MAP
    elif level_id == 6: current_map = LEVEL_6_MAP
    
    return create_level(current_map, level_id, party_list)

def draw_transition(screen):
    global TRANSITION_RADIUS, TRANSITION_ANGLE
    rect_size = max(0, TRANSITION_RADIUS)
    surface = pygame.Surface((int(rect_size), int(rect_size)))
    surface.fill(TRANSITION_COLOR)
    rotated = pygame.transform.rotate(surface, TRANSITION_ANGLE)
    screen.blit(rotated, rotated.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
    TRANSITION_ANGLE += 5

def main():
    global CURRENT_STATE, DIALOGUE_OPTION, CURRENT_LEVEL_ID, TRANSITION_RADIUS, active_index, party, IS_TRANSITIONING, main_menu, world_map
    
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Chick: Going To Chicken Land")
    clock = pygame.time.Clock()
    
    try: ui_font = pygame.font.Font('assets/font.ttf', 20)
    except: ui_font = pygame.font.SysFont("Arial", 20, bold=True)
    
    parallax_bg = ParallaxBackground()
    main_menu = MainMenu()
    world_map = WorldMap()

    # Başlangıç Partisi
    p1 = Player(200, 500, char_type='chicken', p_index=1)
    party = [p1]
    
    # Grupları tanımla (Boş olarak)
    tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group, wave_grass_group = (pygame.sprite.Group() for _ in range(7))
    scroll_x = 0
    can_interact = False
    
    while True:
        # --- INPUT İŞLEMLERİ ---
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(), sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if CURRENT_STATE == STATE_GAME: CURRENT_STATE = STATE_MAP # Oyundan haritaya çık
                elif CURRENT_STATE == STATE_MAP: CURRENT_STATE = STATE_MENU # Haritadan menüye çık
                else: pygame.quit(), sys.exit()

            # MENÜ DURUMU
            if CURRENT_STATE == STATE_MENU:
                action = main_menu.handle_input(event)
                if action == "YENI OYUN":
                    CURRENT_STATE = STATE_MAP
                elif action == "CIKIS":
                    pygame.quit(), sys.exit()
            
            # HARİTA DURUMU
            elif CURRENT_STATE == STATE_MAP:
                selected_level = world_map.handle_input(event)
                if selected_level:
                    CURRENT_LEVEL_ID = selected_level
                    # Bölümü Yükle
                    tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group, wave_grass_group = reset_game(party, CURRENT_LEVEL_ID)
                    CURRENT_STATE = STATE_GAME
            
            # OYUN DURUMU (Diyalog, Karakter Değişimi vb.)
            elif CURRENT_STATE == STATE_GAME:
                if active_index >= len(party): active_index = 0
                active_player = party[active_index]

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if len(party) > 1:
                            active_player.grapple_state = 'none' 
                            active_index = (active_index + 1) % len(party)
                    if event.key == pygame.K_UP and active_player.grapple_state != 'aiming':
                             active_player.jump()
                    if event.key == pygame.K_e and can_interact:
                        DIALOGUE_OPTION = 0 # Sıfırla
                        # Diyalog modu için basit bir duraklatma veya state değişimi yapılabilir
                        # Şimdilik direkt diyalog çizimini oyun döngüsünde yapıyoruz.
                        pass 
                
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    if active_player.grapple_state == 'aiming':
                        active_player.fire_grapple(tile_group)

        # --- UPDATE & DRAW İŞLEMLERİ ---
        
        if CURRENT_STATE == STATE_MENU:
            main_menu.draw(screen)

        elif CURRENT_STATE == STATE_MAP:
            screen.fill((20, 20, 40)) # Harita arkaplanı (görsel yoksa)
            world_map.draw(screen)

        elif CURRENT_STATE == STATE_GAME:
            active_player = party[active_index]
            
            # SCROLL
            target_scroll = active_player.rect.centerx - SCREEN_WIDTH / 2
            if target_scroll < 0: target_scroll = 0
            scroll_x += (target_scroll - scroll_x) * 0.1

            # UPDATE
            wave_grass_group.update(party)
            particle_group.update()
            
            any_dead = False
            for p in party:
                p.update(tile_group, hazard_group, 'playing', (p == active_player), party, particle_group)
                if pygame.sprite.spritecollide(p, enemy_group, False): p.is_dead = True
                if p.is_dead: any_dead = True
                # Ağ özelliği paylaşımı
                if pygame.sprite.spritecollide(p, web_group, True):
                    for member in party: member.has_grapple = True

            # NPC Etkileşim (Karakter Katılımı)
            can_interact = False
            for npc in npc_group:
                if npc.check_proximity(active_player.rect, scroll_x, screen, False):
                    # Eğer E'ye basıldıysa ve diyalog çiziliyorsa (Bu kısım basit tutuldu)
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e]:
                        # Karakteri ekle (Basit versiyon)
                        new_p_index = len(party) + 1
                        new_type = npc.variant
                        new_char = Player(npc.rect.x, npc.rect.y, char_type=new_type, p_index=new_p_index)
                        if active_player.has_grapple: new_char.has_grapple = True
                        party.append(new_char)
                        npc.kill() # NPC'yi yok et
                    else:
                        can_interact = True

            # Düşmanlar & Objeler
            for enemy in enemy_group: enemy.update(tile_group, active_player)
            web_group.update()

            # Bölüm Sonu Kontrolü
            all_finished = True
            for p in party:
                if not pygame.sprite.spritecollide(p, flag_group, False):
                    all_finished = False
                    break
            
            if all_finished:
                IS_TRANSITIONING = True # Geçişi başlat

            # Ölüm Kontrolü
            if any_dead:
                 tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group, wave_grass_group = reset_game(party, CURRENT_LEVEL_ID)

            # ÇİZİM
            if parallax_bg: parallax_bg.draw(screen, scroll_x)
            else: screen.fill(SKY_BLUE)
            
            for group in [tile_group, hazard_group, flag_group, enemy_group, web_group, npc_group]:
                for sprite in group:
                    if hasattr(sprite, 'draw_scrolled'): sprite.draw_scrolled(screen, scroll_x)
            
            for p in party: p.draw(screen, scroll_x)
            for wg in wave_grass_group: wg.draw_scrolled(screen, scroll_x)
            for pt in particle_group: pt.draw_scrolled(screen, scroll_x)
            
            if can_interact: 
                # En yakın NPC'nin üzerine E koy
                if npc_group: draw_prompt(screen, npc_group.sprites()[0].rect.centerx - scroll_x, npc_group.sprites()[0].rect.top - 20)
            
            # UI
            info_text = f"BOLUM: {CURRENT_LEVEL_ID} | P{active_player.p_index}"
            screen.blit(ui_font.render(info_text, True, (0,0,0)), (20, 20))

            # GEÇİŞ EFEKTİ (Bölüm Bittiğinde)
            if IS_TRANSITIONING:
                TRANSITION_RADIUS += TRANSITION_SPEED
                draw_transition(screen)
                if TRANSITION_RADIUS > MAX_RADIUS * 1.5:
                    # BÖLÜM GEÇİLDİ! Haritaya dön ve kilidi aç.
                    IS_TRANSITIONING = False
                    TRANSITION_RADIUS = 0
                    world_map.unlock_next_level(CURRENT_LEVEL_ID)
                    CURRENT_STATE = STATE_MAP

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()