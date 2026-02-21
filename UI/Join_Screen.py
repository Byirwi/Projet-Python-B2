# UI/Join_Screen.py
import pygame


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

        # Curseur clignotant
        self.cursor_visible = True
        self.cursor_timer = 0

        # Zones interactives (mises à jour dans draw)
        self.ip_rect = pygame.Rect(150, 250, 500, 50)
        self.port_rect = pygame.Rect(150, 380, 200, 50)
        self.connect_rect = pygame.Rect(200, 500, 400, 60)

    def _build_connect_payload(self):
        ip = self.ip_input.strip() or "127.0.0.1"
        port = self.port_input.strip() or "5555"
        return ("CONNECT", ip, port)

    def handle_events(self):
        """Gestion des événements clavier"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.ip_rect.collidepoint(event.pos):
                    self.selected_field = 0
                elif self.port_rect.collidepoint(event.pos):
                    self.selected_field = 1
                elif self.connect_rect.collidepoint(event.pos):
                    self.selected_field = 2
                    return self._build_connect_payload()

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
                    return self._build_connect_payload()

                # Saisie de texte
                # Saisie champ IP
                elif self.selected_field == 0:
                    if event.key == pygame.K_BACKSPACE:
                        self.ip_input = self.ip_input[:-1]
                    elif len(self.ip_input) < 15 and event.unicode.isprintable() and event.unicode:
                        self.ip_input += event.unicode

                # Saisie champ Port
                elif self.selected_field == 1:
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
        self.screen.blit(title, title.get_rect(center=(512, 80)))
        pygame.draw.line(self.screen, self.COLOR_INFO, (200, 140), (824, 140), 2)

        # Curseur clignotant (toggle toutes les 30 frames)
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        # Champ IP
        ip_label = self.font_text.render("Adresse IP :", True, self.COLOR_TEXT)
        self.screen.blit(ip_label, ip_label.get_rect(topleft=(150, 200)))

        self.ip_rect = pygame.Rect(150, 250, 500, 50)
        border = self.COLOR_INPUT_BORDER if self.selected_field == 0 else (100, 100, 100)
        pygame.draw.rect(self.screen, self.COLOR_INPUT_BG, self.ip_rect)
        pygame.draw.rect(self.screen, border, self.ip_rect, 3)

        if self.ip_input:
            ip_display = self.ip_input
        else:
            ip_display = "127.0.0.1"
        # Ajouter le curseur si ce champ est sélectionné
        if self.selected_field == 0 and self.cursor_visible:
            if self.ip_input:
                ip_display = self.ip_input + "|"
            else:
                ip_display = "|"
        ip_color = self.COLOR_INFO if self.ip_input else (100, 150, 100)
        ip_text = self.font_text.render(ip_display, True, ip_color)
        self.screen.blit(ip_text, ip_text.get_rect(midleft=(160, self.ip_rect.centery)))
        # Placeholder grisé quand le champ est vide et pas focus
        if not self.ip_input and self.selected_field != 0:
            ph = self.font_text.render("127.0.0.1", True, (80, 80, 80))
            self.screen.blit(ph, ph.get_rect(midleft=(160, self.ip_rect.centery)))

        # Champ Port
        port_label = self.font_text.render("Port :", True, self.COLOR_TEXT)
        self.screen.blit(port_label, port_label.get_rect(topleft=(150, 330)))

        self.port_rect = pygame.Rect(150, 380, 200, 50)
        border = self.COLOR_INPUT_BORDER if self.selected_field == 1 else (100, 100, 100)
        pygame.draw.rect(self.screen, self.COLOR_INPUT_BG, self.port_rect)
        pygame.draw.rect(self.screen, border, self.port_rect, 3)

        port_display = self.port_input
        if self.selected_field == 1 and self.cursor_visible:
            port_display += "|"
        port_text = self.font_text.render(port_display, True, self.COLOR_INFO)
        self.screen.blit(port_text, port_text.get_rect(midleft=(160, self.port_rect.centery)))

        # Bouton Connecter
        self.connect_rect = pygame.Rect(200, 500, 400, 60)
        btn_color = self.COLOR_INPUT_BORDER if self.selected_field == 2 else (60, 60, 80)
        pygame.draw.rect(self.screen, btn_color, self.connect_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 200, 200), self.connect_rect, 2, border_radius=6)
        connect_text = self.font_text.render("CONNECTER", True, self.COLOR_TEXT)
        self.screen.blit(connect_text, connect_text.get_rect(center=self.connect_rect.center))

        # Message
        if self.message:
            color = self.COLOR_ERROR if "Erreur" in self.message else self.COLOR_INFO
            msg = self.font_small.render(self.message, True, color)
            self.screen.blit(msg, msg.get_rect(center=(512, 600)))

        instr = self.font_small.render("TAB ou ↑↓ pour naviguer | ENTER: valider | ESC: annuler", True, (150, 150, 150))
        self.screen.blit(instr, instr.get_rect(center=(512, 700)))

        pygame.display.flip()

    def run(self):
        """Boucle principale"""
        while True:
            result = self.handle_events()

            if result:
                return result

            self.draw()
            self.clock.tick(60)


