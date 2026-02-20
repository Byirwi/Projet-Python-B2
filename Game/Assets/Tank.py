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

        # Créer une surface temporaire pour dessiner le tank (sans rotation)
        tank_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        tank_surface.fill((0, 0, 0, 0))  # Transparent
        
        offset_x, offset_y = 5, 5  # Offset pour la rotation autour du centre
        
        # ===== CORPS DU TANK =====
        body_color = self.color
        body_dark = tuple(max(0, c - 40) for c in self.color)
        
        # Chassis principal
        pygame.draw.rect(tank_surface, body_color, (offset_x, offset_y, self.width, self.height))
        
        # Bordure du chassis
        pygame.draw.rect(tank_surface, body_dark, (offset_x, offset_y, self.width, self.height), 2)
        
        # ===== CHENILLES (côtés) - Longueur complète =====
        tread_color = (40, 40, 40)
        
        # Chenille gauche (longueur complète)
        pygame.draw.rect(tank_surface, tread_color, (offset_x - 4, offset_y, 4, self.height))
        pygame.draw.rect(tank_surface, (20, 20, 20), (offset_x - 4, offset_y, 4, self.height), 1)
        
        # Chenille droite (longueur complète)
        pygame.draw.rect(tank_surface, tread_color, (offset_x + self.width, offset_y, 4, self.height))
        pygame.draw.rect(tank_surface, (20, 20, 20), (offset_x + self.width, offset_y, 4, self.height), 1)
        
        # ===== TOURELLE (turret) =====
        turret_radius = 12
        cx = offset_x + self.width // 2
        cy = offset_y + self.height // 2
        
        # Tourelle circulaire
        pygame.draw.circle(tank_surface, body_color, (int(cx), int(cy)), turret_radius)
        pygame.draw.circle(tank_surface, body_dark, (int(cx), int(cy)), turret_radius, 2)
        
        # Écoutille au centre (cercle plus clair)
        pygame.draw.circle(tank_surface, tuple(min(255, c + 60) for c in body_color), (int(cx), int(cy)), 4)
        
        # ===== CANON (barrel) - orienté vers le haut (angle 0) =====
        # Le canon pointe vers le haut au départ (angle 0)
        barrel_length = 28
        barrel_end_x = cx
        barrel_end_y = cy - barrel_length
        
        # Canon épais (principal)
        pygame.draw.line(tank_surface, (200, 200, 200), 
                        (cx, cy), 
                        (barrel_end_x, barrel_end_y), 5)
        
        # Canon foncé (intérieur pour effet 3D)
        pygame.draw.line(tank_surface, (100, 100, 100), 
                        (cx, cy), 
                        (barrel_end_x, barrel_end_y), 2)
        
        # Anneau de sortie
        pygame.draw.circle(tank_surface, (150, 150, 150), (int(barrel_end_x), int(barrel_end_y)), 4)
        pygame.draw.circle(tank_surface, (80, 80, 80), (int(barrel_end_x), int(barrel_end_y)), 4, 1)
        
        # ===== ROTATION DU TANK =====
        # Rotation autour du centre de la surface
        rotated_surface = pygame.transform.rotate(tank_surface, -self.angle)
        rotated_rect = rotated_surface.get_rect(center=(sx + self.width // 2, sy + self.height // 2))
        
        # Blitter la surface rotée
        screen.blit(rotated_surface, rotated_rect.topleft)
        
        # ===== AFFICHAGE DE SANTÉ (barre au-dessus) - non-rotée =====
        health_bar_width = self.width
        health_ratio = max(0, self.health / 100.0)
        health_bar_x = sx
        health_bar_y = sy - 8
        health_bar_height = 5
        
        # Fond de la barre de santé
        pygame.draw.rect(screen, (50, 50, 50), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Barre de santé colorée
        if health_ratio > 0.5:
            health_color = (0, 255, 0)
        elif health_ratio > 0.25:
            health_color = (255, 200, 0)
        else:
            health_color = (255, 0, 0)
        
        pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 1)

