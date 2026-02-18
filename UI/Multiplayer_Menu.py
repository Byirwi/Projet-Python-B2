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
        self.selected = 0  # Index de l'option sélectionnée

        # Couleurs
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (100, 200, 255)  # Bleu clair pour différencier
        self.COLOR_SELECTED = (255, 255, 255)
        self.COLOR_NORMAL = (100, 100, 100)
        self.COLOR_ACCENT = (100, 200, 255)
        self.COLOR_INFO = (150, 150, 150)

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

                # Échap : retour
                elif event.key == pygame.K_ESCAPE:
                    return "RETOUR"

        return None

    def draw(self):
        """Affichage du menu"""
        # Fond
        self.screen.fill(self.COLOR_BG)

        # Titre
        title = self.font_title.render("MULTIJOUEUR", True, self.COLOR_TITLE)
        title_rect = title.get_rect(center=(512, 120))
        self.screen.blit(title, title_rect)

        # Sous-titre informatif
        subtitle = self.font_subtitle.render("Mode Réseau Local", True, self.COLOR_INFO)
        subtitle_rect = subtitle.get_rect(center=(512, 180))
        self.screen.blit(subtitle, subtitle_rect)

        # Options du menu
        start_y = 300
        for i, option in enumerate(self.options):
            # Couleur selon si sélectionné
            color = self.COLOR_SELECTED if i == self.selected else self.COLOR_NORMAL

            # Rendu du texte
            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(512, start_y + i * 90))
            self.screen.blit(text, text_rect)

            # Description de chaque option
            if i == 0:  # HÉBERGER
                desc = "Créer une partie et attendre un joueur"
            elif i == 1:  # REJOINDRE
                desc = "Se connecter à une partie existante"
            else:  # RETOUR
                desc = "Revenir au menu principal"

            # Afficher description si sélectionné
            if i == self.selected:
                desc_text = self.font_subtitle.render(desc, True, self.COLOR_INFO)
                desc_rect = desc_text.get_rect(center=(512, start_y + i * 90 + 40))
                self.screen.blit(desc_text, desc_rect)

            # Indicateur de sélection (triangle)
            if i == self.selected:
                # Triangle pointant vers la gauche (à droite du texte)
                pygame.draw.polygon(self.screen, self.COLOR_ACCENT, [
                    (text_rect.right + 40, text_rect.centery),  # Pointe droite
                    (text_rect.right + 20, text_rect.centery - 15),  # Coin haut
                    (text_rect.right + 20, text_rect.centery + 15)  # Coin bas
                ])

        # Instructions en bas
        instructions = "↑↓ Naviguer  |  ENTER Valider  |  ESC Retour"
        instr_text = self.font_subtitle.render(instructions, True, (80, 80, 80))
        instr_rect = instr_text.get_rect(center=(512, 700))
        self.screen.blit(instr_text, instr_rect)

        pygame.display.flip()

    def run(self):
        """Boucle principale du menu multijoueur"""
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