# Game/Multi_Game.py
import pygame
import sys
import math
import time
from Game.Assets.Map import GameMap
from Game.Assets.Tank import Tank
from Game.Assets.Shell import Shell
from Game.Assets.Camera import Camera
from Game.Movement.Player_Movement import PlayerMovement
from Game.Collisions.Shell_Collisions import ShellCollisions
from Config import MENU_WIDTH, MENU_HEIGHT, FPS, MAP_WIDTH, MAP_HEIGHT
from Score_Manager import add_score, get_leaderboard, merge_scores
from UI.Name_Input import NameInput


class MultiGame:
    """Gestionnaire du mode multijoueur"""

    def __init__(self, screen, network_obj, is_host=True):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.is_host = is_host
        self.network = network_obj

        # Police pour les infos
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # Initialiser la partie
        self._init_game()

    def _init_game(self):
        """Initialise / réinitialise l'état de la partie"""
        # Map
        self.game_map = GameMap()

        # Joueur local
        if self.is_host:
            self.player = Tank(MAP_WIDTH // 4, MAP_HEIGHT // 2, (0, 100, 255))
            self.opponent_color = (255, 50, 50)
        else:
            self.player = Tank(3 * MAP_WIDTH // 4, MAP_HEIGHT // 2, (255, 50, 50))
            self.opponent_color = (0, 100, 255)

        # Adversaire
        self.opponent = Tank(
            3 * MAP_WIDTH // 4 if self.is_host else MAP_WIDTH // 4,
            MAP_HEIGHT // 2, self.opponent_color
        )

        # Caméra
        self.camera = Camera(MENU_WIDTH, MENU_HEIGHT)

        # Projectiles locaux (tirés par nous)
        self.shells = []
        # Projectiles reçus du réseau (tirés par l'adversaire) — recréés chaque frame
        self.opponent_shells = []

        # État
        self.running = True
        self.connection_lost = False

    def handle_events(self):
        """Gestion des événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if event.key == pygame.K_r:
                    self.player.reload()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    shell = self.player.fire()
                    if shell:
                        self.shells.append(shell)
        return None

    def update(self):
        """Mise à jour du jeu"""
        keys = pygame.key.get_pressed()

        # Mouvement du joueur
        solid_obstacles = self.game_map.get_solid_obstacles()
        PlayerMovement.handle_input(self.player, keys, solid_obstacles)
        self.player.update()

        # Viser vers la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.player.aim_at_mouse(mouse_x, mouse_y, self.camera.x, self.camera.y)

        # === Mise à jour des projectiles locaux ===
        for shell in self.shells[:]:
            shell.update()

        bouncing_obstacles = self.game_map.get_bouncing_obstacles()
        destroying_obstacles = self.game_map.get_destroying_obstacles()

        # Collisions projectiles locaux vs obstacles (rebonds, destruction)
        # + détection si on se touche soi-même (friendly fire après rebond)
        local_collision = ShellCollisions.check_all_collisions(
            self.shells,
            bouncing_obstacles,
            destroying_obstacles,
            [self.player]  # Seulement notre tank : on gère NOS HP
        )
        for tank, _shell in local_collision['tanks_hit']:
            tank.take_damage(25)
        if local_collision['shells_to_remove']:
            self.shells = [s for s in self.shells if s.active]

        # === Collisions projectiles adverses vs notre joueur ===
        # Les opponent_shells sont recréés depuis le réseau, on vérifie si
        # l'un d'eux touche notre tank
        if self.opponent_shells:
            opp_collision = ShellCollisions.check_all_collisions(
                self.opponent_shells,
                bouncing_obstacles,
                destroying_obstacles,
                [self.player]  # Seulement notre tank
            )
            for tank, _shell in opp_collision['tanks_hit']:
                tank.take_damage(25)
            if opp_collision['shells_to_remove']:
                self.opponent_shells = [s for s in self.opponent_shells if s.active]

        # Caméra
        self.camera.follow(self.player)

        # === Réseau ===
        if not self.receive_opponent_data():
            self.connection_lost = True
        self.send_player_data()

    def send_player_data(self):
        """Envoyer l'état du joueur + projectiles au réseau"""
        # Sérialiser les projectiles
        shells_data = []
        for s in self.shells:
            if s.active:
                shells_data.append({
                    "x": round(s.x, 1),
                    "y": round(s.y, 1),
                    "vx": round(s.vx, 2),
                    "vy": round(s.vy, 2),
                    "bounces": s.bounces,
                })

        data = {
            "x": self.player.x,
            "y": self.player.y,
            "angle": self.player.angle,
            "health": self.player.health,
            "shells_data": shells_data,
        }
        self.network.send(data)

    def receive_opponent_data(self):
        """Recevoir l'état de l'adversaire + ses projectiles du réseau.
        Draine toute la file d'attente et n'applique que le dernier
        message d'état de jeu (pour éviter le retard / les dégâts en double)."""
        latest_game_data = None

        # Vider toute la file : garder seulement le dernier état de jeu
        while True:
            data = self.network.receive()
            if data is None:
                break
            # Messages non-jeu (sync scoreboard, rematch) → ignorer
            if "scores_sync" in data or "scores_merged" in data or "rematch" in data:
                continue
            # C'est un message d'état de jeu → ne garder que le plus récent
            latest_game_data = data

        if latest_game_data is None:
            return True  # Pas de nouvelles données, ce n'est pas une erreur

        try:
            data = latest_game_data

            # Mise à jour position/angle adversaire
            self.opponent.x = data.get("x", self.opponent.x)
            self.opponent.y = data.get("y", self.opponent.y)
            self.opponent.angle = data.get("angle", self.opponent.angle)
            self.opponent.health = data.get("health", self.opponent.health)

            # Recréer les projectiles de l'adversaire depuis les données réseau
            shells_data = data.get("shells_data", [])
            new_opponent_shells = []
            for sd in shells_data:
                # Créer un Shell "fantôme" avec les données reçues
                s = Shell(sd["x"], sd["y"], 0, self.opponent)
                # Écraser la vélocité calculée par le constructeur
                s.vx = sd["vx"]
                s.vy = sd["vy"]
                s.bounces = sd["bounces"]
                s.active = True
                # Mettre la bonne couleur selon les bounces
                s._update_color()
                new_opponent_shells.append(s)
            self.opponent_shells = new_opponent_shells

            return True
        except Exception as e:
            print(f"Erreur réception données: {e}")
            return False

    def _draw_health_bar(self, x, y, width, height, health, max_health=100):
        """Dessine une barre de vie"""
        ratio = max(0.0, health / max_health)
        pygame.draw.rect(self.screen, (100, 0, 0), (x, y, width, height))
        if ratio > 0.5:
            bar_color = (0, 255, 0)
        elif ratio > 0.25:
            bar_color = (255, 200, 0)
        else:
            bar_color = (255, 0, 0)
        pygame.draw.rect(self.screen, bar_color, (x, y, int(width * ratio), height))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, width, height), 2)

    def draw(self):
        """Affichage du jeu"""
        self.screen.fill((20, 20, 30))
        self.camera.follow(self.player)
        self.game_map.draw(self.screen, self.camera.x, self.camera.y)

        # Projectiles (les nôtres + ceux de l'adversaire)
        for shell in self.shells:
            shell.draw(self.screen, self.camera.x, self.camera.y)
        for shell in self.opponent_shells:
            shell.draw(self.screen, self.camera.x, self.camera.y)

        # Tanks
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        self.opponent.draw(self.screen, self.camera.x, self.camera.y)

        # === HUD ===
        player_label = self.font.render(f"Vous: {self.player.health} HP", True, (0, 255, 0))
        self.screen.blit(player_label, (10, 10))
        self._draw_health_bar(10, 45, 200, 18, self.player.health)

        opponent_label = self.font.render(f"Adversaire: {self.opponent.health} HP", True, (255, 80, 80))
        self.screen.blit(opponent_label, (10, 72))
        self._draw_health_bar(10, 107, 200, 18, self.opponent.health)

        if self.player.reloading:
            reload_text = self.font_small.render("Rechargement...", True, (255, 100, 100))
            self.screen.blit(reload_text, (10, 132))
            # Barre de progression du rechargement
            progress = 1.0 - (self.player.reload_cooldown / self.player.reload_time)
            pygame.draw.rect(self.screen, (60, 60, 60), (10, 152, 150, 10))
            pygame.draw.rect(self.screen, (255, 165, 0), (10, 152, int(150 * progress), 10))
            pygame.draw.rect(self.screen, (255, 255, 255), (10, 152, 150, 10), 1)
        else:
            ammo_label = self.font_small.render(
                f"Munitions: {'● ' * self.player.ammo}{'○ ' * (self.player.mag_size - self.player.ammo)}  [R]",
                True, (255, 255, 0) if self.player.ammo > 0 else (255, 100, 100)
            )
            self.screen.blit(ammo_label, (10, 132))

        if self.connection_lost:
            error_msg = self.font.render("CONNEXION PERDUE!", True, (255, 0, 0))
            error_rect = error_msg.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2))
            self.screen.blit(error_msg, error_rect)

        esc_info = self.font_small.render("ESC pour quitter", True, (150, 150, 150))
        self.screen.blit(esc_info, (10, MENU_HEIGHT - 40))

        pygame.display.flip()

    def _show_end_screen(self, won):
        """Affiche l'écran de fin de partie avec option Rejouer / Menu.
        Gère aussi la saisie du nom, l'enregistrement du score et la
        synchronisation du scoreboard entre les deux joueurs."""
        font_big = pygame.font.Font(None, 72)
        font_info = pygame.font.Font(None, 36)
        font_option = pygame.font.Font(None, 48)

        if won:
            title_text = "VICTOIRE !"
            title_color = (0, 255, 0)
            sub_text = "Vous avez détruit l'adversaire !"
        else:
            title_text = "DÉFAITE..."
            title_color = (255, 0, 0)
            sub_text = "Votre tank a été détruit !"

        # --- Étape 1 : Saisie du nom ---
        name_screen = NameInput(self.screen, won, mode="multi")
        player_name = name_screen.run()
        if player_name:
            add_score(player_name, won)

        # --- Étape 2 : Synchroniser le scoreboard via le réseau ---
        # Envoyer notre scoreboard complet à l'adversaire
        try:
            my_scores = get_leaderboard()
            self.network.send({"scores_sync": my_scores})

            # Attendre de recevoir le scoreboard de l'adversaire (timeout 5 s)
            start_time = time.time()
            remote_scores = None
            while time.time() - start_time < 5:
                data = self.network.receive()
                if data and "scores_sync" in data:
                    remote_scores = data["scores_sync"]
                    break
                pygame.time.wait(50)

            if remote_scores:
                merge_scores(remote_scores)
                # Renvoyer le scoreboard fusionné pour que l'autre joueur le reçoive aussi
                merged = get_leaderboard()
                self.network.send({"scores_merged": merged})

                # Attendre le scoreboard fusionné de l'adversaire aussi
                start2 = time.time()
                while time.time() - start2 < 3:
                    data2 = self.network.receive()
                    if data2 and "scores_merged" in data2:
                        merge_scores(data2["scores_merged"])
                        break
                    pygame.time.wait(50)
        except Exception as e:
            print(f"Erreur sync scoreboard: {e}")

        # --- Étape 3 : Menu Rejouer / Menu ---
        selected = 0
        options = ["REJOUER", "MENU"]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        selected = 1 - selected
                    if event.key == pygame.K_RETURN:
                        return options[selected]
                    if event.key == pygame.K_ESCAPE:
                        return "MENU"

            overlay = pygame.Surface((MENU_WIDTH, MENU_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))

            title = font_big.render(title_text, True, title_color)
            title_rect = title.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 - 100))
            self.screen.blit(title, title_rect)

            sub = font_info.render(sub_text, True, (255, 200, 100))
            sub_rect = sub.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 - 40))
            self.screen.blit(sub, sub_rect)

            for i, opt in enumerate(options):
                color = (255, 255, 255) if i == selected else (100, 100, 100)
                text = font_option.render(opt, True, color)
                text_rect = text.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + 40 + i * 60))
                self.screen.blit(text, text_rect)
                if i == selected:
                    pygame.draw.polygon(self.screen, (255, 200, 0), [
                        (text_rect.left - 30, text_rect.centery),
                        (text_rect.left - 15, text_rect.centery - 10),
                        (text_rect.left - 15, text_rect.centery + 10)
                    ])

            pygame.display.flip()
            self.clock.tick(FPS)

    def run(self):
        """Boucle principale du jeu (avec support rematch)"""
        while True:
            self.running = True

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
                    won = self.player.health > 0

                    choice = self._show_end_screen(won)

                    if choice == "REJOUER":
                        self._init_game()
                        self.network.send({"rematch": True})
                        break
                    else:
                        self.network.stop() if self.is_host else self.network.disconnect()
                        return "MENU_SCORED"

