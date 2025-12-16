import pygame
import sys
import math
from settings import *
from sprites import Tile, Flag, WebItem
from player import Player
from npcs import NPC, Enemy
from ui import draw_prompt, draw_dialogue_box
from level_map import LEVEL_1_MAP, LEVEL_2_MAP, LEVEL_3_MAP, LEVEL_4_MAP

# --- GLOBAL DURUMLAR ---
GAME_STATE = 'playing'
DIALOGUE_OPTION = 0 
CURRENT_LEVEL = 1

# --- PARTİ SİSTEMİ ---
party = []          
active_index = 0    

# --- GEÇİŞ ANİMASYONU ---
TRANSITION_RADIUS = 0
MAX_RADIUS = int(math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)) 
TRANSITION_SPEED = 25 
TRANSITION_ANGLE = 0

bg_image = None

def load_background():
    global bg_image
    try:
        bg = pygame.image.load('assets/background.png').convert()
        bg_image = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except FileNotFoundError:
        bg_image = None

def draw_background(screen, scroll_x):
    if bg_image:
        rel_x = (scroll_x * 0.5) % SCREEN_WIDTH
        screen.blit(bg_image, (-rel_x, 0))
        screen.blit(bg_image, (-rel_x + SCREEN_WIDTH, 0))
    else:
        screen.fill(SKY_BLUE)

def create_level(level_map, level_num):
    tiles = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    npcs = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    flags = pygame.sprite.Group()
    web_items = pygame.sprite.Group() 

    for row_index, row in enumerate(level_map):
        for col_index, cell in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            if cell == 'X': tiles.add(Tile(x, y, 'grass'))
            elif cell == 'T': tiles.add(Tile(x, y, 'dirt'))
            elif cell == 'K': tiles.add(Tile(x, y, 'box'))
            elif cell == 'W': hazards.add(Tile(x, y, 'water'))
            elif cell == 'N': 
                variant = 'duck'
                if level_num == 4: variant = 'seagull'
                npcs.add(NPC(x, y, variant))     
            elif cell == 'D': enemies.add(Enemy(x, y)) 
            elif cell == 'F': flags.add(Flag(x, y))
            elif cell == 'S': web_items.add(WebItem(x, y)) 
            
    return tiles, hazards, npcs, enemies, flags, web_items

def reset_game(party_list, npc_group, enemy_group, flag_group, web_group, level_map, level_num):
    start_x, start_y = party_list[0].start_pos
    
    for i, p in enumerate(party_list):
        p.rect.topleft = (start_x - (i * 30), start_y)
        p.velocity = pygame.math.Vector2(0, 0)
        p.is_dead = False
        p.grapple_state = 'none' 
    
    npc_group.empty()
    enemy_group.empty()
    flag_group.empty()
    web_group.empty()
    
    new_tiles, new_hazards, new_npcs, new_enemies, new_flags, new_webs = create_level(level_map, level_num)
    
    for npc in new_npcs: npc_group.add(npc)
    for enemy in new_enemies: enemy_group.add(enemy)
    for flag in new_flags: flag_group.add(flag)
    for web in new_webs: web_group.add(web)
    
    global GAME_STATE
    GAME_STATE = 'playing'
    
    return 0, new_tiles, new_hazards, new_npcs, new_enemies, new_flags, new_webs

def draw_transition(screen):
    global TRANSITION_RADIUS, TRANSITION_ANGLE
    rect_size = TRANSITION_RADIUS
    if rect_size < 0: rect_size = 0
    surface = pygame.Surface((int(rect_size), int(rect_size)))
    surface.fill(TRANSITION_COLOR)
    rotated_surface = pygame.transform.rotate(surface, TRANSITION_ANGLE)
    rect = rotated_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(rotated_surface, rect)
    TRANSITION_ANGLE += 5

