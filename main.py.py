import pygame
import sys
from settings import *
from sprites import Tile, Flag
from player import Player, Companion
from npcs import NPC, Enemy # Enemy eklendi
from ui import draw_prompt, draw_dialogue_box
from level_map import LEVEL_MAP 

# --- GLOBAL DURUMLAR ---
GAME_STATE = 'playing'
DIALOGUE_OPTION = 0 
COMPANION_ACTIVE = False

def create_level(level_map):
    tiles = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    npcs = pygame.sprite.Group()
    enemies = pygame.sprite.Group() # Düşman grubu
    flags = pygame.sprite.Group()   # Bayrak grubu

    for row_index, row in enumerate(level_map):
        for col_index, cell in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            if cell == 'X': tiles.add(Tile(x, y, 'grass'))
            elif cell == 'T': tiles.add(Tile(x, y, 'dirt'))
            elif cell == 'K': tiles.add(Tile(x, y, 'box')) # KUTULAR GERİ GELDİ
            elif cell == 'W': hazards.add(Tile(x, y, 'water'))
            elif cell == 'N': npcs.add(NPC(x, y))
            elif cell == 'D': enemies.add(Enemy(x, y)) # Düşman
            elif cell == 'F': flags.add(Flag(x, y))    # Bayrak
            
    return tiles, hazards, npcs, enemies, flags

def reset_level(player, companion_group, npc_group, enemy_group, flag_group, level_map):
    player.rect.topleft = player.start_pos
    player.velocity = pygame.math.Vector2(0, 0)
    player.is_dead = False
    
    companion_group.empty()
    npc_group.empty()
    enemy_group.empty()
    flag_group.empty()
    
    new_tiles, new_hazards, new_npcs, new_enemies, new_flags = create_level(level_map)
    for npc in new_npcs: npc_group.add(npc)
    for enemy in new_enemies: enemy_group.add(enemy)
    for flag in new_flags: flag_group.add(flag)
    
    global COMPANION_ACTIVE, GAME_STATE
    COMPANION_ACTIVE = False
    GAME_STATE = 'playing'
    return 0 

def main():
    global GAME_STATE, DIALOGUE_OPTION, COMPANION_ACTIVE
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Chick: Going To Chicken Land")
    clock = pygame.time.Clock()

    # Tüm grupları oluşturuyoruz
    tile_group, hazard_group, npc_group, enemy_group, flag_group = create_level(LEVEL_MAP)
    
    player = Player(200, 800) # Tavuk burada doğacak
    companion_group = pygame.sprite.GroupSingle()

    scroll_x = 0
    can_interact = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(), sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(), sys.exit()
                
                if GAME_STATE == 'playing':
                    if event.key == pygame.K_SPACE: player.jump()
                    if event.key == pygame.K_e and can_interact:
                        GAME_STATE = 'dialogue'
                        player.velocity.x = 0 
                        if companion_group.sprite: companion_group.sprite.velocity.x = 0

                elif GAME_STATE == 'dialogue':
                    if event.key == pygame.K_LEFT: DIALOGUE_OPTION = 0
                    if event.key == pygame.K_RIGHT: DIALOGUE_OPTION = 1
                    if event.key == pygame.K_RETURN:
                        if DIALOGUE_OPTION == 0: # EVET
                            COMPANION_ACTIVE = True
                            if npc_group:
                                npc = npc_group.sprites()[0]
                                companion = Companion(npc.rect.centerx, npc.rect.bottom - VISUAL_Y_OFFSET - CHAR_HEIGHT)
                                companion.target_player = player
                                companion_group.add(companion)
                                npc_group.empty() 
                        GAME_STATE = 'playing'

        # --- UPDATE ---
        if GAME_STATE == 'playing':
            target_scroll = player.rect.centerx - SCREEN_WIDTH / 2
            if target_scroll < 0: target_scroll = 0
            scroll_x = target_scroll

            player.update(tile_group, hazard_group, GAME_STATE)
            if companion_group.sprite:
                companion_group.sprite.update(tile_group, hazard_group, GAME_STATE)

            # Düşman Update
            for enemy in enemy_group:
                enemy.update(tile_group, player)

            # Çarpışma Kontrolleri (Main loop içinde)
            # 1. Düşman ile çarpışma
            if pygame.sprite.spritecollide(player, enemy_group, False):
                player.is_dead = True
                
            # 2. Bayrak ile çarpışma (Bölüm Sonu)
            if pygame.sprite.spritecollide(player, flag_group, False):
                print("BÖLÜM BİTTİ!")
                player.is_dead = True # Şimdilik başa sarıyoruz

            # Resetleme
            if player.is_dead or (companion_group.sprite and companion_group.sprite.is_dead):
                scroll_x = reset_level(player, companion_group, npc_group, enemy_group, flag_group, LEVEL_MAP)

        # --- DRAW ---
        screen.fill(SKY_BLUE)
        for tile in tile_group: tile.draw_scrolled(screen, scroll_x)
        for hazard in hazard_group: hazard.draw_scrolled(screen, scroll_x)
        for flag in flag_group: flag.draw_scrolled(screen, scroll_x) # Bayrak Çiz
        
        can_interact = False
        for npc in npc_group:
            npc.draw_scrolled(screen, scroll_x)
            if npc.check_proximity(player.rect, scroll_x, screen, COMPANION_ACTIVE):
                draw_prompt(screen, npc.rect.centerx - scroll_x, npc.rect.top - 20)
                can_interact = True
        
        # Düşman Çiz
        for enemy in enemy_group:
            enemy.draw_scrolled(screen, scroll_x)

        player.draw(screen, scroll_x)
        if companion_group.sprite:
             companion_group.sprite.draw(screen, scroll_x)

        if GAME_STATE == 'dialogue':
            draw_dialogue_box(screen, DIALOGUE_OPTION)

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()