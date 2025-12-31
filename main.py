import pygame
import sys
import math
from settings import *
from sprites import Tile, Flag, WebItem, WaveGrass
from player import Player
from npcs import NPC, Enemy
from ui import draw_prompt, draw_dialogue_box, MainMenu, WorldMap, SettingsMenu
from level_map import LEVEL_1_MAP, LEVEL_2_MAP, LEVEL_3_MAP, LEVEL_4_MAP, LEVEL_5_MAP, LEVEL_6_MAP

# --- GLOBAL DURUMLAR ---
CURRENT_STATE = STATE_MENU
CURRENT_LEVEL_ID = 1
DIALOGUE_MODE = None 
DIALOGUE_TARGET_NPC = None

party = []          
particle_group = pygame.sprite.Group()

TRANSITION_RADIUS = 0
MAX_RADIUS = int(math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)) 
TRANSITION_SPEED = 25 
TRANSITION_ANGLE = 0
IS_TRANSITIONING = False

# UI
main_menu = None
world_map = None
settings_menu = None

# --- PARALLAX ---
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

# --- SU FİZİĞİ SİMÜLASYONU ---
def simulate_water_flow(string_map):
    grid = [list(row) for row in string_map]
    if not grid: return []
    
    max_cols = max(len(row) for row in grid)
    for row in grid:
        if len(row) < max_cols:
            row.extend([' '] * (max_cols - len(row)))
            
    rows = len(grid)
    cols = max_cols
    
    for _ in range(10): 
        new_grid = [row[:] for row in grid]
        changed = False
        
        for r in range(rows - 1): 
            for c in range(1, cols - 1):
                if grid[r][c] == 'W':
                    if grid[r+1][c] == ' ':
                        new_grid[r+1][c] = 'W'
                        changed = True
                    elif grid[r+1][c] != ' ':
                        if grid[r][c-1] == ' ':
                            new_grid[r][c-1] = 'W'
                            changed = True
                        if grid[r][c+1] == ' ':
                            new_grid[r][c+1] = 'W'
                            changed = True
                            
        grid = new_grid
        if not changed: break

    return grid

