import pygame
import random
import math
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
        self.rng = random.Random(42)

        # Rochers / murs — solides, font rebondir les projectiles
        self.obstacles = [
            pygame.Rect(587, 423, 97, 103),
            pygame.Rect(1013, 594, 147, 83),
            pygame.Rect(1587, 1094, 127, 118),
            pygame.Rect(314, 812, 73, 194),
            pygame.Rect(1823, 217, 193, 76),
            pygame.Rect(213, 1287, 487, 213),    
            pygame.Rect(1117, 1214, 163, 337), 
            pygame.Rect(1794, 423, 207, 94),  # Déplacé loin du spawn client (1920, 800)
            pygame.Rect(456, 178, 89, 124),
            pygame.Rect(2147, 934, 156, 203),
            pygame.Rect(743, 1456, 184, 87),
            pygame.Rect(1923, 512, 112, 168),
            pygame.Rect(134, 423, 97, 97),
            pygame.Rect(2314, 1289, 143, 176),
            pygame.Rect(891, 67, 203, 119),
            pygame.Rect(1756, 1343, 78, 234),
            pygame.Rect(523, 1089, 167, 92),
            pygame.Rect(2089, 134, 186, 154),
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

        # Eau — bloque les tanks (les projectiles la traversent)
        self.water_zones = [
            pygame.Rect(1200, 200, 300, 300),
            pygame.Rect(400, 1000, 400, 200),
        ]

        self.surface = pygame.Surface((self.width, self.height))
        self._generate_terrain()

    def _generate_terrain(self):
        self._draw_grass_texture()

        for zone in self.sand_zones:
            self._draw_sand_texture(zone)
        for zone in self.water_zones:
            self._draw_water_texture(zone)
        for zone in self.dirt_zones:
            self._draw_dirt_texture(zone)

        for obs in self.obstacles:
            pygame.draw.rect(self.surface, self.COLOR_ROCK, obs)
            pygame.draw.rect(self.surface, (70, 70, 70), obs, 3)  # bordure

    def _draw_grass_texture(self):
        self.surface.fill(self.COLOR_GRASS)

        # Brins d'herbe en V
        blade_dark = (24, 118, 24)
        blade_light = (56, 170, 56)
        for _ in range(4200):
            x = self.rng.randint(3, self.width - 4)
            y = self.rng.randint(3, self.height - 4)
            blade_color = blade_light if self.rng.random() < 0.35 else blade_dark
            height = self.rng.randint(2, 4)
            pygame.draw.line(self.surface, blade_color, (x, y + height), (x, y - height), 1)
            if self.rng.random() < 0.62:
                pygame.draw.line(self.surface, blade_color, (x, y), (x - 2, y + height - 1), 1)
            if self.rng.random() < 0.62:
                pygame.draw.line(self.surface, blade_color, (x, y), (x + 2, y + height - 1), 1)

    def _draw_water_texture(self, zone):
        pygame.draw.rect(self.surface, self.COLOR_WATER, zone)

        wave_light = (95, 185, 255)
        wave_shadow = (20, 120, 220)

        for y in range(zone.top + 6, zone.bottom, 12):
            x = zone.left + self.rng.randint(0, 8)
            while x < zone.right - 8:
                seg = self.rng.randint(14, 34)
                end_x = min(x + seg, zone.right - 2)

                pygame.draw.line(self.surface, wave_light, (x, y), (end_x, y), 1)
                if y + 1 < zone.bottom - 1:
                    pygame.draw.line(self.surface, wave_shadow, (x, y + 1), (end_x, y + 1), 1)

                x += seg + self.rng.randint(10, 24)

    def _draw_sand_texture(self, zone):
        pygame.draw.rect(self.surface, self.COLOR_SAND, zone)

        wave_light = (224, 208, 158)
        wave_shadow = (170, 154, 112)

        for y in range(zone.top + 6, zone.bottom, 12):
            x = zone.left + self.rng.randint(0, 8)
            while x < zone.right - 8:
                seg = self.rng.randint(14, 34)
                end_x = min(x + seg, zone.right - 2)

                amplitude = self.rng.randint(1, 2)
                phase = self.rng.uniform(0.0, math.pi * 2)
                frequency = self.rng.uniform(0.18, 0.32)

                points = []
                shadow_points = []
                for px in range(x, end_x + 1, 2):
                    offset = int(round(amplitude * math.sin((px - x) * frequency + phase)))
                    py = y + offset
                    points.append((px, py))
                    shadow_points.append((px, py + 1))

                if len(points) >= 2:
                    pygame.draw.lines(self.surface, wave_light, False, points, 1)
                if len(shadow_points) >= 2 and y + 1 < zone.bottom - 1:
                    pygame.draw.lines(self.surface, wave_shadow, False, shadow_points, 1)

                x += seg + self.rng.randint(10, 24)

    def _draw_dirt_texture(self, zone):
        pygame.draw.rect(self.surface, self.COLOR_DIRT, zone)

        # Taches de terre (plus sombres)
        for _ in range(max(70, (zone.width * zone.height) // 3500)):
            x = self.rng.randint(zone.left, zone.right - 1)
            y = self.rng.randint(zone.top, zone.bottom - 1)
            tone = self.rng.randint(-30, -8)
            color = (
                max(0, min(255, self.COLOR_DIRT[0] + tone)),
                max(0, min(255, self.COLOR_DIRT[1] + tone)),
                max(0, min(255, self.COLOR_DIRT[2] + tone)),
            )
            pygame.draw.circle(self.surface, color, (x, y), self.rng.randint(2, 5))

    # --- Accesseurs pour le système de collision ---

    def get_solid_obstacles(self):
        """Obstacles qui bloquent le déplacement des tanks (rochers + eau)."""
        return self.water_zones + self.obstacles

    def get_bouncing_obstacles(self):
        """Obstacles qui font rebondir les projectiles (rochers uniquement)."""
        return self.obstacles

    def get_destroying_obstacles(self):
        """Obstacles qui détruisent les projectiles (aucun actuellement)."""
        return []

    def get_terrain_speed_modifier(self, tank_rect):
        """Retourne le coefficient de vitesse selon le terrain sous le tank.
        
        Sable : 0.5 (50% vitesse)
        Terre : 0.7 (70% vitesse)
        Herbe : 1.0 (100% vitesse)
        """
        # Vérifier si le tank est sur du sable
        for zone in self.sand_zones:
            if tank_rect.colliderect(zone):
                return 0.5
        
        # Vérifier si le tank est sur de la terre
        for zone in self.dirt_zones:
            if tank_rect.colliderect(zone):
                return 0.7
        
        # Par défaut : herbe (vitesse normale)
        return 1.0

    def draw(self, screen, camera_x, camera_y):
        """Blit la portion visible de la map."""
        view = pygame.Rect(camera_x, camera_y, MENU_WIDTH, MENU_HEIGHT)
        view.clamp_ip(pygame.Rect(0, 0, self.width, self.height))
        screen.blit(self.surface, (0, 0), view)
