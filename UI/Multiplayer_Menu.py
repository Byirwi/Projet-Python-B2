# UI/Multiplayer_Menu.py
import pygame
import sys


class MultiplayerMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Polices
        self.font_title = pygame.font.Font(None, 64)
        self.font_menu = pygame.font.Font(None, 48)
        self.font_subtitle = pygame.font.Font(None, 32)

        # Options du menu
        self.options = ["HÉBERGER", "REJOINDRE", "RETOUR"]
        self.selected = 0

        # Rectangles cliquables (calculés dans draw)
        self.option_rects = []

        # Couleurs
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (100, 200, 255)
        self.COLOR_SELECTED = (255, 255, 255)
        self.COLOR_NORMAL = (100, 100, 100)
        self.COLOR_ACCENT = (100, 200, 255)
        self.COLOR_INFO = (150, 150, 150)

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
                    return "RETOUR"

            # Souris : survol
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected = i

            # Souris : clic
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        return self.options[i]

        return None

    def draw(self):
        """Affichage du menu"""
        self.screen.fill(self.COLOR_BG)

        # Titre
        title = self.font_title.render("MULTIJOUEUR", True, self.COLOR_TITLE)
        title_rect = title.get_rect(center=(512, 120))
        self.screen.blit(title, title_rect)

        # Sous-titre
        subtitle = self.font_subtitle.render("Mode Réseau Local", True, self.COLOR_INFO)
        subtitle_rect = subtitle.get_rect(center=(512, 180))
        self.screen.blit(subtitle, subtitle_rect)

        # Options du menu
        start_y = 300
        self.option_rects = []
        for i, option in enumerate(self.options):
            color = self.COLOR_SELECTED if i == self.selected else self.COLOR_NORMAL

            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(512, start_y + i * 90))
            click_rect = text_rect.inflate(80, 20)
            self.option_rects.append(click_rect)
            self.screen.blit(text, text_rect)

            # Description
            if i == 0:
                desc = "Créer une partie et attendre un joueur"
            elif i == 1:
                desc = "Se connecter à une partie existante"
            else:
                desc = "Revenir au menu principal"

            if i == self.selected:
                desc_text = self.font_subtitle.render(desc, True, self.COLOR_INFO)
                desc_rect = desc_text.get_rect(center=(512, start_y + i * 90 + 40))
                self.screen.blit(desc_text, desc_rect)

            # Triangle
            if i == self.selected:
                pygame.draw.polygon(self.screen, self.COLOR_ACCENT, [
                    (text_rect.right + 40, text_rect.centery),
                    (text_rect.right + 20, text_rect.centery - 15),
                    (text_rect.right + 20, text_rect.centery + 15)
                ])

        # Instructions en bas
        instructions = "↑↓ / Souris: Naviguer  |  ENTER / Clic: Valider  |  ESC: Retour"
        instr_text = self.font_subtitle.render(instructions, True, (80, 80, 80))
        instr_rect = instr_text.get_rect(center=(512, 700))
        self.screen.blit(instr_text, instr_rect)

        pygame.display.flip()

    def run(self):
        """Boucle principale du menu multijoueur"""
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