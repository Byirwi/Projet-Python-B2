# Main.py
import pygame
import sys
from UI.Menu import MainMenu
from UI.Multiplayer_Menu import MultiplayerMenu


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
            #Lancer le jeu solo

        elif choice == "MULTIJOUEUR":
            # Afficher le menu multijoueur
            multi_menu = MultiplayerMenu(screen)
            multi_choice = multi_menu.run()

            if multi_choice == "HÉBERGER":
                print("→ Hébergement d'une partie...")
                #Écran héberger
                # from UI.Host_Screen import HostScreen
                # host = HostScreen(screen)
                # host.run()

            elif multi_choice == "REJOINDRE":
                print("→ Rejoindre une partie...")
                #Écran rejoindre
                # from UI.Join_Screen import JoinScreen
                # join = JoinScreen(screen)
                # join.run()

            elif multi_choice == "RETOUR":
                # Retour au menu principal (la boucle va recommencer)
                pass

        elif choice == "SCORES":
            print("→ Affichage des SCORES...")
            #Afficher scoreboard

        elif choice == "QUITTER":
            print("→ Au revoir !")
            running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()