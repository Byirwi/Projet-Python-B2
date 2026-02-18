import pygame

class TankCollisions:
    """Gère les collisions entre tanks"""
    
    @staticmethod
    def check_tank_vs_tank(tank1, tank2):
        """
        Vérifie si deux tanks se chevauchent
        
        Args:
            tank1, tank2: Instances de Tank
            
        Returns:
            bool: True si collision, False sinon
        """
        rect1 = pygame.Rect(tank1.x, tank1.y, tank1.width, tank1.height)
        rect2 = pygame.Rect(tank2.x, tank2.y, tank2.width, tank2.height)
        
        return rect1.colliderect(rect2)
    
    @staticmethod
    def resolve_tank_vs_tank(tank1, tank2, old_x1, old_y1):
        """
        Résout une collision entre deux tanks
        
        Args:
            tank1: Tank qui s'est déplacé
            tank2: Tank statique/autre tank
            old_x1, old_y1: Position précédente de tank1
        """
        if TankCollisions.check_tank_vs_tank(tank1, tank2):
            # Remettre tank1 à sa position précédente
            tank1.x = old_x1
            tank1.y = old_y1