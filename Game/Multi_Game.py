# Game/Multi_Game.py
import pygame
import sys
import json
from Game.Assets.Map import GameMap
from Game.Assets.Tank import Tank
from Game.Assets.Camera import Camera
from Game.Movement.Player_Movement import PlayerMovement
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
        keys = pygame.key.get_pressed()

        # Mouvement du joueur avec collisions
        solid_obstacles = self.game_map.get_solid_obstacles()
        PlayerMovement.handle_input(self.player, keys, solid_obstacles)

        # Mettre à jour le tank (cooldown, etc.)
        self.player.update()

        # Viser vers la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.player.aim_at_mouse(mouse_x, mouse_y, self.camera.x, self.camera.y)

        # Mise à jour des projectiles du joueur
        for shell in self.shells[:]:
            shell.update()

        # Collisions pour les projectiles du joueur
        bouncing_obstacles = self.game_map.get_bouncing_obstacles()
        destroying_obstacles = self.game_map.get_destroying_obstacles()
        player_collision_result = ShellCollisions.check_all_collisions(
            self.shells,
            bouncing_obstacles,
            destroying_obstacles,
            [self.player, self.opponent]
        )
        for tank, _shell in player_collision_result['tanks_hit']:
            tank.take_damage(25)
        if player_collision_result['shells_to_remove']:
            self.shells = [shell for shell in self.shells if shell.active]

        # Mise à jour des projectiles de l'adversaire
        for shell in self.opponent_shells[:]:
            shell.update()

        # Collisions pour les projectiles de l'adversaire
        opponent_collision_result = ShellCollisions.check_all_collisions(
            self.opponent_shells,
            bouncing_obstacles,
            destroying_obstacles,
            [self.player, self.opponent]
        )
        for tank, _shell in opponent_collision_result['tanks_hit']:
            tank.take_damage(25)
        if opponent_collision_result['shells_to_remove']:
            self.opponent_shells = [shell for shell in self.opponent_shells if shell.active]

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
        self.camera.follow(self.player)

        # Afficher la carte
        self.game_map.draw(self.screen, self.camera.x, self.camera.y)

        # Afficher les projectiles
        for shell in self.shells:
            shell.draw(self.screen, self.camera.x, self.camera.y)
        for shell in self.opponent_shells:
            shell.draw(self.screen, self.camera.x, self.camera.y)

        # Afficher les tanks
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        self.opponent.draw(self.screen, self.camera.x, self.camera.y)

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

