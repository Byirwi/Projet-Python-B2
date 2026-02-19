# UI/Name_Input.py
"""Écran de saisie du nom du joueur après une partie"""

import pygame
import sys
from Config import MENU_WIDTH


class NameInput:
    """Écran pour entrer son nom avant d'enregistrer le score"""

    def __init__(self, screen, won, mode="solo"):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.won = won
        self.mode = mode  # "solo" ou "multi"

        # Polices
        self.font_title = pygame.font.Font(None, 64)
        self.font_text = pygame.font.Font(None, 36)
        self.font_input = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)

        # Couleurs
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_WIN = (0, 255, 0)
        self.COLOR_LOSE = (255, 0, 0)
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_INPUT_BG = (40, 40, 50)
        self.COLOR_INPUT_BORDER = (255, 200, 0)

        # Saisie
        self.name = ""
        self.max_length = 15
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_events(self):
        """Gestion des événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "SKIP"  # Ne pas enregistrer le score
                if event.key == pygame.K_RETURN:
                    if self.name.strip():
                        return self.name.strip()
                    # Si vide, ne pas valider
                if event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif len(self.name) < self.max_length and event.unicode.isprintable() and event.unicode != '':
                    self.name += event.unicode
        return None

    def draw(self):
        """Affichage de l'écran"""
        self.screen.fill(self.COLOR_BG)

        # Titre selon victoire/défaite
        if self.won:
            title_text = "VICTOIRE !"
            title_color = self.COLOR_WIN
        else:
            title_text = "DÉFAITE..."
            title_color = self.COLOR_LOSE

        title = self.font_title.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(MENU_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)

        # Instruction
        instr = self.font_text.render("Entrez votre nom pour le leaderboard :", True, self.COLOR_TEXT)
        instr_rect = instr.get_rect(center=(MENU_WIDTH // 2, 250))
        self.screen.blit(instr, instr_rect)

        # Champ de saisie
        input_rect = pygame.Rect(MENU_WIDTH // 2 - 200, 300, 400, 60)
        pygame.draw.rect(self.screen, self.COLOR_INPUT_BG, input_rect)
        pygame.draw.rect(self.screen, self.COLOR_INPUT_BORDER, input_rect, 3)

        # Texte saisi + curseur clignotant
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        display_name = self.name
        if self.cursor_visible:
            display_name += "|"

        name_surface = self.font_input.render(display_name, True, self.COLOR_TEXT)
        name_rect = name_surface.get_rect(midleft=(input_rect.left + 15, input_rect.centery))
        self.screen.blit(name_surface, name_rect)

        # Aide
        help1 = self.font_small.render("ENTER pour valider", True, (0, 255, 100))
        help1_rect = help1.get_rect(center=(MENU_WIDTH // 2, 400))
        self.screen.blit(help1, help1_rect)

        help2 = self.font_small.render("ESC pour passer (ne pas enregistrer)", True, (100, 100, 100))
        help2_rect = help2.get_rect(center=(MENU_WIDTH // 2, 430))
        self.screen.blit(help2, help2_rect)

        pygame.display.flip()

    def run(self):
        """Boucle principale — retourne le nom ou 'SKIP'"""
        while True:
            self.clock.tick(60)
            result = self.handle_events()

            if result == "QUIT":
                pygame.quit()
                sys.exit()
            elif result == "SKIP":
                return None  # Pas de nom, pas d'enregistrement
            elif result is not None:
                return result  # Le nom du joueur

            self.draw()


