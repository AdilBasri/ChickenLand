import pygame
import sys
import math
from settings import *
from sprites import Tile, Flag
from player import Player, Companion
from npcs import NPC, Enemy
from ui import draw_prompt, draw_dialogue_box
from level_map import LEVEL_1_MAP, LEVEL_2_MAP, LEVEL_3_MAP

# --- GLOBAL DURUMLAR ---
GAME_STATE = 'playing'   # playing, dialogue, transition_out, transition_in
DIALOGUE_OPTION = 0 
COMPANION_ACTIVE = False
CURRENT_LEVEL = 1

# --- GEÇİŞ ANİMASYONU DEĞİŞKENLERİ ---
TRANSITION_RADIUS = 0
# Ekran köşegeni kadar büyüsün ki tam kaplasın
MAX_RADIUS = int(math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)) 
TRANSITION_SPEED = 25 
TRANSITION_ANGLE = 0

def create_level(level_map):
    tiles = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    npcs = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    flags = pygame.sprite.Group()

    for row_index, row in enumerate(level_map):
        for col_index, cell in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            if cell == 'X': tiles.add(Tile(x, y, 'grass'))
            elif cell == 'T': tiles.add(Tile(x, y, 'dirt'))
            elif cell == 'K': tiles.add(Tile(x, y, 'box'))
            elif cell == 'W': hazards.add(Tile(x, y, 'water'))
            elif cell == 'N': npcs.add(NPC(x, y))     # Hikaye Karakteri
            elif cell == 'D': enemies.add(Enemy(x, y)) # Düşman (Köpek)
            elif cell == 'F': flags.add(Flag(x, y))    # Bölüm Sonu Bayrağı
            
    return tiles, hazards, npcs, enemies, flags

def reset_game(player, companion_group, npc_group, enemy_group, flag_group, level_map):
    # Oyuncuyu başlangıca al
    player.rect.topleft = player.start_pos
    player.velocity = pygame.math.Vector2(0, 0)
    player.is_dead = False
    
    # Yoldaş durumunu kontrol et
    has_companion = COMPANION_ACTIVE 
    
    # Eski grupleri temizle
    companion_group.empty()
    npc_group.empty()
    enemy_group.empty()
    flag_group.empty()
    
    # Yeni harita objelerini oluştur
    new_tiles, new_hazards, new_npcs, new_enemies, new_flags = create_level(level_map)
    
    # Sprite gruplarını güncelle
    for npc in new_npcs: npc_group.add(npc)
    for enemy in new_enemies: enemy_group.add(enemy)
    for flag in new_flags: flag_group.add(flag)
    
    # Eğer yoldaşımız zaten varsa (önceki levelden geldiyse), oyuncunun yanında doğsun
    if has_companion:
        # Oyuncunun 50 piksel solunda doğsun
        companion = Companion(player.rect.x - 50, player.rect.y)
        companion.target_player = player
        companion_group.add(companion)

    global GAME_STATE
    GAME_STATE = 'playing'
    
    # Yeni oluşturulan grupları ve scroll değerini (0) döndür
    return 0, new_tiles, new_hazards, new_npcs, new_enemies, new_flags

def draw_transition(screen):
    global TRANSITION_RADIUS, TRANSITION_ANGLE
    
    # Dönen siyah kareyi çiz
    rect_size = TRANSITION_RADIUS
    if rect_size < 0: rect_size = 0 # Negatif boyut hatasını önle
    
    surface = pygame.Surface((int(rect_size), int(rect_size)))
    surface.fill((0,0,0)) # Siyah
    
    # Kareyi merkezden döndür
    rotated_surface = pygame.transform.rotate(surface, TRANSITION_ANGLE)
    rect = rotated_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    
    screen.blit(rotated_surface, rect)
    TRANSITION_ANGLE += 5

