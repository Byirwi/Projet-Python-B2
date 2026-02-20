import pygame


class MapCollisions:
    """Collisions entre entités et obstacles de la map."""

    @staticmethod
    def check_tank_collision(tank, obstacles):
        """Retourne le premier obstacle en collision avec le tank, ou None."""
        tank_rect = pygame.Rect(tank.x, tank.y, tank.width, tank.height)
        for obs in obstacles:
            if tank_rect.colliderect(obs):
                return obs
        return None

    @staticmethod
    def check_shell_collision(shell, obstacles):
        """Retourne {'obstacle': Rect, 'side': str} si le shell touche un obstacle."""
        shell_rect = pygame.Rect(
            shell.x - shell.radius, shell.y - shell.radius,
            shell.radius * 2, shell.radius * 2
        )
        for obs in obstacles:
            if shell_rect.colliderect(obs):
                side = MapCollisions._get_collision_side(shell, obs)
                return {'obstacle': obs, 'side': side}
        return None

    @staticmethod
    def _get_collision_side(shell, obstacle):
        """Détermine le côté touché en comparant les distances aux 4 bords."""
        distances = {
            'left':   abs(shell.x - obstacle.left),
            'right':  abs(shell.x - obstacle.right),
            'top':    abs(shell.y - obstacle.top),
            'bottom': abs(shell.y - obstacle.bottom),
        }
        return min(distances, key=distances.get)

    @staticmethod
    def resolve_tank_collision(tank, old_x, old_y, obstacles):
        """Repousse le tank à sa position précédente si collision détectée."""
        if MapCollisions.check_tank_collision(tank, obstacles):
            tank.x = old_x
            tank.y = old_y