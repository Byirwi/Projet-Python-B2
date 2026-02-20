# UI/Name_Input.py
"""Écran de saisie du nom du joueur après une partie"""

import pygame
import sys
from Config import MENU_WIDTH


class NameInput:
    """Saisie du pseudo après une partie. Retourne le nom ou None (skip)."""

    def __init__(self, screen, won, mode="solo"):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.won = won
        self.mode = mode

        self.font_title = pygame.font.Font(None, 64)
        self.font_text = pygame.font.Font(None, 36)
        self.font_input = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)

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
                if event.key == pygame.K_RETURN and self.name.strip():
                    return self.name.strip()
                if event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif len(self.name) < self.max_length and event.unicode.isprintable() and event.unicode != '':
                    self.name += event.unicode
        return None

    def draw(self):
        """Affichage de l'écran"""
        self.screen.fill((20, 20, 30))

        title_text = "VICTOIRE !" if self.won else "DÉFAITE..."
        title_color = (0, 255, 0) if self.won else (255, 0, 0)
        title = self.font_title.render(title_text, True, title_color)
        self.screen.blit(title, title.get_rect(center=(MENU_WIDTH // 2, 120)))

        instr = self.font_text.render("Entrez votre nom pour le leaderboard :", True, (255, 255, 255))
        self.screen.blit(instr, instr.get_rect(center=(MENU_WIDTH // 2, 250)))

        # Champ de saisie
        input_rect = pygame.Rect(MENU_WIDTH // 2 - 200, 300, 400, 60)
        pygame.draw.rect(self.screen, (40, 40, 50), input_rect)
        pygame.draw.rect(self.screen, (255, 200, 0), input_rect, 3)

        # Curseur clignotant
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        display = self.name + ("|" if self.cursor_visible else "")
        txt = self.font_input.render(display, True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(midleft=(input_rect.left + 15, input_rect.centery)))

        h1 = self.font_small.render("ENTER pour valider", True, (0, 255, 100))
        self.screen.blit(h1, h1.get_rect(center=(MENU_WIDTH // 2, 400)))
        h2 = self.font_small.render("ESC pour passer", True, (100, 100, 100))
        self.screen.blit(h2, h2.get_rect(center=(MENU_WIDTH // 2, 430)))

        pygame.display.flip()

    def run(self):
        """Boucle principale — retourne le nom ou 'SKIP'"""
        while True:
            self.clock.tick(60)
            result = self.handle_events()
            if result == "QUIT":
                pygame.quit(); sys.exit()
            elif result == "SKIP":
                return None
            elif result is not None:
                return result
            self.draw()

