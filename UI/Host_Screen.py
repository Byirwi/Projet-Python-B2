# UI/Host_Screen.py
import pygame
import socket
import sys
import time
from Game.Network import NetworkServer


class HostScreen:

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 56)
        self.font_text = pygame.font.Font(None, 36)

        self.port = 5555
        self.local_ip = self._get_local_ip()
        self.server = NetworkServer(self.port)
        self.client_connected = False

        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (100, 200, 255)
        self.COLOR_INFO = (0, 255, 100)
        self.COLOR_TEXT = (255, 255, 255)

    @staticmethod
    def _get_local_ip():
        """Récupère l'IP LAN via un socket UDP éphémère."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "CANCEL"
        return None

    def draw(self):
        self.screen.fill(self.COLOR_BG)

        title = self.font_title.render("HÉBERGER UNE PARTIE", True, self.COLOR_TITLE)
        self.screen.blit(title, title.get_rect(center=(512, 100)))
        pygame.draw.line(self.screen, self.COLOR_INFO, (300, 150), (724, 150), 2)

        for label, value, y in [
            ("Votre IP locale :", self.local_ip, 220),
            ("Port :", str(self.port), 330),
        ]:
            lbl = self.font_text.render(label, True, self.COLOR_TEXT)
            self.screen.blit(lbl, lbl.get_rect(center=(512, y)))
            val = self.font_text.render(value, True, self.COLOR_INFO)
            self.screen.blit(val, val.get_rect(center=(512, y + 50)))

        instr = self.font_text.render("Communiquez cette adresse au joueur 2", True, self.COLOR_TEXT)
        self.screen.blit(instr, instr.get_rect(center=(512, 480)))

        wait = self.font_text.render("En attente de connexion...", True, (150, 150, 150))
        self.screen.blit(wait, wait.get_rect(center=(512, 560)))

        esc = self.font_text.render("ESC pour annuler", True, (100, 100, 100))
        self.screen.blit(esc, esc.get_rect(center=(512, 700)))

        pygame.display.flip()

    def run(self):
        if not self.server.start():
            return "CANCEL"

        wait_time = 0
        max_wait = 60 * 30  # 30 secondes

        while True:
            self.clock.tick(60)
            wait_time += 1

            action = self.handle_events()
            if action == "QUIT":
                self.server.stop(); pygame.quit(); sys.exit()
            elif action == "CANCEL":
                self.server.stop(); return "CANCEL"

            # Un client vient de se connecter
            if self.server.client_socket is not None and not self.client_connected:
                self.client_connected = True
                time.sleep(1)
                return ("START_GAME", self.server)

            if wait_time > max_wait:
                self.server.stop(); return "TIMEOUT"

            self.draw()