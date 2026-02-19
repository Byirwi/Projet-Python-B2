import pygame
import math
from Config import MAP_WIDTH, MAP_HEIGHT


class Shell:
    """Projectile avec rebonds. Change de couleur à chaque rebond."""

    _next_id = 0  # compteur global pour identifiant unique

    def __init__(self, x, y, angle, owner):
        Shell._next_id += 1
        self.shell_id = Shell._next_id

        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner  # pour ignorer la self-collision avant le 1er rebond

        self.radius = 4
        self.speed = 8
        self.color = (255, 255, 0)

        # Vecteur vitesse calculé depuis l'angle
        rad = math.radians(angle - 90)
        self.vx = self.speed * math.cos(rad)
        self.vy = self.speed * math.sin(rad)

        self.active = True
        self.bounces = 0
        self.max_bounces = 3

    def update(self):
        if not self.active:
            return

        self.x += self.vx
        self.y += self.vy

        bounced = False

        # Rebond sur les bords horizontaux de la map
        if self.x - self.radius <= 0 or self.x + self.radius >= MAP_WIDTH:
            if self.bounces < self.max_bounces:
                self.vx = -self.vx
                self.x = max(self.radius, min(self.x, MAP_WIDTH - self.radius))
                bounced = True
            else:
                self.active = False
                return

        # Rebond sur les bords verticaux de la map
        if self.y - self.radius <= 0 or self.y + self.radius >= MAP_HEIGHT:
            if self.bounces < self.max_bounces:
                self.vy = -self.vy
                self.y = max(self.radius, min(self.y, MAP_HEIGHT - self.radius))
                bounced = True
            else:
                self.active = False
                return

        if bounced:
            self.bounces += 1
            self._update_color()

    def bounce_horizontal(self):
        """Rebond sur un mur vertical (inverse vx)."""
        if self.bounces < self.max_bounces:
            self.vx = -self.vx
            self.bounces += 1
            self._update_color()
            return True
        self.active = False
        return False

    def bounce_vertical(self):
        """Rebond sur un mur horizontal (inverse vy)."""
        if self.bounces < self.max_bounces:
            self.vy = -self.vy
            self.bounces += 1
            self._update_color()
            return True
        self.active = False
        return False

    def _update_color(self):
        """Jaune → Orange → Orange foncé → Rouge selon les rebonds."""
        colors = {1: (255, 200, 0), 2: (255, 100, 0)}
        self.color = colors.get(self.bounces, (255, 0, 0))

    def draw(self, screen, camera_x, camera_y):
        if not self.active:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (sx, sy), max(1, self.radius // 2))
