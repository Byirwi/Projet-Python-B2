import pygame
import math
from Config import MAP_WIDTH, MAP_HEIGHT

class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.color = color
        self.speed = 3
        self.angle = 0  # Direction du tank (0 = haut)
        
        # Cooldown de tir
        self.fire_cooldown = 0
        self.fire_delay = 30  # Délai entre deux tirs (en frames, ~0.5s à 60 FPS)
        
    def aim_at_mouse(self, mouse_x, mouse_y, camera_x, camera_y):
        """
        Fait viser le canon du tank vers la position de la souris
        
        Args:
            mouse_x, mouse_y: Position de la souris à l'écran
            camera_x, camera_y: Position de la caméra
        """
        # Position du centre du tank dans le monde
        tank_center_x = self.x + self.width // 2
        tank_center_y = self.y + self.height // 2
        
        # Position de la souris dans le monde (souris + caméra)
        world_mouse_x = mouse_x + camera_x
        world_mouse_y = mouse_y + camera_y
        
        # Calculer l'angle entre le tank et la souris
        dx = world_mouse_x - tank_center_x
        dy = world_mouse_y - tank_center_y
        
        # Calculer l'angle en degrés (atan2 retourne en radians)
        self.angle = math.degrees(math.atan2(dy, dx)) + 90
    
    def update(self):
        """Met à jour l'état du tank"""
        # Réduire le cooldown de tir
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
    
    def can_fire(self):
        """Vérifie si le tank peut tirer"""
        return self.fire_cooldown == 0
    
    def fire(self):
        """
        Crée un projectile tiré depuis ce tank
        
        Returns:
            Shell: Nouveau projectile, ou None si cooldown actif
        """
        if not self.can_fire():
            return None
        
        # Position de départ : bout du canon
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Décaler la position de départ au bout du canon
        angle_rad = math.radians(self.angle - 90)
        cannon_length = 25
        start_x = center_x + cannon_length * math.cos(angle_rad)
        start_y = center_y + cannon_length * math.sin(angle_rad)
        
        # Import ici pour éviter import circulaire
        from Game.Assets.Shell import Shell
        
        # Activer le cooldown
        self.fire_cooldown = self.fire_delay
        
        return Shell(start_x, start_y, self.angle, self)
        
    def draw(self, screen, camera_x, camera_y):
        """Dessine le tank à l'écran"""
        # Position relative à la caméra
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Corps du tank
        pygame.draw.rect(screen, self.color, 
                        (screen_x, screen_y, self.width, self.height))
        
        # Canon du tank (ligne pointant dans la direction)
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        # Calculer la fin du canon selon l'angle
        angle_rad = math.radians(self.angle - 90)  # -90 car 0° = haut
        cannon_length = 25
        end_x = center_x + cannon_length * math.cos(angle_rad)
        end_y = center_y + cannon_length * math.sin(angle_rad)
        
        pygame.draw.line(screen, (255, 255, 255), 
                        (center_x, center_y), (end_x, end_y), 3)