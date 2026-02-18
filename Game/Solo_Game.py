import pygame
import sys
from Game.Assets.Map import GameMap
from Game.Assets.Tank import Tank
from Game.Assets.Camera import Camera
from Game.Movement.Player_Movement import PlayerMovement
from Game.Movement.Shell_Movement import ShellMovement
from Game.Collisions.Shell_Collisions import ShellCollisions
from Config import MENU_WIDTH, MENU_HEIGHT, FPS, MAP_WIDTH, MAP_HEIGHT


class SoloGame:
    """Gestionnaire du mode de jeu Solo"""
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Map
        self.game_map = GameMap()
        
        # Tank du joueur (commence au centre)
        self.player = Tank(MAP_WIDTH // 2, MAP_HEIGHT // 2, (0, 255, 0))
        
        # Caméra
        self.camera = Camera(MENU_WIDTH, MENU_HEIGHT)
        
        # Projectiles
        self.shells = []
        
        # Police pour les infos
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
    def handle_events(self):
        """Gestion des événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.KEYDOWN:
                # ESC pour retourner au menu
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
            
            # Tir avec clic gauche
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    shell = self.player.fire()
                    if shell:  # Si le tir est autorisé (cooldown)
                        self.shells.append(shell)
                    
        return None
    
    def update(self):
        """Mise à jour de la logique du jeu"""
        keys = pygame.key.get_pressed()
        
        # Déplacer le joueur avec gestion des collisions (tous les obstacles solides)
        solid_obstacles = self.game_map.get_solid_obstacles()
        PlayerMovement.handle_input(self.player, keys, solid_obstacles)
        
        # Mettre à jour le tank (cooldown, etc.)
        self.player.update()
        
        # Faire viser le tank vers la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.player.aim_at_mouse(mouse_x, mouse_y, self.camera.x, self.camera.y)
        
        # Mettre à jour les projectiles
        self.shells = ShellMovement.update_shells(self.shells)
        
        # Vérifier les collisions des projectiles
        # Seulement les rochers font rebondir, l'eau n'arrête pas les projectiles
        bouncing_obstacles = self.game_map.get_bouncing_obstacles()
        destroying_obstacles = []  # Liste vide - rien ne détruit les projectiles
        
        collision_result = ShellCollisions.check_all_collisions(
            self.shells, 
            bouncing_obstacles,
            destroying_obstacles
        )
        
        # Traiter les collisions
        if collision_result['tanks_hit']:
            for tank, shell in collision_result['tanks_hit']:
                print(f"Tank touché à ({int(tank.x)}, {int(tank.y)}) !")
        
        # Faire suivre la caméra
        self.camera.follow(self.player)
    
    def draw(self):
        """Affichage du jeu"""
        # Dessiner la map avec la caméra
        self.game_map.draw(self.screen, self.camera.x, self.camera.y)
        
        # Dessiner les projectiles
        for shell in self.shells:
            shell.draw(self.screen, self.camera.x, self.camera.y)
        
        # Dessiner le tank
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        
        # HUD - Informations en haut
        info_text = self.font_small.render(
            f"Position: ({int(self.player.x)}, {int(self.player.y)}) | "
            f"Angle: {int(self.player.angle)}° | "
            f"Projectiles: {len(self.shells)}", 
            True, (255, 255, 255)
        )
        self.screen.blit(info_text, (10, 10))
        
        # Indicateur de cooldown
        if self.player.fire_cooldown > 0:
            cooldown_text = self.font_small.render(
                f"Rechargement...", 
                True, (255, 100, 100)
            )
            self.screen.blit(cooldown_text, (10, 40))
        
        # Instructions en bas
        controls_text = self.font_small.render(
            "Flèches: Déplacer | Souris: Viser | Clic: Tirer | ESC: Menu", 
            True, (255, 255, 255)
        )
        self.screen.blit(controls_text, (10, MENU_HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        """Boucle principale du jeu"""
        running = True
        while running:
            self.clock.tick(FPS)
            
            # Événements
            result = self.handle_events()
            if result == "QUIT":
                pygame.quit()
                sys.exit()
            elif result == "MENU":
                return "MENU"
            
            # Mise à jour
            self.update()
            
            # Affichage
            self.draw()
        
        return None