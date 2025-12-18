import pygame
import sys
import math
from settings import *
from sprites import Tile, Flag, WebItem, WaveGrass
from player import Player
from npcs import NPC, Enemy
from ui import draw_prompt, draw_dialogue_box
from level_map import LEVEL_1_MAP, LEVEL_2_MAP, LEVEL_3_MAP, LEVEL_4_MAP, LEVEL_5_MAP, LEVEL_6_MAP

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

# --- PARALLAX ARKAPLAN SİSTEMİ ---
background_layers = []

def load_background():
    global background_layers
    background_layers = []
    
    # Katman Listesi: (Dosya Adı, Hız Çarpanı)
    # 0.0 = Sabit durur (Gökyüzü)
    # 0.2 = Yavaş hareket eder (Bulutlar)
    # 0.5 = Orta hız (Dağlar)
    # 0.8 = Hızlı (Yakın ağaçlar)
    layers_config = [
        {'file': 'assets/layer_1.png', 'speed': 0.0}, # En arka (Gökyüzü)
        {'file': 'assets/layer_2.png', 'speed': 0.2}, # Uzak Bulutlar
        {'file': 'assets/layer_3.png', 'speed': 0.5}, # Dağlar
    ]

    for layer in layers_config:
        try:
            img = pygame.image.load(layer['file']).convert_alpha()
            # Resmi ekran yüksekliğine göre ölçekle (Orantıyı koruyarak)
            aspect_ratio = img.get_width() / img.get_height()
            new_height = SCREEN_HEIGHT
            new_width = int(new_height * aspect_ratio)
            scaled_img = pygame.transform.scale(img, (new_width, new_height))
            
            background_layers.append({
                'image': scaled_img,
                'speed': layer['speed'],
                'width': new_width
            })
        except FileNotFoundError:
            print(f"UYARI: {layer['file']} bulunamadı. Arkaplan eksik olacak.")

def draw_background(screen, scroll_x):
    # Eğer hiç resim yüklenemediyse düz renk bas
    if not background_layers:
        screen.fill(SKY_BLUE)
        return

    for layer in background_layers:
        speed = layer['speed']
        img = layer['image']
        width = layer['width']
        
        # --- PARALLAX HESABI (DÜZELTİLDİ) ---
        
        # 1. Ne kadar kaydığımızı hesapla
        # (scroll_x * speed) -> Toplam gidilen mesafe
        # % width -> Bu mesafenin resim genişliğine göre modu.
        # Bu bize 0 ile resim_genişliği arasında bir değer verir.
        offset = (scroll_x * speed) % width
        
        # 2. Çizime başlayacağımız X koordinatı.
        # Eksi (-) koyuyoruz çünkü biz sağa giderken resim sola (geriye) kaymalı.
        # Bu sayede resim her zaman ekranın solundan (-width ile 0 arasında) başlar.
        start_x = -offset
        
        # 3. Ekranı doldurana kadar yan yana çiz (Tiling)
        # start_x'ten başlayıp ekranın sonuna kadar (SCREEN_WIDTH) resimleri yan yana diziyoruz.
        # Bu sayede resim küçük olsa bile veya hızlı kaysa bile boşluk kalmaz.
        current_x = start_x
        while current_x < SCREEN_WIDTH:
            screen.blit(img, (current_x, 0))
            current_x += width

def create_level(level_map, level_num, party_list):
    tiles = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    npcs = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    flags = pygame.sprite.Group()
    web_items = pygame.sprite.Group()
    wave_grass = pygame.sprite.Group()

    owned_types = [p.char_type for p in party_list]
    grapple_owned = False
    for p in party_list:
        if p.has_grapple:
            grapple_owned = True
            break

    for row_index, row in enumerate(level_map):
        for col_index, cell in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            
            if cell == 'X': tiles.add(Tile(x, y, 'grass'))
            elif cell == 'T': 
                tiles.add(Tile(x, y, 'dirt'))
                wave_grass.add(WaveGrass(x, y))
            elif cell == 'K': tiles.add(Tile(x, y, 'box'))
            elif cell == 'W': hazards.add(Tile(x, y, 'water'))
            
            elif cell == 'N': 
                target_variant = 'duck' 
                if level_num == 4: target_variant = 'seagull'
                if level_num == 6: target_variant = 'twi' 

                if target_variant not in owned_types:
                    npcs.add(NPC(x, y, target_variant))
            
            elif cell == 'D': enemies.add(Enemy(x, y)) 
            elif cell == 'F': flags.add(Flag(x, y))
            
            elif cell == 'S': 
                if not grapple_owned:
                    web_items.add(WebItem(x, y)) 
            
    return tiles, hazards, npcs, enemies, flags, web_items, wave_grass

