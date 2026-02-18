# Game/Multi_Game.py
import pygame
import sys
import json
from Game.Assets.Map import GameMap
from Game.Assets.Tank import Tank
from Game.Assets.Camera import Camera
from Game.Movement.Player_Movement import PlayerMovement
from Game.Movement.Shell_Movement import ShellMovement
from Game.Collisions.Shell_Collisions import ShellCollisions
from Game.Network import NetworkServer, NetworkClient
from Config import MENU_WIDTH, MENU_HEIGHT, FPS, MAP_WIDTH, MAP_HEIGHT


class MultiGame:
    """Gestionnaire du mode multijoueur"""

    def __init__(self, screen, network_obj, is_host=True):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.is_host = is_host
        self.network = network_obj

        # Map
        self.game_map = GameMap()

        # Joueur local (Bleu si host, Rouge si client)
        if is_host:
            self.player = Tank(MAP_WIDTH // 4, MAP_HEIGHT // 2, (0, 100, 255))  # Bleu
            self.opponent_color = (255, 50, 50)  # Rouge pour l'adversaire
        else:
            self.player = Tank(3 * MAP_WIDTH // 4, MAP_HEIGHT // 2, (255, 50, 50))  # Rouge
            self.opponent_color = (0, 100, 255)  # Bleu pour l'adversaire

        # Adversaire (Tank distant)
        self.opponent = Tank(3 * MAP_WIDTH // 4 if is_host else MAP_WIDTH // 4, MAP_HEIGHT // 2, self.opponent_color)

        # Caméra
        self.camera = Camera(MENU_WIDTH, MENU_HEIGHT)

        # Projectiles
        self.shells = []
        self.opponent_shells = []

        # Police pour les infos
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # État
        self.running = True
        self.connection_lost = False

    def handle_events(self):
        """Gestion des événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                # ESC pour retourner au menu
                if event.key == pygame.K_ESCAPE:
                    return "MENU"

            # Tir avec clic gauche
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    shell = self.player.fire()
                    if shell:
                        self.shells.append(shell)

        return None

    def update(self):
        """Mise à jour du jeu"""
        # Mouvement du joueur
        PlayerMovement.update(self.player)

        # Mise à jour des projectiles du joueur
        for shell in self.shells[:]:
            ShellMovement.update(shell)

            # Collision avec la carte
            if ShellCollisions.check_map_collision(shell, self.game_map):
                self.shells.remove(shell)
                continue

            # Collision avec l'adversaire
            if ShellCollisions.check_tank_collision(shell, self.opponent):
                self.opponent.take_damage(25)
                self.shells.remove(shell)

        # Mise à jour des projectiles de l'adversaire
        for shell in self.opponent_shells[:]:
            ShellMovement.update(shell)

            # Collision avec la carte
            if ShellCollisions.check_map_collision(shell, self.game_map):
                self.opponent_shells.remove(shell)
                continue

            # Collision avec le joueur
            if ShellCollisions.check_tank_collision(shell, self.player):
                self.player.take_damage(25)
                self.opponent_shells.remove(shell)

        # Recevoir les données du réseau
        if not self.receive_opponent_data():
            self.connection_lost = True

        # Envoyer les données du joueur
        self.send_player_data()

    def send_player_data(self):
        """Envoyer l'état du joueur au réseau"""
        data = {
            "x": self.player.x,
            "y": self.player.y,
            "angle": self.player.angle,
            "health": self.player.health,
            "shells": len(self.shells)
        }
        self.network.send(data)

    def receive_opponent_data(self):
        """Recevoir l'état de l'adversaire du réseau"""
        data = self.network.receive()
        if data:
            try:
                self.opponent.x = data.get("x", self.opponent.x)
                self.opponent.y = data.get("y", self.opponent.y)
                self.opponent.angle = data.get("angle", self.opponent.angle)
                self.opponent.health = data.get("health", self.opponent.health)

                # Gérer les projectiles de l'adversaire
                num_shells = data.get("shells", 0)
                # Note: On pourrait implémenter une synchronisation des projectiles ici
                return True
            except Exception as e:
                print(f"Erreur réception données: {e}")
                return False
        return True

    def draw(self):
        """Affichage du jeu"""
        self.screen.fill((20, 20, 30))

        # Mettre à jour la caméra sur le joueur
        self.camera.update(self.player)

        # Afficher la carte
        for tile in self.game_map.tiles:
            screen_x = tile.x - self.camera.x
            screen_y = tile.y - self.camera.y
            if -50 < screen_x < MENU_WIDTH + 50 and -50 < screen_y < MENU_HEIGHT + 50:
                pygame.draw.rect(self.screen, (50, 50, 50), (screen_x, screen_y, 20, 20))
                pygame.draw.rect(self.screen, (100, 100, 100), (screen_x, screen_y, 20, 20), 1)

        # Afficher le joueur
        player_screen_x = self.player.x - self.camera.x
        player_screen_y = self.player.y - self.camera.y
        pygame.draw.rect(self.screen, self.player.color, (player_screen_x, player_screen_y, 50, 50))

        # Afficher l'adversaire
        opponent_screen_x = self.opponent.x - self.camera.x
        opponent_screen_y = self.opponent.y - self.camera.y
        pygame.draw.rect(self.screen, self.opponent.color, (opponent_screen_x, opponent_screen_y, 50, 50))

        # Afficher les projectiles du joueur
        for shell in self.shells:
            shell_screen_x = shell.x - self.camera.x
            shell_screen_y = shell.y - self.camera.y
            if -10 < shell_screen_x < MENU_WIDTH + 10 and -10 < shell_screen_y < MENU_HEIGHT + 10:
                pygame.draw.rect(self.screen, (255, 255, 0), (shell_screen_x, shell_screen_y, 3, 7))

        # Afficher les projectiles de l'adversaire
        for shell in self.opponent_shells:
            shell_screen_x = shell.x - self.camera.x
            shell_screen_y = shell.y - self.camera.y
            if -10 < shell_screen_x < MENU_WIDTH + 10 and -10 < shell_screen_y < MENU_HEIGHT + 10:
                pygame.draw.rect(self.screen, (255, 200, 0), (shell_screen_x, shell_screen_y, 3, 7))

        # Afficher les infos
        player_info = self.font.render(f"Vous: {self.player.health} HP", True, (0, 255, 0))
        opponent_info = self.font.render(f"Adversaire: {self.opponent.health} HP", True, (255, 0, 0))

        self.screen.blit(player_info, (10, 10))
        self.screen.blit(opponent_info, (10, 50))

        # Afficher message d'erreur connexion
        if self.connection_lost:
            error_msg = self.font.render("CONNEXION PERDUE!", True, (255, 0, 0))
            error_rect = error_msg.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2))
            self.screen.blit(error_msg, error_rect)

        # ESC pour quitter
        esc_info = self.font_small.render("ESC pour quitter", True, (150, 150, 150))
        self.screen.blit(esc_info, (10, MENU_HEIGHT - 40))

        pygame.display.flip()

    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            result = self.handle_events()

            if result:
                self.network.stop() if self.is_host else self.network.disconnect()
                return result

            self.update()
            self.draw()

            self.clock.tick(FPS)

            # Vérifier si quelqu'un est mort
            if self.player.health <= 0 or self.opponent.health <= 0:
                self.running = False
                self.network.stop() if self.is_host else self.network.disconnect()

                if self.player.health > 0:
                    return "WIN"
                else:
                    return "LOSE"

        return "MENU"

