import pygame
import math

class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.color = color
        self.speed = 3
        self.angle = 0

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
        """Oriente le canon vers le curseur."""
        tank_cx = self.x + self.width // 2
        tank_cy = self.y + self.height // 2
        dx = (mouse_x + camera_x) - tank_cx
        dy = (mouse_y + camera_y) - tank_cy
        self.angle = math.degrees(math.atan2(dy, dx)) + 90

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
        """Tire un projectile depuis le bout du canon. Retourne un Shell ou None."""
        if not self.can_fire():
            return None

        from Game.Assets.Shell import Shell

        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        rad = math.radians(self.angle - 90)
        start_x = cx + 25 * math.cos(rad)
        start_y = cy + 25 * math.sin(rad)

        self.ammo -= 1
        self.fire_cooldown = self.fire_delay

        # Chargeur vide → rechargement auto
        if self.ammo <= 0:
            self.reloading = True
            self.reload_cooldown = self.reload_time

        return Shell(start_x, start_y, self.angle, self)

    def draw(self, screen, camera_x, camera_y):
        sx = self.x - camera_x
        sy = self.y - camera_y

        # Corps
        pygame.draw.rect(screen, self.color, (sx, sy, self.width, self.height))

        # Canon (trait blanc qui part du centre)
        cx = sx + self.width // 2
        cy = sy + self.height // 2
        rad = math.radians(self.angle - 90)
        end_x = cx + 25 * math.cos(rad)
        end_y = cy + 25 * math.sin(rad)
        pygame.draw.line(screen, (255, 255, 255), (cx, cy), (end_x, end_y), 3)
