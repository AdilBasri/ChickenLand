import pygame
import math
import os
from settings import *

# --- YARDIMCI ---
def draw_prompt(screen, x, y):
    prompt_rect = pygame.Rect(x - 20, y - 40, 40, 40)
    pygame.draw.rect(screen, (255, 255, 255), prompt_rect, border_radius=5)
    pygame.draw.rect(screen, (0, 0, 0), prompt_rect, 2, border_radius=5)
    font = pygame.font.SysFont("Arial", 24, bold=True)
    text_surf = font.render("E", True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=prompt_rect.center)
    screen.blit(text_surf, text_rect)

def draw_dialogue_box(screen, selected_option, title_text, desc_text, opt1_text, opt2_text):
    box_rect = pygame.Rect(50, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 100, 130)
    pygame.draw.rect(screen, UI_BG_COLOR, box_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), box_rect, 2, border_radius=10)
    
    font_title = pygame.font.SysFont("Arial", 22, bold=True)
    font_desc = pygame.font.SysFont("Arial", 20)
    
    title = font_title.render(title_text, True, SELECTION_COLOR)
    screen.blit(title, (box_rect.x + 20, box_rect.y + 15))
    
    desc = font_desc.render(desc_text, True, TEXT_COLOR)
    screen.blit(desc, (box_rect.x + 20, box_rect.y + 45))
    
    opt1_color = SELECTION_COLOR if selected_option == 0 else TEXT_COLOR
    opt2_color = SELECTION_COLOR if selected_option == 1 else TEXT_COLOR
    
    txt1 = font_desc.render(f"> {opt1_text}", True, opt1_color)
    txt2 = font_desc.render(f"> {opt2_text}", True, opt2_color)
    
    screen.blit(txt1, (box_rect.x + 50, box_rect.y + 90))
    screen.blit(txt2, (box_rect.x + 400, box_rect.y + 90))

