# UI/Host_Screen.py
import pygame
import socket
import sys
import time
from Game.Network import NetworkServer


class HostScreen:  # ✅ Correction 1
    def __init__(self, screen):
        # Faire un truc pour héberger une partie
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Polices
        self.font_title = pygame.font.Font(None, 56)
        self.font_text = pygame.font.Font(None, 36)

        # Réseau
        self.port = 5555
        self.local_ip = self.get_local_ip()  # ✅ Correction 2
        self.server = NetworkServer(self.port)
        self.client_connected = False

        # Couleurs
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (100, 200, 255)
        self.COLOR_INFO = (0, 255, 100)
        self.COLOR_TEXT = (255, 255, 255)

    def get_local_ip(self):
        # Récupérer l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Se connecter à une adresse IP publique pour obtenir l'IP locale
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            # Si erreur, retourner localhost
            return "127.0.0.1"

    def handle_events(self):
        for event in pygame.event.get():
            # Détecter Quit
            if event.type == pygame.QUIT:
                return "QUIT"
            # Détecter ESC
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "CANCEL"  # ✅ Correction 5
        return None

    def draw(self):
        # Afficher l'écran d'hébergement
        # Fond
        self.screen.fill(self.COLOR_BG)

        # Titre
        title = self.font_title.render("HÉBERGER UNE PARTIE", True, self.COLOR_TITLE)
        title_rect = title.get_rect(center=(512, 100))
        self.screen.blit(title, title_rect)  # ✅ Correction 3

        # Ligne de séparation
        pygame.draw.line(self.screen, self.COLOR_INFO, (300, 150), (724, 150), 2)

        # IP
        ip_label = self.font_text.render("Votre IP locale :", True, self.COLOR_TEXT)  # ✅ Correction 4
        ip_label_rect = ip_label.get_rect(center=(512, 220))
        self.screen.blit(ip_label, ip_label_rect)

        ip_value = self.font_text.render(self.local_ip, True, self.COLOR_INFO)
        ip_value_rect = ip_value.get_rect(center=(512, 270))
        self.screen.blit(ip_value, ip_value_rect)

        # Port
        port_label = self.font_text.render("Port :", True, self.COLOR_TEXT)
        port_label_rect = port_label.get_rect(center=(512, 330))
        self.screen.blit(port_label, port_label_rect)

        port_value = self.font_text.render(str(self.port), True, self.COLOR_INFO)
        port_value_rect = port_value.get_rect(center=(512, 380))
        self.screen.blit(port_value, port_value_rect)

        # Instructions
        instr1 = self.font_text.render("Communiquez cette adresse au joueur 2", True, self.COLOR_TEXT)
        instr1_rect = instr1.get_rect(center=(512, 480))
        self.screen.blit(instr1, instr1_rect)

        # Attente
        waiting = self.font_text.render("En attente de connexion...", True, (150, 150, 150))
        waiting_rect = waiting.get_rect(center=(512, 560))
        self.screen.blit(waiting, waiting_rect)

        # ESC
        esc = self.font_text.render("ESC pour annuler", True, (100, 100, 100))
        esc_rect = esc.get_rect(center=(512, 700))
        self.screen.blit(esc, esc_rect)

        # Rafraîchir
        pygame.display.flip()

    def run(self):  # ✅ Correction 6 : Même niveau d'indentation que draw()
        """Boucle principale"""
        # Démarrer le serveur
        if not self.server.start():
            print("Erreur: Impossible de démarrer le serveur")
            return "CANCEL"

        running = True
        wait_time = 0
        max_wait = 60 * 5  # 5 secondes (60 FPS)

        while running:
            self.clock.tick(60)  # 60 FPS
            wait_time += 1

            # Événements
            action = self.handle_events()

            if action == "QUIT":
                self.server.stop()
                pygame.quit()
                sys.exit()
            elif action == "CANCEL":
                self.server.stop()
                return "CANCEL"  # Retour au menu multi

            # Vérifier si un client s'est connecté
            if self.server.client_socket is not None and not self.client_connected:
                self.client_connected = True
                print("✅ Client connecté! Lancement du jeu...")
                time.sleep(1)  # Petit délai
                return ("START_GAME", self.server)

            # Timeout après 30 secondes
            if wait_time > max_wait * 6:
                self.server.stop()
                return "TIMEOUT"

            # Affichage
            self.draw()