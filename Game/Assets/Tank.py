import pygame
import math

class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.color = color
        self.speed = 4
        self.hull_angle = 0      # Angle du châssis (déplacement)
        self.turret_angle = 0    # Angle de la tourelle (souris)

        self.health = 100

        # Chargeur : 3 balles, 0.5s entre chaque tir, 2s de reload
        self.mag_size = 3
        self.ammo = self.mag_size
        self.fire_cooldown = 0
        self.fire_delay = 30        # ~0.5s @ 60 FPS

        self.reloading = False
        self.reload_cooldown = 0
        self.reload_time = 120      # ~2s @ 60 FPS

    def aim_at_mouse(self, mouse_x, mouse_y, camera_x, camera_y):
        """Oriente la tourelle vers le curseur (indépendamment du châssis)."""
        tank_cx = self.x + self.width // 2
        tank_cy = self.y + self.height // 2
        dx = (mouse_x + camera_x) - tank_cx
        dy = (mouse_y + camera_y) - tank_cy
        self.turret_angle = math.degrees(math.atan2(dy, dx)) + 90

    def update(self):
        """Tick : cooldown de tir + progression du rechargement."""
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        if self.reloading:
            self.reload_cooldown -= 1
            if self.reload_cooldown <= 0:
                self.ammo = self.mag_size
                self.reloading = False
                self.reload_cooldown = 0

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def reload(self):
        """Rechargement manuel (touche R)."""
        if not self.reloading and self.ammo < self.mag_size:
            self.reloading = True
            self.reload_cooldown = self.reload_time
            self.fire_cooldown = 0

    def can_fire(self):
        return self.fire_cooldown == 0 and self.ammo > 0 and not self.reloading

    def fire(self):
        """Tire un projectile depuis le bout du canon (tourelle). Retourne un Shell ou None."""
        if not self.can_fire():
            return None

        from Game.Assets.Shell import Shell

        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        rad = math.radians(self.turret_angle - 90)
        start_x = cx + 25 * math.cos(rad)
        start_y = cy + 25 * math.sin(rad)

        self.ammo -= 1
        self.fire_cooldown = self.fire_delay

        # Chargeur vide → rechargement auto
        if self.ammo <= 0:
            self.reloading = True
            self.reload_cooldown = self.reload_time

        return Shell(start_x, start_y, self.turret_angle, self)

    def draw(self, screen, camera_x, camera_y):
        sx = self.x - camera_x
        sy = self.y - camera_y
        cx = sx + self.width // 2
        cy = sy + self.height // 2

        body_color = self.color
        body_dark = tuple(max(0, c - 40) for c in self.color)
        tread_color = (40, 40, 40)

        # ===== CHÂSSIS (hull) avec rotation hull_angle =====
        hull_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        offset = 5

        # Corps principal
        pygame.draw.rect(hull_surface, body_color, (offset, offset, self.width, self.height))
        pygame.draw.rect(hull_surface, body_dark, (offset, offset, self.width, self.height), 2)

        # Chenilles gauche/droite
        pygame.draw.rect(hull_surface, tread_color, (offset - 4, offset, 4, self.height))
        pygame.draw.rect(hull_surface, (20, 20, 20), (offset - 4, offset, 4, self.height), 1)
        pygame.draw.rect(hull_surface, tread_color, (offset + self.width, offset, 4, self.height))
        pygame.draw.rect(hull_surface, (20, 20, 20), (offset + self.width, offset, 4, self.height), 1)

        rotated_hull = pygame.transform.rotate(hull_surface, -self.hull_angle)
        hull_rect = rotated_hull.get_rect(center=(cx, cy))
        screen.blit(rotated_hull, hull_rect.topleft)

        # ===== TOURELLE (turret) avec rotation turret_angle =====
        turret_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        t_center = 30

        # Tourelle circulaire
        pygame.draw.circle(turret_surface, body_color, (t_center, t_center), 12)
        pygame.draw.circle(turret_surface, body_dark, (t_center, t_center), 12, 2)
        # Écoutille
        pygame.draw.circle(turret_surface, tuple(min(255, c + 60) for c in body_color), (t_center, t_center), 4)

        # Canon (vers le haut de la surface non-tournée)
        barrel_length = 28
        barrel_end_y = t_center - barrel_length
        pygame.draw.line(turret_surface, (200, 200, 200), (t_center, t_center), (t_center, barrel_end_y), 5)
        pygame.draw.line(turret_surface, (100, 100, 100), (t_center, t_center), (t_center, barrel_end_y), 2)
        pygame.draw.circle(turret_surface, (150, 150, 150), (t_center, int(barrel_end_y)), 4)
        pygame.draw.circle(turret_surface, (80, 80, 80), (t_center, int(barrel_end_y)), 4, 1)

        rotated_turret = pygame.transform.rotate(turret_surface, -self.turret_angle)
        turret_rect = rotated_turret.get_rect(center=(cx, cy))
        screen.blit(rotated_turret, turret_rect.topleft)

        # ===== BARRE DE SANTÉ (non-tournée) =====
        health_ratio = max(0, self.health / 100.0)
        hb_x, hb_y = sx, sy - 8
        hb_w, hb_h = self.width, 5
        pygame.draw.rect(screen, (50, 50, 50), (hb_x, hb_y, hb_w, hb_h))
        if health_ratio > 0.5:
            hc = (0, 255, 0)
        elif health_ratio > 0.25:
            hc = (255, 200, 0)
        else:
            hc = (255, 0, 0)
        pygame.draw.rect(screen, hc, (hb_x, hb_y, hb_w * health_ratio, hb_h))
        pygame.draw.rect(screen, (255, 255, 255), (hb_x, hb_y, hb_w, hb_h), 1)

