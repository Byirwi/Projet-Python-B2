import pygame

class MapCollisions:
    """Gère les collisions entre les entités et la map"""
    
    @staticmethod
    def check_tank_collision(tank, obstacles):
        """
        Vérifie si un tank entre en collision avec des obstacles
        
        Args:
            tank: Instance de Tank
            obstacles: Liste de pygame.Rect (obstacles de la map)
            
        Returns:
            pygame.Rect ou None: L'obstacle en collision, ou None
        """
        tank_rect = pygame.Rect(tank.x, tank.y, tank.width, tank.height)
        
        for obstacle in obstacles:
            if tank_rect.colliderect(obstacle):
                return obstacle
        
        return None
    
    @staticmethod
    def check_shell_collision(shell, obstacles):
        """
        Vérifie si un projectile entre en collision avec des obstacles
        
        Args:
            shell: Instance de Shell
            obstacles: Liste de pygame.Rect (obstacles de la map)
            
        Returns:
            dict ou None: {'obstacle': pygame.Rect, 'side': 'top'|'bottom'|'left'|'right'} ou None
        """
        # Créer un petit rect autour du projectile
        shell_rect = pygame.Rect(
            shell.x - shell.radius,
            shell.y - shell.radius,
            shell.radius * 2,
            shell.radius * 2
        )
        
        for obstacle in obstacles:
            if shell_rect.colliderect(obstacle):
                # Déterminer quel côté de l'obstacle a été touché
                side = MapCollisions._get_collision_side(shell, obstacle)
                return {'obstacle': obstacle, 'side': side}
        
        return None
    
    @staticmethod
    def _get_collision_side(shell, obstacle):
        """
        Détermine de quel côté l'obstacle a été touché
        
        Returns:
            str: 'top', 'bottom', 'left' ou 'right'
        """
        # Centre de l'obstacle
        obstacle_center_x = obstacle.centerx
        obstacle_center_y = obstacle.centery
        
        # Direction du projectile par rapport au centre de l'obstacle
        dx = shell.x - obstacle_center_x
        dy = shell.y - obstacle_center_y
        
        # Calculer les distances aux bords
        left_dist = abs(shell.x - obstacle.left)
        right_dist = abs(shell.x - obstacle.right)
        top_dist = abs(shell.y - obstacle.top)
        bottom_dist = abs(shell.y - obstacle.bottom)
        
        # Trouver la plus petite distance
        min_dist = min(left_dist, right_dist, top_dist, bottom_dist)
        
        if min_dist == left_dist:
            return 'left'
        elif min_dist == right_dist:
            return 'right'
        elif min_dist == top_dist:
            return 'top'
        else:
            return 'bottom'
    
    @staticmethod
    def resolve_tank_collision(tank, old_x, old_y, obstacles):
        """
        Résout une collision en repoussant le tank à sa position précédente
        
        Args:
            tank: Instance de Tank
            old_x, old_y: Position précédente du tank
            obstacles: Liste de pygame.Rect (obstacles de la map)
        """
        collision = MapCollisions.check_tank_collision(tank, obstacles)
        
        if collision:
            # Remettre le tank à sa position précédente
            tank.x = old_x
            tank.y = old_y