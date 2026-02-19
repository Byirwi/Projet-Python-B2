import pygame
from Config import MAP_WIDTH, MAP_HEIGHT, MENU_WIDTH, MENU_HEIGHT

class GameMap:
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        
        # Couleurs du terrain
        self.COLOR_GRASS = (34, 139, 34)      # Vert herbe
        self.COLOR_DIRT = (139, 90, 43)       # Marron terre
        self.COLOR_SAND = (194, 178, 128)     # Sable
        self.COLOR_WATER = (30, 144, 255)     # Bleu eau
        self.COLOR_ROCK = (105, 105, 105)     # Gris roche
        
        # Obstacles solides (rochers, murs, etc.) - REBONDISSENTl
        self.obstacles = [
            pygame.Rect(600, 400, 100, 100),    # Rocher 1
            pygame.Rect(1000, 600, 150, 80),    # Rocher 2
            pygame.Rect(1600, 1100, 120, 120),  # Rocher 3
            pygame.Rect(300, 800, 80, 200),     # Mur vertical
            pygame.Rect(1800, 200, 200, 80),    # Mur horizontal
        ]
        
        # Zones de sable (non solides, juste visuel)
        self.sand_zones = [
            pygame.Rect(200, 200, 400, 300),
            pygame.Rect(1500, 800, 500, 400),
            pygame.Rect(800, 1200, 600, 300)
        ]
        
        # Zones d'eau (obstacles sans rebond - détruisent les projectiles)
        self.water_zones = [
            pygame.Rect(1200, 200, 300, 300),
            pygame.Rect(400, 1000, 400, 200)
        ]
        
        # Zones de terre (non solides, juste visuel)
        self.dirt_zones = [
            pygame.Rect(1800, 400, 400, 400),
            pygame.Rect(100, 700, 300, 300)
        ]
        
        # Surface de la map (plus grande que l'écran)
        self.surface = pygame.Surface((self.width, self.height))
        self.generate_terrain()
        
    def generate_terrain(self):
        """Génère un terrain simple avec différentes zones"""
        # Remplir avec de l'herbe
        self.surface.fill(self.COLOR_GRASS)
        
        # Zones de sable
        for zone in self.sand_zones:
            pygame.draw.rect(self.surface, self.COLOR_SAND, zone)
        
        # Zones d'eau
        for zone in self.water_zones:
            pygame.draw.rect(self.surface, self.COLOR_WATER, zone)
            
        # Zones de terre
        for zone in self.dirt_zones:
            pygame.draw.rect(self.surface, self.COLOR_DIRT, zone)
        
        # Obstacles solides (rochers)
        for obstacle in self.obstacles:
            pygame.draw.rect(self.surface, self.COLOR_ROCK, obstacle)
            # Bordure plus foncée pour les obstacles
            pygame.draw.rect(self.surface, (70, 70, 70), obstacle, 3)
    
    def get_solid_obstacles(self):
        """Retourne tous les obstacles solides pour les tanks (eau + rochers)"""
        return self.water_zones + self.obstacles
    
    def get_bouncing_obstacles(self):
        """Retourne uniquement les obstacles qui font rebondir (rochers)"""
        return self.obstacles
    
    def get_destroying_obstacles(self):
        """Retourne les obstacles qui détruisent les projectiles (eau)"""
        return self.water_zones
    
    def draw(self, screen, camera_x, camera_y):
        """
        Affiche la partie visible de la map selon la position de la caméra
        
        Args:
            screen: Surface pygame de l'écran
            camera_x, camera_y: Position de la caméra
        """
        # Calculer quelle partie de la map afficher
        view_rect = pygame.Rect(camera_x, camera_y, MENU_WIDTH, MENU_HEIGHT)
        
        # Limiter la caméra aux bordures de la map
        if view_rect.left < 0:
            view_rect.left = 0
        if view_rect.top < 0:
            view_rect.top = 0
        if view_rect.right > self.width:
            view_rect.right = self.width
        if view_rect.bottom > self.height:
            view_rect.bottom = self.height
        
        # Afficher la portion visible
        screen.blit(self.surface, (0, 0), view_rect)