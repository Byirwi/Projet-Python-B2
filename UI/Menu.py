# ui/menu.py
import pygame
import sys


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Polices
        self.font_title = pygame.font.Font(None, 72)
        self.font_menu = pygame.font.Font(None, 48)

        # Options du menu
        self.options = ["SOLO", "MULTIJOUEUR", "SCORES", "QUITTER"]
        self.selected = 0  # Index de l'option sélectionnée

        # Rectangles cliquables pour chaque option (calculés dans draw)
        self.option_rects = []

        # Couleurs
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (255, 200, 0)
        self.COLOR_SELECTED = (255, 255, 255)
        self.COLOR_NORMAL = (100, 100, 100)
        self.COLOR_ACCENT = (255, 200, 0)

    def handle_events(self):
        """Gestion des événements clavier et souris"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected]
                elif event.key == pygame.K_ESCAPE:
                    return "QUITTER"

            # Souris : survol → sélection
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected = i

            # Souris : clic → valider
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        return self.options[i]

        return None

    def draw(self):
        """Affichage du menu"""
        # Fond
        self.screen.fill(self.COLOR_BG)

        # Titre
        title = self.font_title.render("TANK BATTLE", True, self.COLOR_TITLE)
        title_rect = title.get_rect(center=(512, 150))
        self.screen.blit(title, title_rect)

        # Options du menu
        self.option_rects = []
        for i, option in enumerate(self.options):
            color = self.COLOR_SELECTED if i == self.selected else self.COLOR_NORMAL

            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(512, 300 + i * 80))
            # Agrandir la zone cliquable
            click_rect = text_rect.inflate(80, 20)
            self.option_rects.append(click_rect)
            self.screen.blit(text, text_rect)

            # Indicateur de sélection (triangle)
            if i == self.selected:
                pygame.draw.polygon(self.screen, self.COLOR_ACCENT, [
                    (text_rect.right + 40, text_rect.centery),
                    (text_rect.right + 20, text_rect.centery - 15),
                    (text_rect.right + 20, text_rect.centery + 15)
                ])

        # Instructions en bas
        instructions = "↑↓ / Souris: Naviguer  |  ENTER / Clic: Valider  |  ESC: Quitter"
        instr_font = pygame.font.Font(None, 28)
        instr_text = instr_font.render(instructions, True, (80, 80, 80))
        instr_rect = instr_text.get_rect(center=(512, 730))
        self.screen.blit(instr_text, instr_rect)

        pygame.display.flip()

    def run(self):
        """Boucle principale du menu"""
        running = True
        while running:
            self.clock.tick(60)

            choice = self.handle_events()

            if choice == "QUIT":
                pygame.quit()
                sys.exit()
            elif choice:
                return choice

            self.draw()