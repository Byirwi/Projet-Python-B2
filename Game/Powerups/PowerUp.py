import pygame


# Compteur global pour les IDs uniques
_powerup_counter = 0


class PowerUp:
    def __init__(self, power_type, x, y, powerup_id=None):
        global _powerup_counter
        
        self.power_type = power_type
        self.x = x
        self.y = y
        self.size = 18
        self.rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
        
        # ID unique pour synchronisation réseau
        if powerup_id is None:
            self.powerup_id = _powerup_counter
            _powerup_counter += 1
        else:
            self.powerup_id = powerup_id
            _powerup_counter = max(_powerup_counter, powerup_id + 1)

    def draw(self, screen, camera_x, camera_y):
        sx = self.rect.x - camera_x
        sy = self.rect.y - camera_y
        draw_rect = pygame.Rect(sx, sy, self.rect.width, self.rect.height)

        if self.power_type == "heal":
            pygame.draw.rect(screen, (60, 200, 80), draw_rect, border_radius=4)
            pygame.draw.rect(screen, (255, 255, 255), draw_rect, 2, border_radius=4)
            cx, cy = draw_rect.center
            pygame.draw.line(screen, (255, 255, 255), (cx - 4, cy), (cx + 4, cy), 2)
            pygame.draw.line(screen, (255, 255, 255), (cx, cy - 4), (cx, cy + 4), 2)
        else:  # speed
            pygame.draw.rect(screen, (70, 170, 255), draw_rect, border_radius=4)
            pygame.draw.rect(screen, (255, 255, 255), draw_rect, 2, border_radius=4)
            cx, cy = draw_rect.center
            points = [(cx - 3, cy - 5), (cx + 1, cy - 1), (cx - 1, cy - 1), (cx + 3, cy + 5), (cx - 1, cy + 1), (cx + 1, cy + 1)]
            pygame.draw.polygon(screen, (255, 255, 255), points)
