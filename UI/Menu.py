# ui/menu.py
import pygame
import sys


class MainMenu:

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 72)
        self.font_menu = pygame.font.Font(None, 48)
        self.options = ["SOLO", "MULTIJOUEUR", "SCORES", "QUITTER"]
        self.selected = 0
        self.option_rects = []

        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (255, 200, 0)
        self.COLOR_SELECTED = (255, 255, 255)
        self.COLOR_NORMAL = (100, 100, 100)
        self.COLOR_ACCENT = (255, 200, 0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected]
                elif event.key == pygame.K_ESCAPE:
                    return "QUITTER"

            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected = i

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        return self.options[i]
        return None

    def draw(self):
        self.screen.fill(self.COLOR_BG)

        title = self.font_title.render("TANK BATTLE", True, self.COLOR_TITLE)
        self.screen.blit(title, title.get_rect(center=(512, 150)))

        self.option_rects = []
        for i, option in enumerate(self.options):
            color = self.COLOR_SELECTED if i == self.selected else self.COLOR_NORMAL
            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(512, 300 + i * 80))
            self.option_rects.append(text_rect.inflate(80, 20))
            self.screen.blit(text, text_rect)

            if i == self.selected:
                pygame.draw.polygon(self.screen, self.COLOR_ACCENT, [
                    (text_rect.right + 40, text_rect.centery),
                    (text_rect.right + 20, text_rect.centery - 15),
                    (text_rect.right + 20, text_rect.centery + 15)])

        instr = pygame.font.Font(None, 28).render(
            "↑↓ / Souris: Naviguer  |  ENTER / Clic: Valider  |  ESC: Quitter",
            True, (80, 80, 80))
        self.screen.blit(instr, instr.get_rect(center=(512, 730)))

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(60)
            choice = self.handle_events()
            if choice == "QUIT":
                pygame.quit(); sys.exit()
            elif choice:
                return choice
            self.draw()

