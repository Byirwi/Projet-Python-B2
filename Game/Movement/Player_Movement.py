import pygame
import math
from Config import MAP_WIDTH, MAP_HEIGHT


class PlayerMovement:
    """Déplacement du tank via clavier (flèches + ZQSD)."""

    @staticmethod
    def handle_input(tank, keys, obstacles=None, game_map=None):
        """Déplace le tank, oriente le châssis selon la direction, applique ralentissement terrain, clamp aux bords, et résout les collisions."""
        old_x, old_y = tank.x, tank.y
        dx, dy = 0, 0

        # Flèches + ZQSD
        if keys[pygame.K_UP] or keys[pygame.K_z]:    dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  dy += 1
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:  dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1

        moved = (dx != 0 or dy != 0)

        if moved:
            # Orienter le châssis vers la direction du mouvement
            angle_rad = math.atan2(dy, dx)
            tank.hull_angle = math.degrees(angle_rad) + 90

            # Normaliser le vecteur de déplacement pour mouvement diagonal uniforme
            length = math.sqrt(dx*dx + dy*dy)
            dx = (dx / length) * tank.speed
            dy = (dy / length) * tank.speed

            # Appliquer le modificateur de vitesse selon le terrain
            if game_map:
                tank_rect = pygame.Rect(tank.x, tank.y, tank.width, tank.height)
                speed_modifier = game_map.get_terrain_speed_modifier(tank_rect)
                dx *= speed_modifier
                dy *= speed_modifier

            tank.x += dx
            tank.y += dy

        # Clamp aux limites de la map
        tank.x = max(0, min(tank.x, MAP_WIDTH - tank.width))
        tank.y = max(0, min(tank.y, MAP_HEIGHT - tank.height))

        # Collision avec les obstacles → annuler le déplacement
        if obstacles and moved:
            from Game.Collisions.Map_Collisions import MapCollisions
            MapCollisions.resolve_tank_collision(tank, old_x, old_y, obstacles)

        return moved