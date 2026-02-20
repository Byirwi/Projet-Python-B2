import pygame
from Config import MAP_WIDTH, MAP_HEIGHT, MENU_WIDTH, MENU_HEIGHT


class GameMap:
    """Carte du jeu : génère le terrain, expose les obstacles par catégorie."""

    # Palette
    COLOR_GRASS = (34, 139, 34)
    COLOR_DIRT  = (139, 90, 43)
    COLOR_SAND  = (194, 178, 128)
    COLOR_WATER = (30, 144, 255)
    COLOR_ROCK  = (105, 105, 105)

    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT

        # Rochers / murs — solides, font rebondir les projectiles
        self.obstacles = [
            pygame.Rect(600, 400, 100, 100),
            pygame.Rect(1000, 600, 150, 80),
            pygame.Rect(1600, 1100, 120, 120),
            pygame.Rect(300, 800, 80, 200),
            pygame.Rect(1800, 200, 200, 80),
        ]

        # Zones décoratives (pas de collision)
        self.sand_zones = [
            pygame.Rect(200, 200, 400, 300),
            pygame.Rect(1500, 800, 500, 400),
            pygame.Rect(800, 1200, 600, 300),
        ]
        self.dirt_zones = [
            pygame.Rect(1800, 400, 400, 400),
            pygame.Rect(100, 700, 300, 300),
        ]

        # Eau — bloque les tanks, détruit les projectiles (pas de rebond)
        self.water_zones = [
            pygame.Rect(1200, 200, 300, 300),
            pygame.Rect(400, 1000, 400, 200),
        ]

        self.surface = pygame.Surface((self.width, self.height))
        self._generate_terrain()

    def _generate_terrain(self):
        self.surface.fill(self.COLOR_GRASS)

        for zone in self.sand_zones:
            pygame.draw.rect(self.surface, self.COLOR_SAND, zone)
        for zone in self.water_zones:
            pygame.draw.rect(self.surface, self.COLOR_WATER, zone)
        for zone in self.dirt_zones:
            pygame.draw.rect(self.surface, self.COLOR_DIRT, zone)

        for obs in self.obstacles:
            pygame.draw.rect(self.surface, self.COLOR_ROCK, obs)
            pygame.draw.rect(self.surface, (70, 70, 70), obs, 3)  # bordure

    # --- Accesseurs pour le système de collision ---

    def get_solid_obstacles(self):
        """Obstacles qui bloquent le déplacement des tanks (rochers + eau)."""
        return self.water_zones + self.obstacles

    def get_bouncing_obstacles(self):
        """Obstacles qui font rebondir les projectiles (rochers uniquement)."""
        return self.obstacles

    def get_destroying_obstacles(self):
        """Obstacles qui détruisent les projectiles (eau)."""
        return self.water_zones

    def draw(self, screen, camera_x, camera_y):
        """Blit la portion visible de la map."""
        view = pygame.Rect(camera_x, camera_y, MENU_WIDTH, MENU_HEIGHT)
        view.clamp_ip(pygame.Rect(0, 0, self.width, self.height))
        screen.blit(self.surface, (0, 0), view)