def main():
    global GAME_STATE, DIALOGUE_OPTION, COMPANION_ACTIVE, CURRENT_LEVEL, TRANSITION_RADIUS
    
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Chick: Going To Chicken Land")
    clock = pygame.time.Clock()

    # BAŞLANGIÇ: LEVEL 1
    current_map = LEVEL_1_MAP
    tile_group, hazard_group, npc_group, enemy_group, flag_group = create_level(current_map)
    
    player = Player(200, 800)
    companion_group = pygame.sprite.GroupSingle()

    scroll_x = 0
    can_interact = False

    while True:
        # --- EVENT LOOP ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(), sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(), sys.exit()
                
                # OYNANIŞ MODU TUŞLARI
                if GAME_STATE == 'playing':
                    if event.key == pygame.K_SPACE: player.jump()
                    
                    # NPC ile Etkileşim
                    if event.key == pygame.K_e and can_interact:
                        GAME_STATE = 'dialogue'
                        player.velocity.x = 0 
                        if companion_group.sprite: companion_group.sprite.velocity.x = 0

                # DİYALOG MODU TUŞLARI
                elif GAME_STATE == 'dialogue':
                    if event.key == pygame.K_LEFT: DIALOGUE_OPTION = 0
                    if event.key == pygame.K_RIGHT: DIALOGUE_OPTION = 1
                    if event.key == pygame.K_RETURN:
                        # Seçim Yapıldı
                        if DIALOGUE_OPTION == 0: # EVET
                            COMPANION_ACTIVE = True
                            if npc_group:
                                npc = npc_group.sprites()[0]
                                # Yoldaş Duck'ı oluştur
                                companion = Companion(npc.rect.centerx, npc.rect.bottom - VISUAL_Y_OFFSET - CHAR_HEIGHT)
                                companion.target_player = player
                                companion_group.add(companion)
                                npc_group.empty() # NPC'yi sahneden kaldır
                        GAME_STATE = 'playing'

        # --- UPDATE ---
        if GAME_STATE == 'playing':
            # Kamera Takibi
            target_scroll = player.rect.centerx - SCREEN_WIDTH / 2
            if target_scroll < 0: target_scroll = 0
            scroll_x = target_scroll

            # Karakter Güncellemeleri
            player.update(tile_group, hazard_group, GAME_STATE)
            if companion_group.sprite:
                companion_group.sprite.update(tile_group, hazard_group, GAME_STATE)

            # Düşman Güncellemesi (Oyuncuyu kovalasın)
            for enemy in enemy_group: enemy.update(tile_group, player)

            # --- ÇARPIŞMA KONTROLLERİ ---
            
            # 1. Oyuncu vs Düşman
            if pygame.sprite.spritecollide(player, enemy_group, False): 
                player.is_dead = True
                
            # 2. Yoldaş vs Düşman (YENİ)
            if companion_group.sprite:
                if pygame.sprite.spritecollide(companion_group.sprite, enemy_group, False):
                    companion_group.sprite.is_dead = True

            # 3. Bölüm Sonu (Bayrak)
            if pygame.sprite.spritecollide(player, flag_group, False):
                GAME_STATE = 'transition_out' 
                TRANSITION_RADIUS = 0 

            # --- ÖLÜM VE RESET ---
            # Eğer Oyuncu YA DA Yoldaş ölürse reset at
            if player.is_dead or (companion_group.sprite and companion_group.sprite.is_dead):
                scroll_x, tile_group, hazard_group, npc_group, enemy_group, flag_group = reset_game(
                    player, companion_group, npc_group, enemy_group, flag_group, current_map
                )

        # --- ÇİZİM ---
        screen.fill(SKY_BLUE)
        
        # Objeleri kaydırarak çiz
        for tile in tile_group: tile.draw_scrolled(screen, scroll_x)
        for hazard in hazard_group: hazard.draw_scrolled(screen, scroll_x)
        for flag in flag_group: flag.draw_scrolled(screen, scroll_x)
        for enemy in enemy_group: enemy.draw_scrolled(screen, scroll_x)
        
        # NPC ve Etkileşim Uyarısı
        can_interact = False
        for npc in npc_group:
            npc.draw_scrolled(screen, scroll_x)
            if npc.check_proximity(player.rect, scroll_x, screen, COMPANION_ACTIVE):
                draw_prompt(screen, npc.rect.centerx - scroll_x, npc.rect.top - 20)
                can_interact = True

        # Karakterler
        player.draw(screen, scroll_x)
        if companion_group.sprite: companion_group.sprite.draw(screen, scroll_x)

        # Diyalog Kutusu
        if GAME_STATE == 'dialogue':
            draw_dialogue_box(screen, DIALOGUE_OPTION)

        # --- GEÇİŞ ANİMASYONU ---
        if GAME_STATE == 'transition_out':
            # Ekranı kapat (Siyah kare büyür)
            TRANSITION_RADIUS += TRANSITION_SPEED
            draw_transition(screen)
            
            # Ekran tamamen kapandıysa Bölüm Değiştir
            if TRANSITION_RADIUS > MAX_RADIUS * 1.5:
                if CURRENT_LEVEL == 1:
                    CURRENT_LEVEL = 2
                    current_map = LEVEL_2_MAP
                    player.start_pos = (200, 800) 
                
                elif CURRENT_LEVEL == 2:
                    CURRENT_LEVEL = 3
                    current_map = LEVEL_3_MAP
                    player.start_pos = (200, 800)
                
                else:
                    print("OYUN BİTTİ! BAŞA DÖNÜLÜYOR...")
                    CURRENT_LEVEL = 1
                    current_map = LEVEL_1_MAP
                    player.start_pos = (200, 800)
                    COMPANION_ACTIVE = False # Başa dönünce yoldaş sıfırlanır

                # Yeni haritayı yükle
                scroll_x, tile_group, hazard_group, npc_group, enemy_group, flag_group = reset_game(
                    player, companion_group, npc_group, enemy_group, flag_group, current_map
                )
                
                GAME_STATE = 'transition_in'

        if GAME_STATE == 'transition_in':
            # Ekranı aç (Siyah kare küçülür)
            TRANSITION_RADIUS -= TRANSITION_SPEED
            draw_transition(screen)
            if TRANSITION_RADIUS <= 0:
                GAME_STATE = 'playing'

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()