# --- ENVANTER (TAB) SİSTEMİ ---
class InventoryOverlay:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.dragging_item = None # 'grapple'
        self.drag_source_index = -1
        try:
            raw_icon = pygame.image.load('assets/web.png').convert_alpha()
            self.icon_surf = pygame.transform.scale(raw_icon, (40, 40))
        except:
            self.icon_surf = pygame.Surface((40,40))
            self.icon_surf.fill((100,200,255))
            
    def draw(self, screen, party):
        # Arka plan karartma
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        screen.blit(overlay, (0,0))
        
        slot_w, slot_h = 80, 80
        start_x = (SCREEN_WIDTH - (len(party) * (slot_w + 20))) // 2
        y_pos = SCREEN_HEIGHT // 2
        
        self.slots = [] # Çarpışma kontrolü için rect'leri sakla
        
        mouse_pos = pygame.mouse.get_pos()
        
        title = self.font.render("YETENEK DAGITIMI (SURUKLE VE BIRAK)", True, (255,255,255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, y_pos - 150))
        
        for i, player in enumerate(party):
            x = start_x + i * (slot_w + 20)
            
            # Karakter Resmi
            try:
                char_img = player.animations['walk'][0]
                char_ratio = char_img.get_width() / char_img.get_height()
                display_h = 100
                display_w = int(display_h * char_ratio)
                scaled_char = pygame.transform.scale(char_img, (display_w, display_h))
                
                # Ortala
                char_rect = scaled_char.get_rect(center=(x + slot_w//2, y_pos - 60))
                screen.blit(scaled_char, char_rect)
            except: pass
            
            # Slot Kutusu
            slot_rect = pygame.Rect(x, y_pos, slot_w, slot_h)
            self.slots.append({'rect': slot_rect, 'player': player, 'index': i})
            
            pygame.draw.rect(screen, SLOT_BG_COLOR, slot_rect, border_radius=5)
            pygame.draw.rect(screen, SLOT_BORDER_COLOR, slot_rect, 2, border_radius=5)
            
            # Eğer item varsa ve bu slot drag kaynağı değilse çiz
            if player.has_grapple:
                if not (self.dragging_item and self.drag_source_index == i):
                    icon_rect = self.icon_surf.get_rect(center=slot_rect.center)
                    screen.blit(self.icon_surf, icon_rect)
                    
        # Sürüklenen İtem
        if self.dragging_item:
            screen.blit(self.icon_surf, (mouse_pos[0] - 20, mouse_pos[1] - 20))
            
    def handle_input(self, event, party):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for slot in self.slots:
                if slot['rect'].collidepoint(mouse_pos):
                    if slot['player'].has_grapple:
                        self.dragging_item = 'grapple'
                        self.drag_source_index = slot['index']
                        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                target_found = False
                for slot in self.slots:
                    if slot['rect'].collidepoint(mouse_pos):
                        # Aynı yere bırakmadıysa
                        if slot['index'] != self.drag_source_index:
                            # Transfer
                            party[self.drag_source_index].has_grapple = False
                            # Eski grapple state'i temizle
                            party[self.drag_source_index].grapple_state = 'none' 
                            
                            # Varsa hedefteki item'ı değiş tokuş yap (Şimdilik sadece 1 item var, o yüzden direkt ver)
                            # Eğer hedefte zaten varsa? Oyun kuralı: 1 item tek kişide.
                            # Ama kod mantığı gereği, tek item varsa sadece transfer olur.
                            slot['player'].has_grapple = True
                            target_found = True
                        else:
                            # Kendi yerine bıraktı, iptal
                            target_found = True # İptal sayılır
                        break
                
                self.dragging_item = None
                self.drag_source_index = -1

# --- AYARLAR MENÜSÜ ---
class SettingsMenu:
    def __init__(self):
        self.options = [
            {'key': 'fullscreen', 'label': 'EKRAN: '},
            {'key': 'volume',     'label': 'SES: '},
            {'key': 'language',   'label': 'DIL: '},
            {'key': 'controls',   'label': 'KONTROL: '}
        ]
        self.selected_index = 0
        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 60, bold=True)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                key = self.options[self.selected_index]['key']
                direction = 1 if event.key == pygame.K_RIGHT else -1
                
                if key == 'fullscreen':
                    GAME_SETTINGS['fullscreen'] = not GAME_SETTINGS['fullscreen']
                    if GAME_SETTINGS['fullscreen']: pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else: pygame.display.set_mode((1280, 720))
                        
                elif key == 'volume':
                    GAME_SETTINGS['volume'] += direction
                    if GAME_SETTINGS['volume'] < 0: GAME_SETTINGS['volume'] = 0
                    if GAME_SETTINGS['volume'] > 10: GAME_SETTINGS['volume'] = 10
                    
                elif key == 'language':
                    GAME_SETTINGS['language'] = 'ENG' if GAME_SETTINGS['language'] == 'TR' else 'TR'
                
            elif event.key == pygame.K_ESCAPE: return "BACK"
        return None

    def draw(self, screen):
        screen.fill((10, 10, 20)) 
        title_surf = self.title_font.render("AYARLAR", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title_surf, title_rect)
        
        for i, opt in enumerate(self.options):
            color = (255, 255, 255)
            if i == self.selected_index: color = SELECTION_COLOR
            
            val_text = ""
            key = opt['key']
            if key == 'fullscreen': val_text = "TAM EKRAN" if GAME_SETTINGS['fullscreen'] else "PENCERE"
            elif key == 'volume': val_text = "|" * GAME_SETTINGS['volume']
            elif key == 'language': val_text = GAME_SETTINGS['language']
            elif key == 'controls': val_text = "P1:OK / P2:WASD"
            
            full_text = f"{opt['label']} < {val_text} >"
            text_surf = self.font.render(full_text, True, color)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 250 + i * 60))
            screen.blit(text_surf, text_rect)
            
        hint = self.font.render("[ESC] GERI DON", True, (100, 100, 100))
        screen.blit(hint, (50, SCREEN_HEIGHT - 50))

