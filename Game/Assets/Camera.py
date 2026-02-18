from Config import MAP_WIDTH, MAP_HEIGHT

class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        
    def follow(self, target):
        """Fait suivre la caméra au tank"""
        # Centrer la caméra sur le tank
        self.x = target.x - self.width // 2 + target.width // 2
        self.y = target.y - self.height // 2 + target.height // 2
        
        # Limiter la caméra aux bordures de la map
        self.x = max(0, min(self.x, MAP_WIDTH - self.width))
        self.y = max(0, min(self.y, MAP_HEIGHT - self.height))