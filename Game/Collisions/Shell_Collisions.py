import pygame
import math

class ShellCollisions:
    """Gère les collisions des projectiles"""
    
    @staticmethod
    def check_all_collisions(shells, bouncing_obstacles, destroying_obstacles, tanks=None):
        """
        Vérifie les collisions de tous les projectiles
        
        Args:
            shells: Liste de Shell
            bouncing_obstacles: Liste de pygame.Rect (obstacles qui font rebondir)
            destroying_obstacles: Liste de pygame.Rect (obstacles qui détruisent)
            tanks: Liste optionnelle de Tank (pour collision tank vs projectile)
            
        Returns:
            dict: Informations sur les collisions {
                'shells_to_remove': [shell1, shell2, ...],
                'tanks_hit': [(tank, shell), ...]
            }
        """
        from Game.Collisions.Map_Collisions import MapCollisions
        
        result = {
            'shells_to_remove': [],
            'tanks_hit': []
        }
        
        for shell in shells:
            # Vérifier collision avec obstacles destructeurs (eau) - PAS DE REBOND
            destroy_collision = MapCollisions.check_shell_collision(shell, destroying_obstacles)
            if destroy_collision:
                shell.active = False
                result['shells_to_remove'].append(shell)
                continue
            
            # Vérifier collision avec obstacles rebondissants (rochers)
            bounce_collision = MapCollisions.check_shell_collision(shell, bouncing_obstacles)
            if bounce_collision:
                # Faire rebondir selon le côté touché
                side = bounce_collision['side']
                
                if side in ['left', 'right']:
                    # Rebond horizontal
                    if not shell.bounce_horizontal():
                        result['shells_to_remove'].append(shell)
                else:  # 'top' ou 'bottom'
                    # Rebond vertical
                    if not shell.bounce_vertical():
                        result['shells_to_remove'].append(shell)
                
                # Décaler légèrement le projectile pour éviter multiple rebonds
                if side == 'left':
                    shell.x = bounce_collision['obstacle'].left - shell.radius - 1
                elif side == 'right':
                    shell.x = bounce_collision['obstacle'].right + shell.radius + 1
                elif side == 'top':
                    shell.y = bounce_collision['obstacle'].top - shell.radius - 1
                elif side == 'bottom':
                    shell.y = bounce_collision['obstacle'].bottom + shell.radius + 1
                
                continue
            
            # Collision avec les tanks (si fournis)
            if tanks:
                for tank in tanks:
                    if ShellCollisions.check_shell_tank_collision(shell, tank):
                        # Ne pas toucher le propriétaire du projectile
                        if shell.owner != tank:
                            shell.active = False
                            result['shells_to_remove'].append(shell)
                            result['tanks_hit'].append((tank, shell))
                            break
        
        return result
    
    @staticmethod
    def check_shell_tank_collision(shell, tank):
        """
        Vérifie si un projectile touche un tank
        
        Args:
            shell: Instance de Shell
            tank: Instance de Tank
            
        Returns:
            bool: True si collision, False sinon
        """
        # Distance entre le centre du projectile et le centre du tank
        tank_center_x = tank.x + tank.width / 2
        tank_center_y = tank.y + tank.height / 2
        
        dx = shell.x - tank_center_x
        dy = shell.y - tank_center_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Collision si la distance est inférieure au rayon du tank + rayon du projectile
        tank_radius = max(tank.width, tank.height) / 2
        return distance < (tank_radius + shell.radius)