def main():
    global GAME_STATE, DIALOGUE_OPTION, CURRENT_LEVEL, TRANSITION_RADIUS, active_index, party
    
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Chick: Going To Chicken Land")
    clock = pygame.time.Clock()

    try:
        ui_font = pygame.font.Font('assets/font.ttf', 20)
    except FileNotFoundError:
        ui_font = pygame.font.SysFont("Arial", 20, bold=True)
    
    load_background()

    # BAŞLANGIÇ
    current_map = LEVEL_1_MAP
    tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group = create_level(current_map, CURRENT_LEVEL)
    
    party = []
    p1 = Player(200, 800, char_type='chicken', p_index=1)
    party.append(p1)
    active_index = 0

    scroll_x = 0
    can_interact = False

    while True:
        if active_index >= len(party): active_index = 0
        active_player = party[active_index]

        # --- EVENT LOOP ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(), sys.exit()
            
            # --- KEY DOWN ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(), sys.exit()
                
                if event.key == pygame.K_c and GAME_STATE == 'playing':
                    if len(party) > 1:
                        active_player.grapple_state = 'none' # Değiştirince bırak
                        active_index = (active_index + 1) % len(party)

                if GAME_STATE == 'playing':
                    # SPACE TUŞU:
                    # 1. Eğer ağ 'active' ise -> Bırak ve Zıpla (Release)
                    # 2. Eğer ağ yoksa veya 'none' ise -> Nişan almayı başlatır (Player.get_input içinde)
                    if event.key == pygame.K_SPACE:
                        if active_player.grapple_state == 'active':
                            active_player.release_grapple()
                        # Normal zıplama için UP tuşu kullanılıyor artık
                        
                    if event.key == pygame.K_UP: 
                        active_player.jump()
                    
                    if event.key == pygame.K_e and can_interact:
                        GAME_STATE = 'dialogue'
                        for p in party: p.velocity.x = 0

                elif GAME_STATE == 'dialogue':
                    if event.key == pygame.K_LEFT: DIALOGUE_OPTION = 0
                    if event.key == pygame.K_RIGHT: DIALOGUE_OPTION = 1
                    if event.key == pygame.K_RETURN:
                        if DIALOGUE_OPTION == 0: 
                            if npc_group:
                                npc = npc_group.sprites()[0]
                                new_p_index = len(party) + 1
                                new_type = 'duck'
                                if CURRENT_LEVEL == 4: new_type = 'seagull'
                                new_char = Player(npc.rect.x, npc.rect.y, char_type=new_type, p_index=new_p_index)
                                party.append(new_char)
                                npc_group.empty()
                        GAME_STATE = 'playing'
            
            # --- KEY UP ---
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    # Tuş bırakılınca: Nişan alıyorsak fırlat
                    if active_player.has_grapple and active_player.grapple_state == 'aiming':
                        active_player.fire_grapple(tile_group)
                        if active_player.grapple_state != 'active':
                            active_player.grapple_state = 'none'

        # --- UPDATE ---
        if GAME_STATE == 'playing':
            target_scroll = active_player.rect.centerx - SCREEN_WIDTH / 2
            if target_scroll < 0: target_scroll = 0
            scroll_x += (target_scroll - scroll_x) * 0.1

            any_dead = False
            for p in party:
                p.update(tile_group, hazard_group, GAME_STATE, (p == active_player), party)
                
                hits = pygame.sprite.spritecollide(p, web_group, True)
                for hit in hits:
                    p.has_grapple = True 
                
                if pygame.sprite.spritecollide(p, enemy_group, False):
                    p.is_dead = True
                
                if p.is_dead:
                    any_dead = True

            for enemy in enemy_group: enemy.update(tile_group, active_player)
            web_group.update()

            all_players_finished = True
            for p in party:
                if not pygame.sprite.spritecollide(p, flag_group, False):
                    all_players_finished = False
                    break
            
            if all_players_finished:
                GAME_STATE = 'transition_out' 
                TRANSITION_RADIUS = 0 

            if any_dead:
                scroll_x, tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group = reset_game(
                    party, npc_group, enemy_group, flag_group, web_group, current_map, CURRENT_LEVEL
                )

        # --- ÇİZİM ---
        draw_background(screen, scroll_x)
        
        for tile in tile_group: tile.draw_scrolled(screen, scroll_x)
        for hazard in hazard_group: hazard.draw_scrolled(screen, scroll_x)
        for flag in flag_group: flag.draw_scrolled(screen, scroll_x)
        for enemy in enemy_group: enemy.draw_scrolled(screen, scroll_x)
        for web in web_group: web.draw_scrolled(screen, scroll_x)
        
        can_interact = False
        for npc in npc_group:
            npc.draw_scrolled(screen, scroll_x)
            already_recruited = False
            if npc.check_proximity(active_player.rect, scroll_x, screen, already_recruited):
                draw_prompt(screen, npc.rect.centerx - scroll_x, npc.rect.top - 20)
                can_interact = True

        for p in party:
            p.draw(screen, scroll_x)

        if GAME_STATE == 'dialogue':
            draw_dialogue_box(screen, DIALOGUE_OPTION)

        finished_count = sum(1 for p in party if pygame.sprite.spritecollide(p, flag_group, False))
        grapple_status = "VAR" if active_player.has_grapple else "YOK"
        info_text = f"Ekip: {len(party)} | Hedef: {finished_count}/{len(party)} | P{active_player.p_index} | Ağ: {grapple_status}"
        
        text_surface = ui_font.render(info_text, True, (0, 0, 0)) 
        screen.blit(text_surface, (20, 20))

        if GAME_STATE == 'transition_out':
            TRANSITION_RADIUS += TRANSITION_SPEED
            draw_transition(screen)
            
            if TRANSITION_RADIUS > MAX_RADIUS * 1.5:
                if CURRENT_LEVEL == 1:
                    CURRENT_LEVEL = 2
                    current_map = LEVEL_2_MAP
                elif CURRENT_LEVEL == 2:
                    CURRENT_LEVEL = 3
                    current_map = LEVEL_3_MAP
                elif CURRENT_LEVEL == 3:
                    CURRENT_LEVEL = 4
                    current_map = LEVEL_4_MAP
                else:
                    CURRENT_LEVEL = 1
                    current_map = LEVEL_1_MAP
                
                scroll_x, tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group = reset_game(
                    party, npc_group, enemy_group, flag_group, web_group, current_map, CURRENT_LEVEL
                )
                GAME_STATE = 'transition_in'

        if GAME_STATE == 'transition_in':
            TRANSITION_RADIUS -= TRANSITION_SPEED
            draw_transition(screen)
            if TRANSITION_RADIUS <= 0:
                GAME_STATE = 'playing'

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()