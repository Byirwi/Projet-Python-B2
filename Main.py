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
    # Initialisation
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Tank Battle")

    # Boucle principale
    running = True
    while running:
        # Afficher le menu principal
        menu = MainMenu(screen)
        choice = menu.run()

        # Traiter le choix
        if choice == "SOLO":
            print("→ Lancement du mode SOLO...")
            solo_game = SoloGame(screen)
            result = solo_game.run()

            if result == "MENU":
                # Le joueur est mort ou a appuyé ESC
                # Si le joueur est mort, proposer de sauvegarder
                if solo_game.player.health <= 0:
                    name_screen = NameInput(screen, won=False, mode="solo")
                    name = name_screen.run()
                    if name:
                        add_score(name, False)
                        print(f"✅ Score enregistré pour {name} (Défaite solo)")

        elif choice == "MULTIJOUEUR":
            # Afficher le menu multijoueur
            multi_menu = MultiplayerMenu(screen)
            multi_choice = multi_menu.run()

            if multi_choice == "HÉBERGER":
                # Afficher l'écran héberger
                host_screen = HostScreen(screen)
                result = host_screen.run()

                if isinstance(result, tuple) and result[0] == "START_GAME":
                    # Lancer le jeu en tant que host
                    print("→ Lancement du jeu multijoueur en tant que HOST...")
                    server = result[1]
                    multi_game = MultiGame(screen, server, is_host=True)
                    game_result = multi_game.run()

                    # MENU_SCORED = scores déjà enregistrés et synchronisés dans le jeu
                    if game_result in ("WIN", "LOSE"):
                        won = game_result == "WIN"
                        name_screen = NameInput(screen, won, mode="multi")
                        name = name_screen.run()
                        if name:
                            add_score(name, won)
                            print(f"✅ Score enregistré pour {name} ({'Victoire' if won else 'Défaite'})")
                    elif game_result == "MENU_SCORED":
                        print("✅ Scores déjà enregistrés et synchronisés")

                elif result == "CANCEL":
                    pass

            elif multi_choice == "REJOINDRE":
                # Afficher l'écran de connexion
                join_screen = JoinScreen(screen)
                result = join_screen.run()

                if isinstance(result, tuple) and result[0] == "CONNECT":
                    # Se connecter au serveur
                    ip = result[1] or "127.0.0.1"
                    port = int(result[2]) if result[2].isdigit() else 5555

                    print(f"→ Connexion à {ip}:{port}...")
                    client = NetworkClient(ip, port)

                    if client.connect():
                        print("✅ Connecté au serveur!")
                        multi_game = MultiGame(screen, client, is_host=False)
                        game_result = multi_game.run()

                        # MENU_SCORED = scores déjà enregistrés et synchronisés dans le jeu
                        if game_result in ("WIN", "LOSE"):
                            won = game_result == "WIN"
                            name_screen = NameInput(screen, won, mode="multi")
                            name = name_screen.run()
                            if name:
                                add_score(name, won)
                                print(f"✅ Score enregistré pour {name} ({'Victoire' if won else 'Défaite'})")
                        elif game_result == "MENU_SCORED":
                            print("✅ Scores déjà enregistrés et synchronisés")
                    else:
                        print("❌ Erreur de connexion")

                elif result == "CANCEL":
                    pass

            elif multi_choice == "RETOUR":
                pass

        elif choice == "SCORES":
            print("→ Affichage des SCORES...")
            scoreboard = Scoreboard(screen)
            scoreboard.run()

        elif choice == "QUITTER":
            print("→ Au revoir !")
            running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()