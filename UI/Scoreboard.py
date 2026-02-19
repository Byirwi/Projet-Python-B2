# UI/Scoreboard.py
"""Écran du leaderboard / tableau des scores"""

import pygame
import sys
from Score_Manager import get_leaderboard, clear_scores
from Config import MENU_WIDTH, MENU_HEIGHT


class Scoreboard:
    """Affiche le leaderboard avec les meilleurs joueurs"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Polices
        self.font_title = pygame.font.Font(None, 64)
        self.font_header = pygame.font.Font(None, 36)
        self.font_row = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_button = pygame.font.Font(None, 30)

        # Couleurs
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_TITLE = (255, 200, 0)
        self.COLOR_HEADER = (100, 200, 255)
        self.COLOR_GOLD = (255, 215, 0)
        self.COLOR_SILVER = (192, 192, 192)
        self.COLOR_BRONZE = (205, 127, 50)
        self.COLOR_TEXT = (200, 200, 200)
        self.COLOR_LINE = (60, 60, 80)
        self.COLOR_BTN = (150, 40, 40)
        self.COLOR_BTN_HOVER = (200, 60, 60)

        # Données
        self.scores = get_leaderboard()
        self.scroll_offset = 0
        self.max_visible = 10

        # Boutons
        self.clear_btn_rect = pygame.Rect(MENU_WIDTH // 2 - 130, MENU_HEIGHT - 100, 260, 40)
        self.back_btn_rect = pygame.Rect(20, MENU_HEIGHT - 50, 150, 35)
        self.clear_btn_hover = False
        self.back_btn_hover = False

        # Confirmation
        self.confirm_active = False
        self.confirm_selected = 1  # 0 = Oui, 1 = Non (défaut sur Non)
        self.confirm_btn_oui = pygame.Rect(MENU_WIDTH // 2 - 130, MENU_HEIGHT // 2 + 20, 110, 45)
        self.confirm_btn_non = pygame.Rect(MENU_WIDTH // 2 + 20, MENU_HEIGHT // 2 + 20, 110, 45)

    def handle_events(self):
        """Gestion des événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            # === Mode confirmation ===
            if self.confirm_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        self.confirm_selected = 1 - self.confirm_selected
                    if event.key == pygame.K_RETURN:
                        if self.confirm_selected == 0:  # Oui
                            clear_scores()
                            self.scores = []
                        self.confirm_active = False
                    if event.key == pygame.K_ESCAPE:
                        self.confirm_active = False

                if event.type == pygame.MOUSEMOTION:
                    if self.confirm_btn_oui.collidepoint(event.pos):
                        self.confirm_selected = 0
                    elif self.confirm_btn_non.collidepoint(event.pos):
                        self.confirm_selected = 1

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.confirm_btn_oui.collidepoint(event.pos):
                        clear_scores()
                        self.scores = []
                        self.confirm_active = False
                    elif self.confirm_btn_non.collidepoint(event.pos):
                        self.confirm_active = False

                continue  # Ne pas traiter les autres événements en mode confirmation

            # === Mode normal ===
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    return "MENU"
                if event.key == pygame.K_UP:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                if event.key == pygame.K_DOWN:
                    self.scroll_offset = min(
                        max(0, len(self.scores) - self.max_visible),
                        self.scroll_offset + 1
                    )
                if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    if self.scores:
                        self.confirm_active = True
                        self.confirm_selected = 1

            # Molette souris pour scroller
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y
                self.scroll_offset = max(0, min(
                    max(0, len(self.scores) - self.max_visible),
                    self.scroll_offset
                ))

            # Survol souris
            if event.type == pygame.MOUSEMOTION:
                self.clear_btn_hover = self.clear_btn_rect.collidepoint(event.pos)
                self.back_btn_hover = self.back_btn_rect.collidepoint(event.pos)

            # Clic souris
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.clear_btn_rect.collidepoint(event.pos) and self.scores:
                    self.confirm_active = True
                    self.confirm_selected = 1
                if self.back_btn_rect.collidepoint(event.pos):
                    return "MENU"

        return None

    def _draw_confirm_dialog(self):
        """Dessine la boîte de dialogue de confirmation"""
        # Overlay sombre
        overlay = pygame.Surface((MENU_WIDTH, MENU_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Boîte de dialogue
        dialog_rect = pygame.Rect(MENU_WIDTH // 2 - 200, MENU_HEIGHT // 2 - 60, 400, 150)
        pygame.draw.rect(self.screen, (30, 30, 45), dialog_rect)
        pygame.draw.rect(self.screen, (255, 80, 80), dialog_rect, 3)

        # Texte
        text = self.font_header.render("Supprimer tous les scores ?", True, (255, 255, 255))
        text_rect = text.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 - 25))
        self.screen.blit(text, text_rect)

        # Bouton OUI
        oui_color = (200, 60, 60) if self.confirm_selected == 0 else (80, 30, 30)
        pygame.draw.rect(self.screen, oui_color, self.confirm_btn_oui)
        pygame.draw.rect(self.screen, (255, 255, 255) if self.confirm_selected == 0 else (100, 100, 100),
                         self.confirm_btn_oui, 2)
        oui_text = self.font_button.render("OUI", True, (255, 255, 255))
        oui_text_rect = oui_text.get_rect(center=self.confirm_btn_oui.center)
        self.screen.blit(oui_text, oui_text_rect)

        # Bouton NON
        non_color = (40, 100, 40) if self.confirm_selected == 1 else (30, 50, 30)
        pygame.draw.rect(self.screen, non_color, self.confirm_btn_non)
        pygame.draw.rect(self.screen, (255, 255, 255) if self.confirm_selected == 1 else (100, 100, 100),
                         self.confirm_btn_non, 2)
        non_text = self.font_button.render("NON", True, (255, 255, 255))
        non_text_rect = non_text.get_rect(center=self.confirm_btn_non.center)
        self.screen.blit(non_text, non_text_rect)

    def draw(self):
        """Affichage du scoreboard"""
        self.screen.fill(self.COLOR_BG)

        # Titre
        title = self.font_title.render("LEADERBOARD", True, self.COLOR_TITLE)
        title_rect = title.get_rect(center=(MENU_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        # Ligne de séparation
        pygame.draw.line(self.screen, self.COLOR_TITLE, (150, 100), (MENU_WIDTH - 150, 100), 2)

        # En-têtes
        y_start = 130
        headers = ["#", "JOUEUR", "VICTOIRES", "DÉFAITES", "PARTIES"]
        col_x = [80, 200, 450, 620, 780]

        for i, header in enumerate(headers):
            text = self.font_header.render(header, True, self.COLOR_HEADER)
            text_rect = text.get_rect(center=(col_x[i], y_start))
            self.screen.blit(text, text_rect)

        pygame.draw.line(self.screen, self.COLOR_LINE, (50, y_start + 25), (MENU_WIDTH - 50, y_start + 25), 1)

        # Lignes du leaderboard
        if not self.scores:
            no_score = self.font_row.render("Aucun score enregistré", True, (100, 100, 100))
            no_rect = no_score.get_rect(center=(MENU_WIDTH // 2, 300))
            self.screen.blit(no_score, no_rect)
        else:
            visible_scores = self.scores[self.scroll_offset:self.scroll_offset + self.max_visible]
            for idx, entry in enumerate(visible_scores):
                rank = self.scroll_offset + idx + 1
                row_y = y_start + 55 + idx * 45

                if rank == 1:
                    row_color = self.COLOR_GOLD
                elif rank == 2:
                    row_color = self.COLOR_SILVER
                elif rank == 3:
                    row_color = self.COLOR_BRONZE
                else:
                    row_color = self.COLOR_TEXT

                # Fond alterné
                if idx % 2 == 0:
                    bg_rect = pygame.Rect(50, row_y - 15, MENU_WIDTH - 100, 40)
                    pygame.draw.rect(self.screen, (30, 30, 45), bg_rect)

                # Données
                rank_text = self.font_row.render(str(rank), True, row_color)
                name_text = self.font_row.render(entry["name"][:15], True, row_color)
                wins_text = self.font_row.render(str(entry["wins"]), True, (0, 255, 0))
                losses_text = self.font_row.render(str(entry["losses"]), True, (255, 80, 80))
                games_text = self.font_row.render(str(entry["games"]), True, row_color)

                for text, x in [(rank_text, col_x[0]), (name_text, col_x[1]),
                                (wins_text, col_x[2]), (losses_text, col_x[3]),
                                (games_text, col_x[4])]:
                    rect = text.get_rect(center=(x, row_y))
                    self.screen.blit(text, rect)

        # Indicateur de scroll
        if len(self.scores) > self.max_visible:
            scroll_info = self.font_small.render(
                f"↑↓ / Molette pour défiler ({self.scroll_offset + 1}-"
                f"{min(self.scroll_offset + self.max_visible, len(self.scores))}"
                f" / {len(self.scores)})",
                True, (100, 100, 100)
            )
            scroll_rect = scroll_info.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT - 130))
            self.screen.blit(scroll_info, scroll_rect)

        # === Bouton SUPPRIMER ===
        btn_color = self.COLOR_BTN_HOVER if self.clear_btn_hover else self.COLOR_BTN
        if not self.scores:
            btn_color = (60, 30, 30)  # Grisé si pas de scores
        pygame.draw.rect(self.screen, btn_color, self.clear_btn_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 80, 80), self.clear_btn_rect, 2, border_radius=6)
        clear_text = self.font_button.render("SUPPRIMER LES SCORES", True, (255, 255, 255))
        clear_text_rect = clear_text.get_rect(center=self.clear_btn_rect.center)
        self.screen.blit(clear_text, clear_text_rect)

        # === Bouton RETOUR ===
        back_color = (60, 60, 80) if self.back_btn_hover else (40, 40, 55)
        pygame.draw.rect(self.screen, back_color, self.back_btn_rect, border_radius=6)
        pygame.draw.rect(self.screen, (150, 150, 150), self.back_btn_rect, 2, border_radius=6)
        back_text = self.font_button.render("← RETOUR", True, (200, 200, 200))
        back_text_rect = back_text.get_rect(center=self.back_btn_rect.center)
        self.screen.blit(back_text, back_text_rect)

        # Instructions
        instr = self.font_small.render("ESC: Retour  |  DEL: Supprimer", True, (80, 80, 80))
        instr_rect = instr.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT - 15))
        self.screen.blit(instr, instr_rect)

        # Dialogue de confirmation (par dessus tout)
        if self.confirm_active:
            self._draw_confirm_dialog()

        pygame.display.flip()

    def run(self):
        """Boucle principale"""
        while True:
            self.clock.tick(60)
            result = self.handle_events()

            if result == "QUIT":
                pygame.quit()
                sys.exit()
            elif result == "MENU":
                return "MENU"

            self.draw()


