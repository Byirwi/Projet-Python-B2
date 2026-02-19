import math


class ShellCollisions:
    """Gestion des collisions projectile ↔ obstacles / tanks."""

    @staticmethod
    def check_all_collisions(shells, bouncing_obstacles, destroying_obstacles, tanks=None):
        """Teste toutes les collisions pour une liste de projectiles.

        Retourne {'shells_to_remove': [...], 'tanks_hit': [(tank, shell), ...]}.
        """
        from Game.Collisions.Map_Collisions import MapCollisions

        result = {'shells_to_remove': [], 'tanks_hit': []}

        for shell in shells:
            # Eau → destruction immédiate
            if MapCollisions.check_shell_collision(shell, destroying_obstacles):
                shell.active = False
                result['shells_to_remove'].append(shell)
                continue

            # Rochers → rebond
            bounce = MapCollisions.check_shell_collision(shell, bouncing_obstacles)
            if bounce:
                side = bounce['side']
                ok = shell.bounce_horizontal() if side in ('left', 'right') else shell.bounce_vertical()
                if not ok:
                    result['shells_to_remove'].append(shell)

                # Décaler pour éviter le double-rebond
                obs = bounce['obstacle']
                if side == 'left':
                    shell.x = obs.left - shell.radius - 1
                elif side == 'right':
                    shell.x = obs.right + shell.radius + 1
                elif side == 'top':
                    shell.y = obs.top - shell.radius - 1
                elif side == 'bottom':
                    shell.y = obs.bottom + shell.radius + 1
                continue

            # Tanks → dégâts (friendly fire seulement après ≥1 rebond)
            if tanks:
                for tank in tanks:
                    if ShellCollisions._shell_hits_tank(shell, tank):
                        if shell.owner == tank and shell.bounces == 0:
                            continue
                        shell.active = False
                        result['shells_to_remove'].append(shell)
                        result['tanks_hit'].append((tank, shell))
                        break

        return result

    @staticmethod
    def _shell_hits_tank(shell, tank):
        """Collision cercle (shell) vs cercle englobant (tank)."""
        tcx = tank.x + tank.width / 2
        tcy = tank.y + tank.height / 2
        dist = math.hypot(shell.x - tcx, shell.y - tcy)
        tank_radius = max(tank.width, tank.height) / 2
        return dist < (tank_radius + shell.radius)
