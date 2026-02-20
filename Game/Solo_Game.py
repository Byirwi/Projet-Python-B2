import pygame
import sys
from Game.Assets.Map import GameMap
from Game.Assets.Tank import Tank
from Game.Assets.Camera import Camera
from Game.Movement.Player_Movement import PlayerMovement
from Game.Movement.Shell_Movement import ShellMovement
from Game.Collisions.Shell_Collisions import ShellCollisions
from Game.Powerups.PowerUp_Manager import PowerUpManager
from Config import MENU_WIDTH, MENU_HEIGHT, FPS, MAP_WIDTH, MAP_HEIGHT


class SoloGame:

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.game_map = GameMap()
        self.player = Tank(MAP_WIDTH // 2, MAP_HEIGHT // 2, (0, 255, 0))
        self.camera = Camera(MENU_WIDTH, MENU_HEIGHT)
        self.shells = []
        self.powerup_manager = PowerUpManager()
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

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

    def update(self):
        keys = pygame.key.get_pressed()

        solid_obstacles = self.game_map.get_solid_obstacles()
        PlayerMovement.handle_input(self.player, keys, solid_obstacles, self.game_map)
        self.player.update()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.player.aim_at_mouse(mouse_x, mouse_y, self.camera.x, self.camera.y)

        self.shells = ShellMovement.update_shells(self.shells)

        # Seuls les rochers font rebondir ; l'eau est gérée comme solide pour le tank
        bouncing = self.game_map.get_bouncing_obstacles()
        result = ShellCollisions.check_all_collisions(
            self.shells, bouncing, [],
            [self.player]  # friendly fire après rebond
        )
        for tank, _shell in result['tanks_hit']:
            tank.take_damage(25)
        if result['shells_to_remove']:
            self.shells = [s for s in self.shells if s.active]

        # Spawn + pickup + effets actifs des power-ups
        self.powerup_manager.update(self.player, solid_obstacles)

        self.camera.follow(self.player)

    def draw(self):
        self.game_map.draw(self.screen, self.camera.x, self.camera.y)

        for shell in self.shells:
            shell.draw(self.screen, self.camera.x, self.camera.y)
        self.powerup_manager.draw(self.screen, self.camera.x, self.camera.y)
        self.player.draw(self.screen, self.camera.x, self.camera.y)

        # HUD — debug
        self.screen.blit(self.font_small.render(
            f"Pos: ({int(self.player.x)}, {int(self.player.y)}) | "
            f"Chassic: {int(self.player.hull_angle)}° | Tourelle: {int(self.player.turret_angle)}° | Shells: {len(self.shells)}",
            True, (255, 255, 255)), (10, 10))

        # HP
        self.screen.blit(
            self.font.render(f"HP: {self.player.health}", True, (255, 255, 255)), (10, 35))

        # Barre de vie
        bx, by, bw, bh = 10, 65, 200, 20
        ratio = max(0.0, self.player.health / 100.0)
        bar_color = (0, 255, 0) if ratio > 0.5 else (255, 200, 0) if ratio > 0.25 else (255, 0, 0)
        pygame.draw.rect(self.screen, (100, 0, 0), (bx, by, bw, bh))
        pygame.draw.rect(self.screen, bar_color, (bx, by, int(bw * ratio), bh))
        pygame.draw.rect(self.screen, (255, 255, 255), (bx, by, bw, bh), 2)

        # Munitions / rechargement
        ammo_y = 92
        if self.player.reloading:
            self.screen.blit(
                self.font_small.render("Rechargement...", True, (255, 100, 100)), (10, ammo_y))
            progress = 1.0 - (self.player.reload_cooldown / self.player.reload_time)
            pygame.draw.rect(self.screen, (60, 60, 60), (10, ammo_y + 20, 150, 10))
            pygame.draw.rect(self.screen, (255, 165, 0), (10, ammo_y + 20, int(150 * progress), 10))
            pygame.draw.rect(self.screen, (255, 255, 255), (10, ammo_y + 20, 150, 10), 1)
        else:
            p = self.player
            dots = '● ' * p.ammo + '○ ' * (p.mag_size - p.ammo)
            color = (255, 255, 0) if p.ammo > 0 else (255, 100, 100)
            self.screen.blit(
                self.font_small.render(f"Munitions: {dots} [R] Recharger", True, color), (10, ammo_y))

        self.powerup_manager.draw_hud(self.screen, self.font_small, self.player, x=10, y=118)

        self.screen.blit(self.font_small.render(
            "Flèches/ZQSD: Déplacer | Souris: Viser | Clic: Tirer | R: Recharger | ESC: Menu",
            True, (255, 255, 255)), (10, MENU_HEIGHT - 30))

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)

            result = self.handle_events()
            if result == "QUIT":
                pygame.quit(); sys.exit()
            elif result == "MENU":
                return "MENU"

            self.update()

            if self.player.health <= 0:
                self._show_game_over()
                return "MENU"

            self.draw()

    def _show_game_over(self):
        """Écran Game Over (3 s ou appui touche)."""
        font_big = pygame.font.Font(None, 72)
        font_info = pygame.font.Font(None, 36)
        start = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start < 3000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    return

            overlay = pygame.Surface((MENU_WIDTH, MENU_HEIGHT))
            overlay.fill((0, 0, 0)); overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))

            go = font_big.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(go, go.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 - 30)))

            info = font_info.render("Touché par votre propre projectile !", True, (255, 200, 100))
            self.screen.blit(info, info.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + 30)))

            ret = font_info.render("Retour au menu...", True, (200, 200, 200))
            self.screen.blit(ret, ret.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + 80)))

            pygame.display.flip()
            self.clock.tick(FPS)