def reset_game(party_list, npc_group, enemy_group, flag_group, web_group, wave_grass_group, level_map, level_num):
    start_x = 200
    start_y = 500 
    
    for i, p in enumerate(party_list):
        p.rect.topleft = (start_x - (i * 30), start_y)
        p.velocity = pygame.math.Vector2(0, 0)
        p.is_dead = False
        p.grapple_state = 'none' 
        p.rope_length = 0
        p.grapple_point = None
    
    npc_group.empty()
    enemy_group.empty()
    flag_group.empty()
    web_group.empty()
    wave_grass_group.empty()
    
    new_tiles, new_hazards, new_npcs, new_enemies, new_flags, new_webs, new_wave_grass = create_level(level_map, level_num, party_list)
    
    for npc in new_npcs: npc_group.add(npc)
    for enemy in new_enemies: enemy_group.add(enemy)
    for flag in new_flags: flag_group.add(flag)
    for web in new_webs: web_group.add(web)
    for wg in new_wave_grass: wave_grass_group.add(wg)
    
    global GAME_STATE
    GAME_STATE = 'playing'
    
    return 0, new_tiles, new_hazards, new_npcs, new_enemies, new_flags, new_webs, new_wave_grass

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
    
    # Arkaplanları yükle
    load_background()

    party = []
    p1 = Player(200, 500, char_type='chicken', p_index=1)
    party.append(p1)
    active_index = 0
    
    current_map = LEVEL_1_MAP
    tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group, wave_grass_group = create_level(current_map, CURRENT_LEVEL, party)

    scroll_x = 0
    can_interact = False

    while True:
        if active_index >= len(party): active_index = 0
        active_player = party[active_index]

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(), sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(), sys.exit()
                
                if event.key == pygame.K_c and GAME_STATE == 'playing':
                    if len(party) > 1:
                        active_player.grapple_state = 'none' 
                        active_index = (active_index + 1) % len(party)

                if GAME_STATE == 'playing':
                    if event.key == pygame.K_UP:
                         if active_player.grapple_state != 'aiming':
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
                                if CURRENT_LEVEL == 6: new_type = 'twi' 
                                
                                new_char = Player(npc.rect.x, npc.rect.y, char_type=new_type, p_index=new_p_index)
                                
                                if active_player.has_grapple: new_char.has_grapple = True
                                
                                party.append(new_char)
                                npc_group.empty() 
                        GAME_STATE = 'playing'
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    if active_player.grapple_state == 'aiming':
                        active_player.fire_grapple(tile_group)

        if GAME_STATE == 'playing':
            target_scroll = active_player.rect.centerx - SCREEN_WIDTH / 2
            if target_scroll < 0: target_scroll = 0
            scroll_x += (target_scroll - scroll_x) * 0.1

            wave_grass_group.update(party)

            any_dead = False
            for p in party:
                p.update(tile_group, hazard_group, GAME_STATE, (p == active_player), party)
                
                hits = pygame.sprite.spritecollide(p, web_group, True)
                for hit in hits:
                    for member in party:
                        member.has_grapple = True 
                
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
                scroll_x, tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group, wave_grass_group = reset_game(
                    party, npc_group, enemy_group, flag_group, web_group, wave_grass_group, current_map, CURRENT_LEVEL
                )

        # [PARALLAX ÇİZİMİ]
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
            
        # Çimenleri en son çiz
        for wg in wave_grass_group: wg.draw_scrolled(screen, scroll_x)

        if GAME_STATE == 'dialogue':
            draw_dialogue_box(screen, DIALOGUE_OPTION)

        finished_count = sum(1 for p in party if pygame.sprite.spritecollide(p, flag_group, False))
        grapple_status = "VAR" if active_player.has_grapple else "YOK"
        info_text = f"P{active_player.p_index} | Ag: {grapple_status} | Hareket: OK TUSLARI | Ag: SPACE"
        
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
                elif CURRENT_LEVEL == 4:
                    CURRENT_LEVEL = 5
                    current_map = LEVEL_5_MAP
                elif CURRENT_LEVEL == 5:
                    CURRENT_LEVEL = 6
                    current_map = LEVEL_6_MAP
                else:
                    CURRENT_LEVEL = 1
                    current_map = LEVEL_1_MAP
                    
                    party = []
                    p1 = Player(200, 500, char_type='chicken', p_index=1)
                    party.append(p1)
                    active_index = 0
                
                scroll_x, tile_group, hazard_group, npc_group, enemy_group, flag_group, web_group, wave_grass_group = reset_game(
                    party, npc_group, enemy_group, flag_group, web_group, wave_grass_group, current_map, CURRENT_LEVEL
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