import pygame
from Config import MAP_WIDTH, MAP_HEIGHT

class PlayerMovement:
    """Gère le déplacement du tank joueur"""
    
    @staticmethod
    def handle_input(tank, keys, obstacles=None):
        """
        Déplace le tank selon les touches pressées
        
        Args:
            tank: Instance de Tank à déplacer
            keys: pygame.key.get_pressed()
            obstacles: Liste optionnelle d'obstacles (pygame.Rect)
            
        Returns:
            bool: True si le tank a bougé, False sinon
        """
        # Sauvegarder la position actuelle
        old_x = tank.x
        old_y = tank.y
        
        moved = False
        
        if keys[pygame.K_UP]:
            tank.y -= tank.speed
            moved = True
        if keys[pygame.K_DOWN]:
            tank.y += tank.speed
            moved = True
        if keys[pygame.K_LEFT]:
            tank.x -= tank.speed
            moved = True
        if keys[pygame.K_RIGHT]:
            tank.x += tank.speed
            moved = True

        if keys[pygame.K_z]:
            tank.y -= tank.speed
            moved = True
        if keys[pygame.K_s]:
            tank.y += tank.speed
            moved = True
        if keys[pygame.K_q]:
            tank.x -= tank.speed
            moved = True
        if keys[pygame.K_d]:
            tank.x += tank.speed
            moved = True
            
        # Limiter le tank dans les bordures de la map
        tank.x = max(0, min(tank.x, MAP_WIDTH - tank.width))
        tank.y = max(0, min(tank.y, MAP_HEIGHT - tank.height))
        
        # Vérifier les collisions avec les obstacles si fournis
        if obstacles and moved:
            from Game.Collisions.Map_Collisions import MapCollisions
            MapCollisions.resolve_tank_collision(tank, old_x, old_y, obstacles)
        
        return moved