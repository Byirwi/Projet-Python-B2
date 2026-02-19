import pygame
import math
from Config import MAP_WIDTH, MAP_HEIGHT

class Shell:
    """Projectile tiré par un tank"""
    
    def __init__(self, x, y, angle, owner):
        """
        Crée un projectile
        
        Args:
            x, y: Position de départ (centre du tank)
            angle: Angle de tir (en degrés)
            owner: Référence au tank qui a tiré (pour attribution)
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        
        # Propriétés du projectile
        self.radius = 4  # Rayon du projectile (cercle)
        self.speed = 8   # Vitesse du projectile
        self.color = (255, 255, 0)  # Jaune
        
        # Calculer la direction en radians
        angle_rad = math.radians(angle - 90)
        self.vx = self.speed * math.cos(angle_rad)
        self.vy = self.speed * math.sin(angle_rad)
        
        # État
        self.active = True  # False quand le projectile doit être détruit
        self.bounces = 0    # Nombre de rebonds effectués
        self.max_bounces = 3  # Nombre maximum de rebonds
        
    def update(self):
        """Met à jour la position du projectile"""
        if not self.active:
            return
            
        # Déplacer selon la vélocité
        self.x += self.vx
        self.y += self.vy
        
        # Rebondir sur les bordures de la map
        bounced = False
        
        # Bordure gauche ou droite
        if self.x - self.radius <= 0 or self.x + self.radius >= MAP_WIDTH:
            if self.bounces < self.max_bounces:
                self.vx = -self.vx  # Inverser la direction horizontale
                # Repositionner dans les limites
                self.x = max(self.radius, min(self.x, MAP_WIDTH - self.radius))
                bounced = True
            else:
                self.active = False
                return
        
        # Bordure haut ou bas
        if self.y - self.radius <= 0 or self.y + self.radius >= MAP_HEIGHT:
            if self.bounces < self.max_bounces:
                self.vy = -self.vy  # Inverser la direction verticale
                # Repositionner dans les limites
                self.y = max(self.radius, min(self.y, MAP_HEIGHT - self.radius))
                bounced = True
            else:
                self.active = False
                return
        
        # Incrémenter le compteur de rebonds
        if bounced:
            self.bounces += 1
            self._update_color()
    
    def bounce_horizontal(self):
        """Fait rebondir le projectile horizontalement (sur un mur vertical)"""
        if self.bounces < self.max_bounces:
            self.vx = -self.vx
            self.bounces += 1
            self._update_color()
            return True
        else:
            self.active = False
            return False
    
    def bounce_vertical(self):
        """Fait rebondir le projectile verticalement (sur un mur horizontal)"""
        if self.bounces < self.max_bounces:
            self.vy = -self.vy
            self.bounces += 1
            self._update_color()
            return True
        else:
            self.active = False
            return False
    
    def _update_color(self):
        """Met à jour la couleur selon le nombre de rebonds"""
        if self.bounces == 1:
            self.color = (255, 200, 0)  # Orange
        elif self.bounces == 2:
            self.color = (255, 100, 0)  # Orange foncé
        elif self.bounces >= 3:
            self.color = (255, 0, 0)    # Rouge (dernier rebond)
    
    def draw(self, screen, camera_x, camera_y):
        """Dessine le projectile à l'écran"""
        if not self.active:
            return
            
        # Position relative à la caméra
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Dessiner un cercle avec la couleur actuelle
        pygame.draw.circle(screen, self.color, 
                          (int(screen_x), int(screen_y)), self.radius)
        
        # Dessiner un petit cercle blanc au centre pour l'effet
        pygame.draw.circle(screen, (255, 255, 255), 
                          (int(screen_x), int(screen_y)), max(1, self.radius // 2))