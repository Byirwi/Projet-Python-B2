import pygame
from Config import MAP_WIDTH, MAP_HEIGHT


class PlayerMovement:
    """Déplacement du tank via clavier (flèches + ZQSD)."""

    @staticmethod
    def handle_input(tank, keys, obstacles=None):
        """Déplace le tank, le clamp aux bords, et résout les collisions."""
        old_x, old_y = tank.x, tank.y
        moved = False

        # Flèches
        if keys[pygame.K_UP]:    tank.y -= tank.speed; moved = True
        if keys[pygame.K_DOWN]:  tank.y += tank.speed; moved = True
        if keys[pygame.K_LEFT]:  tank.x -= tank.speed; moved = True
        if keys[pygame.K_RIGHT]: tank.x += tank.speed; moved = True

        # ZQSD
        if keys[pygame.K_z]: tank.y -= tank.speed; moved = True
        if keys[pygame.K_s]: tank.y += tank.speed; moved = True
        if keys[pygame.K_q]: tank.x -= tank.speed; moved = True
        if keys[pygame.K_d]: tank.x += tank.speed; moved = True

        # Clamp aux limites de la map
        tank.x = max(0, min(tank.x, MAP_WIDTH - tank.width))
        tank.y = max(0, min(tank.y, MAP_HEIGHT - tank.height))

        # Collision avec les obstacles → annuler le déplacement
        if obstacles and moved:
            from Game.Collisions.Map_Collisions import MapCollisions
            MapCollisions.resolve_tank_collision(tank, old_x, old_y, obstacles)

        return moved