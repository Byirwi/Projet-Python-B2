# UI/Join_Screen.py
import pygame
import sys


class JoinScreen:
    """Écran pour rejoindre une partie multijoueur"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Polices
        self.font_title = pygame.font.Font(None, 56)
        self.font_text = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # Couleurs
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (100, 200, 255)
        self.COLOR_INFO = (0, 255, 100)
        self.COLOR_ERROR = (255, 100, 100)
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_INPUT_BG = (40, 40, 50)
        self.COLOR_INPUT_BORDER = (100, 200, 255)

        # Champs de saisie
        self.ip_input = ""
        self.port_input = "5555"
        self.selected_field = 0  # 0 = IP, 1 = Port, 2 = Connecter

        # États
        self.message = ""
        self.message_time = 0
        self.is_connecting = False

    def handle_events(self):
        """Gestion des événements clavier"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                # ESC pour revenir
                if event.key == pygame.K_ESCAPE:
                    return "CANCEL"

                # TAB pour changer de champ
                elif event.key == pygame.K_TAB:
                    self.selected_field = (self.selected_field + 1) % 3

                # Flèches haut/bas pour naviguer
                elif event.key == pygame.K_UP:
                    self.selected_field = (self.selected_field - 1) % 3

                elif event.key == pygame.K_DOWN:
                    self.selected_field = (self.selected_field + 1) % 3

                # Entrée pour valider
                elif event.key == pygame.K_RETURN:
                    if self.selected_field == 2:  # Bouton Connecter
                        return ("CONNECT", self.ip_input, self.port_input)

                # Saisie de texte
                elif self.selected_field == 0:  # Champ IP
                    if event.key == pygame.K_BACKSPACE:
                        self.ip_input = self.ip_input[:-1]
                    elif len(self.ip_input) < 15:
                        self.ip_input += event.unicode

                elif self.selected_field == 1:  # Champ Port
                    if event.key == pygame.K_BACKSPACE:
                        self.port_input = self.port_input[:-1]
                    elif event.unicode.isdigit() and len(self.port_input) < 5:
                        self.port_input += event.unicode

        return None

    def draw(self):
        """Afficher l'écran de connexion"""
        self.screen.fill(self.COLOR_BG)

        # Titre
        title = self.font_title.render("REJOINDRE UNE PARTIE", True, self.COLOR_TITLE)
        title_rect = title.get_rect(center=(512, 80))
        self.screen.blit(title, title_rect)

        # Ligne de séparation
        pygame.draw.line(self.screen, self.COLOR_INFO, (200, 140), (824, 140), 2)

        # Champ IP
        ip_label = self.font_text.render("Adresse IP :", True, self.COLOR_TEXT)
        ip_label_rect = ip_label.get_rect(topleft=(150, 200))
        self.screen.blit(ip_label, ip_label_rect)

        ip_input_rect = pygame.Rect(150, 250, 500, 50)
        border_color = self.COLOR_INPUT_BORDER if self.selected_field == 0 else (100, 100, 100)
        pygame.draw.rect(self.screen, self.COLOR_INPUT_BG, ip_input_rect)
        pygame.draw.rect(self.screen, border_color, ip_input_rect, 3)

        ip_text = self.font_text.render(self.ip_input or "127.0.0.1", True, self.COLOR_INFO)
        ip_text_rect = ip_text.get_rect(midleft=(160, ip_input_rect.centery))
        self.screen.blit(ip_text, ip_text_rect)

        # Champ Port
        port_label = self.font_text.render("Port :", True, self.COLOR_TEXT)
        port_label_rect = port_label.get_rect(topleft=(150, 330))
        self.screen.blit(port_label, port_label_rect)

        port_input_rect = pygame.Rect(150, 380, 200, 50)
        border_color = self.COLOR_INPUT_BORDER if self.selected_field == 1 else (100, 100, 100)
        pygame.draw.rect(self.screen, self.COLOR_INPUT_BG, port_input_rect)
        pygame.draw.rect(self.screen, border_color, port_input_rect, 3)

        port_text = self.font_text.render(self.port_input, True, self.COLOR_INFO)
        port_text_rect = port_text.get_rect(midleft=(160, port_input_rect.centery))
        self.screen.blit(port_text, port_text_rect)

        # Bouton Connecter
        connect_rect = pygame.Rect(200, 500, 400, 60)
        button_color = self.COLOR_INPUT_BORDER if self.selected_field == 2 else (100, 100, 100)
        pygame.draw.rect(self.screen, button_color, connect_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), connect_rect, 2)

        connect_text = self.font_text.render("CONNECTER", True, self.COLOR_TEXT)
        connect_text_rect = connect_text.get_rect(center=connect_rect.center)
        self.screen.blit(connect_text, connect_text_rect)

        # Message
        if self.message:
            msg_color = self.COLOR_ERROR if "Erreur" in self.message else self.COLOR_INFO
            msg = self.font_small.render(self.message, True, msg_color)
            msg_rect = msg.get_rect(center=(512, 600))
            self.screen.blit(msg, msg_rect)

        # Instructions
        instr = self.font_small.render("TAB ou ↑↓ pour naviguer | ESC pour annuler", True, (150, 150, 150))
        instr_rect = instr.get_rect(center=(512, 700))
        self.screen.blit(instr, instr_rect)

        pygame.display.flip()

    def run(self):
        """Boucle principale"""
        while True:
            result = self.handle_events()

            if result:
                return result

            self.draw()
            self.clock.tick(60)








