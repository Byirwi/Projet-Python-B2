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

        # Couleurs
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (255, 200, 0)
        self.COLOR_SELECTED = (255, 255, 255)
        self.COLOR_NORMAL = (100, 100, 100)
        self.COLOR_ACCENT = (255, 200, 0)

    def handle_events(self):
        """Gestion des événements clavier"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                # Flèche haut
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)

                # Flèche bas
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)

                # Entrée : valider la sélection
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected]

                # ← AJOUTE CETTE PARTIE (NOUVEAU !) ←
                # ESC : quitter directement
                elif event.key == pygame.K_ESCAPE:
                    return "QUITTER"

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
        for i, option in enumerate(self.options):
            # Couleur selon si sélectionné
            color = self.COLOR_SELECTED if i == self.selected else self.COLOR_NORMAL

            # Rendu du texte
            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(512, 300 + i * 80))
            self.screen.blit(text, text_rect)

            # Indicateur de sélection (triangle)
            if i == self.selected:
                # Triangle pointant vers la droite (à droite du texte)
                pygame.draw.polygon(self.screen, self.COLOR_ACCENT, [
                    (text_rect.right + 40, text_rect.centery),
                    (text_rect.right + 20, text_rect.centery - 15),
                    (text_rect.right + 20, text_rect.centery + 15)
                ])

        # ← AJOUTE CES LIGNES ICI (NOUVEAU !) ←
        # Instructions en bas
        instructions = "↑↓ Naviguer  |  ENTER Valider  |  ESC Quitter"
        instr_font = pygame.font.Font(None, 28)  # Police plus petite
        instr_text = instr_font.render(instructions, True, (80, 80, 80))
        instr_rect = instr_text.get_rect(center=(512, 730))
        self.screen.blit(instr_text, instr_rect)

        pygame.display.flip()

    def run(self):
        """Boucle principale du menu"""
        running = True
        while running:
            self.clock.tick(60)  # 60 FPS

            # Gestion des événements
            choice = self.handle_events()

            if choice == "QUIT":
                pygame.quit()
                sys.exit()
            elif choice:
                return choice  # Retourne le choix de l'utilisateur

            # Affichage
            self.draw()