def create_level(level_map, level_num, party_list):
    processed_map = simulate_water_flow(level_map)

    tiles, hazards, npcs, enemies, flags, web_items, wave_grass = (pygame.sprite.Group() for _ in range(7))
    owned_types = [p.char_type for p in party_list]
    grapple_owned = any(p.has_grapple for p in party_list)

    for r, row in enumerate(processed_map):
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
    global CURRENT_STATE, DIALOGUE_OPTION, CURRENT_LEVEL_ID, TRANSITION_RADIUS, party, IS_TRANSITIONING, main_menu, world_map, settings_menu
    global DIALOGUE_MODE, DIALOGUE_TARGET_NPC

    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION])
    
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Chick: Going To Chicken Land")
    clock = pygame.time.Clock()
    
    try: ui_font = pygame.font.Font('assets/font.ttf', 20)
    except: ui_font = pygame.font.SysFont("Arial", 20, bold=True)
    
    parallax_bg = ParallaxBackground()
    main_menu = MainMenu()
    world_map = WorldMap()
    settings_menu = SettingsMenu()

    # --- TEK OYUNCULU BAŞLANGIÇ ---
    p1 = Player(200, 500, char_type='chicken', p_index=1, input_scheme='ARROWS')
    party = [p1] 
    active_index = 0
    
    tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group, wave_grass_group = (pygame.sprite.Group() for _ in range(7))
    scroll_x = 0
    
    while True:
        if CURRENT_STATE == STATE_GAME: pygame.mouse.set_visible(False)
        else: pygame.mouse.set_visible(True)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(), sys.exit()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if CURRENT_STATE == STATE_GAME: CURRENT_STATE = STATE_MAP 
                elif CURRENT_STATE == STATE_MAP: CURRENT_STATE = STATE_MENU 
                elif CURRENT_STATE == STATE_SETTINGS: CURRENT_STATE = STATE_MENU

            # --- STATE MACHINES ---
            if CURRENT_STATE == STATE_MENU:
                action = main_menu.handle_input(event)
                if action == "YENI OYUN": CURRENT_STATE = STATE_MAP
                elif action == "AYARLAR": CURRENT_STATE = STATE_SETTINGS
                elif action == "CIKIS": pygame.quit(), sys.exit()
            
            elif CURRENT_STATE == STATE_SETTINGS:
                res = settings_menu.handle_input(event)
                if res == "BACK": CURRENT_STATE = STATE_MENU

            elif CURRENT_STATE == STATE_MAP:
                selected_level = world_map.handle_input(event)
                if selected_level:
                    CURRENT_LEVEL_ID = selected_level
                    tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group, wave_grass_group = reset_game(party, CURRENT_LEVEL_ID)
                    CURRENT_STATE = STATE_GAME
            
            elif CURRENT_STATE == STATE_GAME:
                # Aktif oyuncu yönetimi
                if active_index >= len(party): active_index = 0
                active_player = party[active_index]

                if event.type == pygame.KEYDOWN:
                    # Karakter Değiştirme
                    if event.key == pygame.K_c:
                         single_players = [p for p in party if p.input_scheme == CONTROLS['ARROWS']]
                         if len(single_players) > 1:
                             active_player.grapple_state = 'none'
                             active_index = (active_index + 1) % len(party)
                             # WASD oyuncusunu atla
                             while party[active_index].input_scheme == CONTROLS['WASD']:
                                 active_index = (active_index + 1) % len(party)

                    # [DÜZELTME] Zıplama Kontrolü - Sadece Aktif Karakter
                    for i, p in enumerate(party):
                        controls = p.input_scheme
                        if event.key == controls['jump'] and p.grapple_state != 'aiming':
                            # Eğer karakter WASD kullanıyorsa (Co-op) HER ZAMAN zıplar
                            # Eğer ARROWS kullanıyorsa SADECE sırası gelen (active_index) zıplar
                            if p.scheme_name == 'WASD' or (p.scheme_name == 'ARROWS' and i == active_index):
                                p.jump()

                    # Etkileşim "E" Tuşu
                    if event.key == pygame.K_e:
                        for npc in npc_group:
                            if npc.check_proximity(party[0].rect, scroll_x, screen, False):
                                CURRENT_STATE = 'dialogue'
                                DIALOGUE_MODE = 'recruit'
                                DIALOGUE_TARGET_NPC = npc
                                DIALOGUE_OPTION = 0
                                break
                
                if event.type == pygame.KEYUP:
                    # [DÜZELTME] Ağ Atma - Sadece Aktif Karakter
                    for i, p in enumerate(party):
                        if event.key == p.input_scheme['grapple']:
                             # Yine aynı kontrol: WASD ise veya sırası gelen ARROWS ise
                             if p.scheme_name == 'WASD' or (p.scheme_name == 'ARROWS' and i == active_index):
                                if p.grapple_state == 'aiming': p.fire_grapple(tile_group)

            # --- DİYALOG KONTROLLERİ ---
            elif CURRENT_STATE == 'dialogue':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: DIALOGUE_OPTION = 0
                    elif event.key == pygame.K_RIGHT: DIALOGUE_OPTION = 1
                    elif event.key == pygame.K_RETURN:
                        # 1. SORU: Katılsın mı?
                        if DIALOGUE_MODE == 'recruit':
                            if DIALOGUE_OPTION == 0: # EVET
                                DIALOGUE_MODE = 'coop_ask'
                                DIALOGUE_OPTION = 0
                            else: # HAYIR
                                CURRENT_STATE = STATE_GAME 
                        
                        # 2. SORU: Co-op?
                        elif DIALOGUE_MODE == 'coop_ask':
                            new_scheme = 'ARROWS'
                            if DIALOGUE_OPTION == 0: # EVET (Co-op)
                                new_scheme = 'WASD'
                            else: # HAYIR (Single)
                                new_scheme = 'ARROWS'
                            
                            new_p_index = len(party) + 1
                            new_char = Player(DIALOGUE_TARGET_NPC.rect.x, DIALOGUE_TARGET_NPC.rect.y, 
                                            char_type=DIALOGUE_TARGET_NPC.variant, 
                                            p_index=new_p_index, 
                                            input_scheme=new_scheme)
                            
                            if party[0].has_grapple: new_char.has_grapple = True
                            party.append(new_char)
                            DIALOGUE_TARGET_NPC.kill()
                            
                            CURRENT_STATE = STATE_GAME

        # --- UPDATE & DRAW ---
        if CURRENT_STATE == STATE_MENU:
            main_menu.draw(screen)

        elif CURRENT_STATE == STATE_SETTINGS:
            settings_menu.draw(screen)

        elif CURRENT_STATE == STATE_MAP:
            screen.fill((20, 20, 40)) 
            world_map.draw(screen)

        elif CURRENT_STATE == STATE_GAME or CURRENT_STATE == 'dialogue':
            targets = [p for p in party if not p.is_dead]
            if targets:
                avg_x = sum(p.rect.centerx for p in targets) / len(targets)
                target_scroll = avg_x - SCREEN_WIDTH / 2
            else: target_scroll = 0
                
            if target_scroll < 0: target_scroll = 0
            scroll_x += (target_scroll - scroll_x) * 0.1

            if CURRENT_STATE == STATE_GAME:
                wave_grass_group.update(party)
                particle_group.update()
                
                any_dead = False
                for i, p in enumerate(party):
                    # Karakter update ederken 'is_active' bilgisini gönderiyoruz
                    is_active = (i == active_index)
                    p.update(tile_group, hazard_group, 'playing', party, particle_group, is_active)
                    
                    if pygame.sprite.spritecollide(p, enemy_group, False): p.is_dead = True
                    if p.is_dead: any_dead = True
                    if pygame.sprite.spritecollide(p, web_group, True):
                        for member in party: member.has_grapple = True

                for enemy in enemy_group: enemy.update(tile_group, party[0])
                web_group.update()

            if parallax_bg: parallax_bg.draw(screen, scroll_x)
            else: screen.fill(SKY_BLUE)
            
            for group in [tile_group, hazard_group, flag_group, enemy_group, web_group, npc_group, wave_grass_group, particle_group]:
                for sprite in group:
                    if hasattr(sprite, 'draw_scrolled'): sprite.draw_scrolled(screen, scroll_x)
            
            for p in party: p.draw(screen, scroll_x)
            
            if CURRENT_STATE == STATE_GAME:
                for npc in npc_group:
                    if npc.check_proximity(party[0].rect, scroll_x, screen, False):
                         draw_prompt(screen, npc.rect.centerx - scroll_x, npc.rect.top - 20)

            if CURRENT_STATE == 'dialogue':
                if DIALOGUE_MODE == 'recruit':
                    draw_dialogue_box(screen, DIALOGUE_OPTION, 
                                      "YENİ KARAKTER!", 
                                      "Bu karakteri ekibe almak istiyor musun?",
                                      "EVET", "HAYIR")
                elif DIALOGUE_MODE == 'coop_ask':
                    draw_dialogue_box(screen, DIALOGUE_OPTION, 
                                      "CO-OP MODU?", 
                                      "İkinci oyuncu bu karakteri yönetmek ister mi?",
                                      "EVET (WASD ile Oyna)", "HAYIR (Değişmeli Oyna)")

            if CURRENT_STATE == STATE_GAME:
                all_finished = True
                for p in party:
                    if not pygame.sprite.spritecollide(p, flag_group, False):
                        all_finished = False
                        break
                if all_finished: IS_TRANSITIONING = True 

                if any_dead:
                     tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group, wave_grass_group = reset_game(party, CURRENT_LEVEL_ID)

            info_text = f"BOLUM: {CURRENT_LEVEL_ID}"
            screen.blit(ui_font.render(info_text, True, (0,0,0)), (20, 20))

            if IS_TRANSITIONING:
                TRANSITION_RADIUS += TRANSITION_SPEED
                draw_transition(screen)
                if TRANSITION_RADIUS > MAX_RADIUS * 1.5:
                    IS_TRANSITIONING = False
                    TRANSITION_RADIUS = 0
                    world_map.unlock_next_level(CURRENT_LEVEL_ID)
                    CURRENT_STATE = STATE_MAP

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()