# Main.py
import pygame
import sys
from UI.Menu import MainMenu
from UI.Multiplayer_Menu import MultiplayerMenu
from UI.Host_Screen import HostScreen
from UI.Join_Screen import JoinScreen
from UI.Scoreboard import Scoreboard
from UI.Name_Input import NameInput
from Game.Solo_Game import SoloGame
from Game.Multi_Game import MultiGame
from Game.Network import NetworkClient
from Score_Manager import add_score


def main():
    # Initialisation de Pygame et création de la fenêtre
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Tank Battle")

    running = True
    while running:
        # Affichage du menu principal
        menu = MainMenu(screen)
        choice = menu.run()

        if choice == "SOLO":
            # Lancement du mode solo
            solo_game = SoloGame(screen)
            result = solo_game.run()

            # Proposer la sauvegarde du score si le joueur est mort
            if result == "MENU" and solo_game.player.health <= 0:
                name = NameInput(screen, won=False, mode="solo").run()
                if name:
                    add_score(name, False)

        elif choice == "MULTIJOUEUR":
            # Affichage du menu multijoueur
            multi_choice = MultiplayerMenu(screen).run()

            if multi_choice == "HÉBERGER":
                # Lancement d'une partie en tant qu'hôte
                result = HostScreen(screen).run()
                if isinstance(result, tuple) and result[0] == "START_GAME":
                    server = result[1]
                    game_result = MultiGame(screen, server, is_host=True).run()
                    # Fallback si le jeu renvoie WIN/LOSE (ESC pendant la partie)
                    if game_result in ("WIN", "LOSE"):
                        name = NameInput(screen, game_result == "WIN", mode="multi").run()
                        if name:
                            add_score(name, game_result == "WIN")

            elif multi_choice == "REJOINDRE":
                # Connexion à une partie existante
                result = JoinScreen(screen).run()
                if isinstance(result, tuple) and result[0] == "CONNECT":
                    ip = result[1] or "127.0.0.1"
                    port = int(result[2]) if result[2].isdigit() else 5555
                    client = NetworkClient(ip, port)
                    if client.connect():
                        game_result = MultiGame(screen, client, is_host=False).run()
                        if game_result in ("WIN", "LOSE"):
                            name = NameInput(screen, game_result == "WIN", mode="multi").run()
                            if name:
                                add_score(name, game_result == "WIN")

        elif choice == "SCORES":
            # Affichage du tableau des scores
            Scoreboard(screen).run()

        elif choice == "QUITTER":
            # Quitter le jeu
            running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()