# --- ANA MENÜ ---
class MainMenu:
    def __init__(self):
        self.options = ["YENI OYUN", "AYARLAR", "CIKIS"]
        self.selected_index = 0
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 80, bold=True)
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_index]
        return None

    def draw(self, screen):
        screen.fill((20, 20, 40)) 
        title_surf = self.title_font.render("CHICKEN LAND", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(title_surf, title_rect)
        
        for i, option in enumerate(self.options):
            color = (255, 255, 255)
            prefix = ""
            if i == self.selected_index:
                color = (255, 215, 0)
                prefix = "> "
            text_surf = self.font.render(prefix + option, True, color)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 350 + i * 60))
            screen.blit(text_surf, text_rect)

# --- DÜNYA HARİTASI ---
class WorldMap:
    def __init__(self):
        possible_files = ['assets/map.jpg', 'assets/map.png']
        original_img = None
        for f in possible_files:
            if os.path.exists(f):
                try:
                    original_img = pygame.image.load(f).convert()
                    break
                except: continue
        
        if original_img:
            target_height = SCREEN_HEIGHT
            original_w = original_img.get_width()
            original_h = original_img.get_height()
            aspect_ratio = original_w / original_h
            target_width = int(target_height * aspect_ratio)
            self.image = pygame.transform.smoothscale(original_img, (target_width, target_height))
        else:
            self.image = pygame.Surface((3000, SCREEN_HEIGHT))
            self.image.fill((100, 100, 50))
            pygame.draw.line(self.image, (200, 50, 50), (0, 500), (3000, 500), 10)

        self.map_width = self.image.get_width()
        self.map_height = self.image.get_height()
        
        self.scroll_x = 0
        self.target_scroll_x = 0
        self.is_dragging = False
        self.last_mouse_x = 0
        
        self.node_positions_pct = [
            {'id': 1, 'pct': (0.05, 0.75), 'info': 'Wasteland', 'reward': ''},
            {'id': 2, 'pct': (0.15, 0.55), 'info': 'Kemik Vadisi', 'reward': '+1 Duck'},
            {'id': 3, 'pct': (0.30, 0.45), 'info': 'Sinir Kapisi', 'reward': ''},
            {'id': 4, 'pct': (0.45, 0.65), 'info': 'Marti Koprusu', 'reward': '+1 Seagull'},
            {'id': 5, 'pct': (0.60, 0.50), 'info': 'Tavuk Koyu', 'reward': ''},
            {'id': 6, 'pct': (0.75, 0.35), 'info': 'Kraliyet Kalesi', 'reward': '+1 Twi'},
            {'id': 7, 'pct': (0.90, 0.30), 'info': 'Hiz Pisti', 'reward': '+1 Tukan'},
        ]
        
        self.nodes = []
        for n in self.node_positions_pct:
            real_x = int(self.map_width * n['pct'][0])
            real_y = int(self.map_height * n['pct'][1])
            self.nodes.append({
                'id': n['id'],
                'pos': (real_x, real_y),
                'status': 'locked',
                'info': n['info'],
                'reward': n['reward']
            })
            
        self.nodes[0]['status'] = 'unlocked'
        self.current_selection = 0 
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.info_font = pygame.font.SysFont("Arial", 24, bold=True)

    def unlock_next_level(self, completed_level_id):
        if 0 <= completed_level_id - 1 < len(self.nodes):
            self.nodes[completed_level_id - 1]['status'] = 'completed'
            if completed_level_id < len(self.nodes):
                self.nodes[completed_level_id]['status'] = 'unlocked'
                self.current_selection = completed_level_id 
                self.focus_on_node(self.current_selection)

    def focus_on_node(self, node_index):
        node_x = self.nodes[node_index]['pos'][0]
        self.target_scroll_x = node_x - (SCREEN_WIDTH // 2)
        max_scroll = self.map_width - SCREEN_WIDTH
        self.target_scroll_x = max(0, min(self.target_scroll_x, max_scroll))

    def handle_input(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                self.is_dragging = True
                self.last_mouse_x = mouse_pos[0]
                for node in self.nodes:
                    screen_x = node['pos'][0] - self.scroll_x
                    screen_y = node['pos'][1]
                    dist = math.sqrt((mouse_pos[0] - screen_x)**2 + (mouse_pos[1] - screen_y)**2)
                    if dist < 40:
                        if node['status'] != 'locked': return node['id']

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                dx = mouse_pos[0] - self.last_mouse_x
                self.target_scroll_x -= dx 
                self.last_mouse_x = mouse_pos[0]
                self.scroll_x = self.target_scroll_x 

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if self.current_selection < len(self.nodes) - 1:
                    if self.nodes[self.current_selection + 1]['status'] != 'locked':
                        self.current_selection += 1
                        self.focus_on_node(self.current_selection)
            elif event.key == pygame.K_LEFT:
                if self.current_selection > 0:
                    self.current_selection -= 1
                    self.focus_on_node(self.current_selection)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                node = self.nodes[self.current_selection]
                if node['status'] != 'locked': return node['id']
        return None

    def draw(self, screen):
        max_scroll = self.map_width - SCREEN_WIDTH
        if max_scroll < 0: max_scroll = 0
        self.target_scroll_x = max(0, min(self.target_scroll_x, max_scroll))
        self.scroll_x += (self.target_scroll_x - self.scroll_x) * 0.1
        
        screen.blit(self.image, (-self.scroll_x, 0))
        
        if len(self.nodes) > 1:
            adjusted_points = [(n['pos'][0] - self.scroll_x, n['pos'][1]) for n in self.nodes]
            pygame.draw.lines(screen, (60, 40, 20), False, adjusted_points, 8)

        for i, node in enumerate(self.nodes):
            screen_x = node['pos'][0] - self.scroll_x
            screen_y = node['pos'][1]
            if -50 < screen_x < SCREEN_WIDTH + 50:
                color = MAP_COLOR_LOCKED
                if node['status'] == 'unlocked': color = MAP_COLOR_UNLOCKED
                elif node['status'] == 'completed': color = MAP_COLOR_COMPLETED
                
                scale = 1.0
                mouse_pos = pygame.mouse.get_pos()
                dist = math.sqrt((mouse_pos[0] - screen_x)**2 + (mouse_pos[1] - screen_y)**2)
                if i == self.current_selection or dist < 40:
                    scale = 1.3
                    pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), (MAP_NODE_SIZE//2 * scale) + 4, 3)

                pygame.draw.circle(screen, color, (screen_x, screen_y), int(MAP_NODE_SIZE//2 * scale))
                text = self.font.render(str(node['id']), True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_x, screen_y))
                screen.blit(text, text_rect)
                
                if node['status'] == 'completed':
                    offset = 10 * scale
                    pygame.draw.line(screen, (200, 0, 0), (screen_x - offset, screen_y - offset), (screen_x + offset, screen_y + offset), 4)
                    pygame.draw.line(screen, (200, 0, 0), (screen_x + offset, screen_y - offset), (screen_x - offset, screen_y + offset), 4)

                if i == self.current_selection or dist < 40:
                    info_text = f"BOLUM {node['id']}: {node['info']}"
                    if node['reward']: info_text += f" ({node['reward']})"
                    info_surf = self.info_font.render(info_text, True, (255, 255, 255))
                    bg_rect = info_surf.get_rect(midbottom=(screen_x, screen_y - 40))
                    bg_rect.inflate_ip(20, 10)
                    s = pygame.Surface((bg_rect.width, bg_rect.height))
                    s.set_alpha(200)
                    s.fill((0,0,0))
                    screen.blit(s, bg_rect.topleft)
                    screen.blit(info_surf, (bg_rect.x + 10, bg_rect.y + 5))