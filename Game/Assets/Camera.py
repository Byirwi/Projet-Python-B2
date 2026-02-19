from Config import MAP_WIDTH, MAP_HEIGHT


class Camera:
    """Caméra qui suit le joueur, clampée aux bords de la map."""

    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height

    def follow(self, target):
        # Centrer sur la cible
        self.x = target.x - self.width // 2 + target.width // 2
        self.y = target.y - self.height // 2 + target.height // 2
        # Clamp aux limites
        self.x = max(0, min(self.x, MAP_WIDTH - self.width))
        self.y = max(0, min(self.y, MAP_HEIGHT - self.height))