# UI/Host_Screen.py
import pygame
import socket
import sys

class Host_Screen:
    def __init__(self, screen):
        #faire un truc pour héberger une partie
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Polices
        self.font_title = pygame.font.Font(None, 56)
        self.font_text = pygame.font.Font(None, 36)

        #réseau
        self.port = 5555
        self.local.ip = self.get_local_ip()

        #couleurs
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (100, 200, 255)
        self.COLOR_INFO = (0, 255, 100)
        self.COLOR_TEXT = (255, 255, 255)
        pass

    def get_local_ip(self):
        #recuperer l'IP locale
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
        pass

    def handle_events(self):
        for event in pygame.event.get():
            # Detecter Quit
            if event.type == pygame.QUIT:
                return "QUITTER"
            #Detecter ESC
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "Retopur"
        return None

    def draw(self):
        #Afficher l'écran d'hébergement
        # Fond
        self.screen.fill(self.COLOR_BG)

        #  Titre
        title =self.font_title.render("HÉBERGER UNE PARTIE", True, self.COLOR_TITLE)
        title_rect = title.get_rect(center=(512, 100))
        self.sreen.blit(title, title_rect)
        # Ligne de séparation
        pygame.draw.line(self.screen, self.COLOR_INFO, (300, 150), (724, 150), 2)
        #IP
        ip_label

        # Rafraîchir
        pygame.display.flip()