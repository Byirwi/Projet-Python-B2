import pygame
import sys
import time
from Game.Assets.Map import GameMap
from Game.Assets.Tank import Tank
from Game.Assets.Shell import Shell
from Game.Assets.Camera import Camera
from Game.Movement.Player_Movement import PlayerMovement
from Game.Collisions.Shell_Collisions import ShellCollisions
from Game.Powerups.PowerUp_Manager import PowerUpManager
from Config import MENU_WIDTH, MENU_HEIGHT, FPS, MAP_WIDTH, MAP_HEIGHT
from Score_Manager import add_score, get_leaderboard, merge_scores
from UI.Name_Input import NameInput


class MultiGame:

    def __init__(self, screen, network_obj, is_host=True):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.is_host = is_host
        self.network = network_obj
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self._init_game()

    def _init_game(self):
        """(Ré)initialise la partie — appelé aussi lors d'un rematch."""
        self.game_map = GameMap()

        if self.is_host:
            self.player = Tank(MAP_WIDTH // 4, MAP_HEIGHT // 2, (0, 100, 255))
            self.opponent_color = (255, 50, 50)
        else:
            self.player = Tank(3 * MAP_WIDTH // 4, MAP_HEIGHT // 2, (255, 50, 50))
            self.opponent_color = (0, 100, 255)

        self.opponent = Tank(
            3 * MAP_WIDTH // 4 if self.is_host else MAP_WIDTH // 4,
            MAP_HEIGHT // 2, self.opponent_color
        )

        self.camera = Camera(MENU_WIDTH, MENU_HEIGHT)
        self.shells = []            # nos projectiles
        self.opponent_shells = []   # projectiles reçus du réseau
        self._hit_shell_ids = set() # IDs des shells adverses ayant déjà infligé des dégâts
        
        # Power-ups (host gère spawn/lifetime, client synchronise les positions)
        self.powerup_manager = PowerUpManager()
        
        self.running = True
        self.connection_lost = False

    # ── Événements ──────────────────────────────────────────────

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if event.key == pygame.K_r:
                    self.player.reload()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shell = self.player.fire()
                if shell:
                    self.shells.append(shell)
        return None

    # ── Logique ─────────────────────────────────────────────────

    def update(self):
        keys = pygame.key.get_pressed()

        solid = self.game_map.get_solid_obstacles()
        PlayerMovement.handle_input(self.player, keys, solid, self.game_map)
        self.player.update()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.player.aim_at_mouse(mouse_x, mouse_y, self.camera.x, self.camera.y)

        for shell in self.shells[:]:
            shell.update()

        bouncing = self.game_map.get_bouncing_obstacles()
        destroying = self.game_map.get_destroying_obstacles()

        # Nos projectiles vs obstacles + friendly fire
        local = ShellCollisions.check_all_collisions(
            self.shells, bouncing, destroying, [self.player])
        for tank, _ in local['tanks_hit']:
            tank.take_damage(25)
        if local['shells_to_remove']:
            self.shells = [s for s in self.shells if s.active]

        # Projectiles adverses vs notre tank (dédupliqué par shell_id)
        if self.opponent_shells:
            opp = ShellCollisions.check_all_collisions(
                self.opponent_shells, bouncing, destroying, [self.player])
            for tank, s in opp['tanks_hit']:
                if s.shell_id not in self._hit_shell_ids:
                    self._hit_shell_ids.add(s.shell_id)
                    tank.take_damage(25)
            if opp['shells_to_remove']:
                self.opponent_shells = [s for s in self.opponent_shells if s.active]

        # Power-ups (host gère spawn/lifetime, client reçoit la liste)
        if self.is_host:
            self.powerup_manager.update(self.player, solid)
        else:
            # Client vérifie les pickups sur les powerups reçus
            self.powerup_manager._check_pickup(self.player)

        self.camera.follow(self.player)

        if not self.receive_opponent_data():
            self.connection_lost = True
        self.send_player_data()

    # ── Réseau ──────────────────────────────────────────────────

    def send_player_data(self):
        shells_data = [
            {"id": s.shell_id, "x": round(s.x, 1), "y": round(s.y, 1),
             "vx": round(s.vx, 2), "vy": round(s.vy, 2), "bounces": s.bounces}
            for s in self.shells if s.active
        ]
        
        # Host envoie la liste des power-ups
        powerups_data = []
        if self.is_host:
            powerups_data = [
                {"id": p.powerup_id, "x": round(p.x, 1), "y": round(p.y, 1), "type": p.power_type}
                for p in self.powerup_manager.powerups
            ]
        
        # Client envoie les IDs des powerups pickupés
        picked_ids = []
        if not self.is_host:
            picked_ids = self.powerup_manager.get_picked_ids()
        
        self.network.send({
            "x": self.player.x, "y": self.player.y,
            "hull_angle": self.player.hull_angle,
            "turret_angle": self.player.turret_angle,
            "health": self.player.health,
            "shells_data": shells_data,
            "powerups_data": powerups_data,
            "picked_powerup_ids": picked_ids,
        })

    def receive_opponent_data(self):
        """Draine la file réseau, n'applique que le dernier état de jeu."""
        latest = None
        while True:
            data = self.network.receive()
            if data is None:
                break
            # Ignorer les messages de contrôle (scores, rematch)
            if any(k in data for k in ("scores_sync", "scores_merged", "rematch")):
                continue
            latest = data

        if latest is None:
            return True

        try:
            self.opponent.x = latest.get("x", self.opponent.x)
            self.opponent.y = latest.get("y", self.opponent.y)
            self.opponent.hull_angle = latest.get("hull_angle", self.opponent.hull_angle)
            self.opponent.turret_angle = latest.get("turret_angle", self.opponent.turret_angle)
            self.opponent.health = latest.get("health", self.opponent.health)

            # Recréer les shells adverses depuis les données réseau
            self.opponent_shells = []
            active_ids = set()
            for sd in latest.get("shells_data", []):
                s = Shell(sd["x"], sd["y"], 0, self.opponent)
                s.shell_id = sd.get("id", s.shell_id)
                s.vx, s.vy, s.bounces = sd["vx"], sd["vy"], sd["bounces"]
                s.active = True
                s._update_color()
                self.opponent_shells.append(s)
                active_ids.add(s.shell_id)

            # Nettoyer les anciens IDs de shells qui n'existent plus
            self._hit_shell_ids &= active_ids

            # Synchroniser les power-ups reçus depuis le host
            powerups_data = latest.get("powerups_data", [])
            if powerups_data:
                self.powerup_manager.sync_received_powerups(powerups_data)
            
            # Host reçoit les IDs pickupés du client et les applique
            if self.is_host:
                picked_ids = latest.get("picked_powerup_ids", [])
                if picked_ids:
                    self.powerup_manager.apply_picked_ids(picked_ids)

            return True
        except Exception as e:
            print(f"Erreur réseau: {e}")
            return False

    # ── Affichage ───────────────────────────────────────────────

    def _draw_health_bar(self, x, y, w, h, health, max_hp=100):
        ratio = max(0.0, health / max_hp)
        color = (0, 255, 0) if ratio > 0.5 else (255, 200, 0) if ratio > 0.25 else (255, 0, 0)
        pygame.draw.rect(self.screen, (100, 0, 0), (x, y, w, h))
        pygame.draw.rect(self.screen, color, (x, y, int(w * ratio), h))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, w, h), 2)

    def draw(self):
        self.screen.fill((20, 20, 30))
        self.camera.follow(self.player)
        self.game_map.draw(self.screen, self.camera.x, self.camera.y)

        for shell in self.shells:
            shell.draw(self.screen, self.camera.x, self.camera.y)
        for shell in self.opponent_shells:
            shell.draw(self.screen, self.camera.x, self.camera.y)

        # Draw power-ups (host et client affichent via le manager)
        self.powerup_manager.draw(self.screen, self.camera.x, self.camera.y)

        self.player.draw(self.screen, self.camera.x, self.camera.y)
        self.opponent.draw(self.screen, self.camera.x, self.camera.y)

        # HUD — barres de vie
        self.screen.blit(
            self.font.render(f"Vous: {self.player.health} HP", True, (0, 255, 0)), (10, 10))
        self._draw_health_bar(10, 45, 200, 18, self.player.health)

        self.screen.blit(
            self.font.render(f"Adversaire: {self.opponent.health} HP", True, (255, 80, 80)), (10, 72))
        self._draw_health_bar(10, 107, 200, 18, self.opponent.health)

        # Power-up HUD (affichage des effets actifs)
        self.powerup_manager.draw_hud(self.screen, self.font_small, self.player)

        # Munitions / rechargement
        if self.player.reloading:
            self.screen.blit(
                self.font_small.render("Rechargement...", True, (255, 100, 100)), (10, 132))
            progress = 1.0 - (self.player.reload_cooldown / self.player.reload_time)
            pygame.draw.rect(self.screen, (60, 60, 60), (10, 152, 150, 10))
            pygame.draw.rect(self.screen, (255, 165, 0), (10, 152, int(150 * progress), 10))
            pygame.draw.rect(self.screen, (255, 255, 255), (10, 152, 150, 10), 1)
        else:
            p = self.player
            dots = '● ' * p.ammo + '○ ' * (p.mag_size - p.ammo)
            color = (255, 255, 0) if p.ammo > 0 else (255, 100, 100)
            self.screen.blit(
                self.font_small.render(f"Munitions: {dots} [R]", True, color), (10, 132))

        if self.connection_lost:
            msg = self.font.render("CONNEXION PERDUE!", True, (255, 0, 0))
            self.screen.blit(msg, msg.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2)))

        self.screen.blit(
            self.font_small.render("ESC pour quitter", True, (150, 150, 150)), (10, MENU_HEIGHT - 40))

        pygame.display.flip()

    # ── Fin de partie ───────────────────────────────────────────

    def _show_end_screen(self, won):
        """Saisie du nom → sync scoreboard réseau → menu rejouer/quitter."""
        font_big = pygame.font.Font(None, 72)
        font_info = pygame.font.Font(None, 36)
        font_opt = pygame.font.Font(None, 48)

        title_text = "VICTOIRE !" if won else "DÉFAITE..."
        title_color = (0, 255, 0) if won else (255, 0, 0)
        sub_text = "Vous avez détruit l'adversaire !" if won else "Votre tank a été détruit !"

        # 1) Saisie du nom + enregistrement local
        name_screen = NameInput(self.screen, won, mode="multi")
        player_name = name_screen.run()
        if player_name:
            add_score(player_name, won)

        # 2) Synchronisation des scoreboards via le réseau
        try:
            my_scores = get_leaderboard()
            self.network.send({"scores_sync": my_scores})

            # Attendre le scoreboard adverse (timeout 5 s)
            t0 = time.time()
            remote = None
            while time.time() - t0 < 5:
                data = self.network.receive()
                if data and "scores_sync" in data:
                    remote = data["scores_sync"]
                    break
                pygame.time.wait(50)

            if remote:
                merge_scores(remote)
                self.network.send({"scores_merged": get_leaderboard()})
                # Recevoir le scoreboard fusionné final
                t1 = time.time()
                while time.time() - t1 < 3:
                    data2 = self.network.receive()
                    if data2 and "scores_merged" in data2:
                        merge_scores(data2["scores_merged"])
                        break
                    pygame.time.wait(50)
        except Exception as e:
            print(f"Erreur sync scoreboard: {e}")

        # 3) Menu rejouer / quitter
        selected = 0
        options = ["REJOUER", "MENU"]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        selected = 1 - selected
                    if event.key == pygame.K_RETURN:
                        return options[selected]
                    if event.key == pygame.K_ESCAPE:
                        return "MENU"

            overlay = pygame.Surface((MENU_WIDTH, MENU_HEIGHT))
            overlay.fill((0, 0, 0)); overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))

            title = font_big.render(title_text, True, title_color)
            self.screen.blit(title, title.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 - 100)))

            sub = font_info.render(sub_text, True, (255, 200, 100))
            self.screen.blit(sub, sub.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 - 40)))

            for i, opt in enumerate(options):
                c = (255, 255, 255) if i == selected else (100, 100, 100)
                txt = font_opt.render(opt, True, c)
                r = txt.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + 40 + i * 60))
                self.screen.blit(txt, r)
                if i == selected:
                    pygame.draw.polygon(self.screen, (255, 200, 0), [
                        (r.left - 30, r.centery),
                        (r.left - 15, r.centery - 10),
                        (r.left - 15, r.centery + 10)])

            pygame.display.flip()
            self.clock.tick(FPS)

    # ── Boucle principale ───────────────────────────────────────

    def run(self):
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

