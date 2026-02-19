class ShellMovement:
    """Met à jour et nettoie la liste de projectiles."""

    @staticmethod
    def update_shells(shells):
        """Tick tous les shells, retourne uniquement les actifs."""
        for shell in shells:
            shell.update()
        return [s for s in shells if s.active]
