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
            destroying_obstacles,
            [self.player]  # Le joueur peut être touché par ses propres rebonds
        )
        
        # Traiter les collisions (friendly fire / rebonds)
        if collision_result['tanks_hit']:
            for tank, shell in collision_result['tanks_hit']:
                tank.take_damage(25)
                print(f"Tank touché ! HP restants: {tank.health}")

        # Supprimer les projectiles inactifs
        if collision_result['shells_to_remove']:
            self.shells = [shell for shell in self.shells if shell.active]

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
        health_text = self.font.render(
            f"PV: {self.player.health}",
            True,
            (0, 255, 0) if self.player.health > 30 else (255, 80, 80)
        )
        self.screen.blit(health_text, (10, 10))

        info_text = self.font_small.render(
            f"Position: ({int(self.player.x)}, {int(self.player.y)}) | "
            f"Angle: {int(self.player.angle)}° | "
            f"Projectiles: {len(self.shells)}", 
            True, (255, 255, 255)
        )
        self.screen.blit(info_text, (10, 48))
        
        # Affichage des points de vie
        hp_text = self.font.render(f"HP: {self.player.health}", True, (255, 255, 255))
        self.screen.blit(hp_text, (10, 35))

        # Barre de vie
        bar_x, bar_y = 10, 65
        bar_width, bar_height = 200, 20
        hp_ratio = max(0.0, self.player.health / 100.0)

        # Fond de la barre (rouge)
        pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Barre de vie (vert -> jaune -> rouge selon les HP)
        if hp_ratio > 0.5:
            bar_color = (0, 255, 0)
        elif hp_ratio > 0.25:
            bar_color = (255, 200, 0)
        else:
            bar_color = (255, 0, 0)
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        # Bordure de la barre
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Indicateur de cooldown
        if self.player.fire_cooldown > 0:
            cooldown_text = self.font_small.render(
                f"Rechargement...", 
                True, (255, 100, 100)
            )
            self.screen.blit(cooldown_text, (10, 92))

        # Instructions en bas
        controls_text = self.font_small.render(
            "Flèches: Déplacer | Souris: Viser | Clic: Tirer | ESC: Menu", 
            True, (255, 255, 255)
        )
        self.screen.blit(controls_text, (10, MENU_HEIGHT - 30))
        
        pygame.display.flip()

    def show_game_over_screen(self, duration_ms=2500):
        """Affiche un écran de défaite temporaire"""
        start_time = pygame.time.get_ticks()
        title_font = pygame.font.Font(None, 96)
        subtitle_font = pygame.font.Font(None, 36)

        while pygame.time.get_ticks() - start_time < duration_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((15, 15, 20))

            game_over_text = title_font.render("GAME OVER", True, (255, 60, 60))
            game_over_rect = game_over_text.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 - 20))
            self.screen.blit(game_over_text, game_over_rect)

            info_text = subtitle_font.render("Retour au menu...", True, (220, 220, 220))
            info_rect = info_text.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + 40))
            self.screen.blit(info_text, info_rect)

            pygame.display.flip()
            self.clock.tick(FPS)
    
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

            # Défaite si PV à 0
            if self.player.health <= 0:
                self.show_game_over_screen(2500)
                return "LOSE"
            
            # Vérifier si le joueur est mort
            if self.player.health <= 0:
                self._show_game_over()
                return "MENU"

            # Affichage
            self.draw()
        
        return None

    def _show_game_over(self):
        """Affiche l'écran de Game Over pendant quelques secondes"""
        font_big = pygame.font.Font(None, 72)
        font_info = pygame.font.Font(None, 36)

        start_time = pygame.time.get_ticks()
        duration = 3000  # 3 secondes

        while pygame.time.get_ticks() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    return  # Appuyer sur une touche pour skip

            # Fond semi-transparent
            overlay = pygame.Surface((MENU_WIDTH, MENU_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))

            # Texte GAME OVER
            game_over_text = font_big.render("GAME OVER", True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 - 30))
            self.screen.blit(game_over_text, game_over_rect)

            # Texte info
            info_text = font_info.render("Vous avez été touché par votre propre projectile !", True, (255, 200, 100))
            info_rect = info_text.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + 30))
            self.screen.blit(info_text, info_rect)

            # Retour menu
            return_text = font_info.render("Retour au menu...", True, (200, 200, 200))
            return_rect = return_text.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + 80))
            self.screen.blit(return_text, return_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

