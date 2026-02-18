class ShellMovement:
    """Gère le mouvement des projectiles"""
    
    @staticmethod
    def update_shells(shells):
        """
        Met à jour tous les projectiles et retire les inactifs
        
        Args:
            shells: Liste de Shell
            
        Returns:
            Liste de Shell actifs
        """
        # Mettre à jour chaque projectile
        for shell in shells:
            shell.update()
        
        # Retirer les projectiles inactifs
        return [shell for shell in shells if shell.active]