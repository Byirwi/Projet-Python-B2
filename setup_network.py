#!/usr/bin/env python3
"""
setup_network.py - Script de configuration du mode multijoueur

Ce script aide à configurer et tester le système multijoueur
"""

import os
import sys
import subprocess
import platform


def print_banner():
    """Afficher la bannière"""
    print("""
╔═════════════════════════════════════════════════════════════════════╗
║           🎮 TANK BATTLE - SETUP MULTIJOUEUR 🎮                   ║
║                                                                   ║
║  Ce script aide à configurer votre jeu pour le mode multijoueur   ║
║  en réseau local.                                                 ║
╚═════════════════════════════════════════════════════════════════════╝
    """)


def check_python():
    """Vérifier la version de Python"""
    version = sys.version_info
    print(f"[*] Vérification de Python...")
    print(f"    Version: Python {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Erreur: Python 3.8+ requis")
        return False

    print("✅ Python OK\n")
    return True


def check_pygame():
    """Vérifier Pygame"""
    print("[*] Vérification de Pygame...")
    try:
        import pygame
        print(f"    Version: {pygame.version.ver}")
        print("✅ Pygame OK\n")
        return True
    except ImportError:
        print("❌ Pygame non installé\n")
        return False


def install_pygame():
    """Installer Pygame"""
    print("[*] Installation de Pygame...")
    try:
        if platform.system() == "Windows":
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pygame"])
        print("✅ Pygame installé avec succès\n")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}\n")
        return False


def check_files():
    """Vérifier les fichiers nécessaires"""
    print("[*] Vérification des fichiers...")

    required_files = [
        "Main.py",
        "Game/Network.py",
        "Game/Network_Config.py",
        "Game/Multi_Game.py",
        "UI/Join_Screen.py",
        "UI/Host_Screen.py",
    ]

    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"    ✅ {file}")
        else:
            print(f"    ❌ {file}")
            missing.append(file)

    if missing:
        print(f"\n❌ Fichiers manquants: {', '.join(missing)}\n")
        return False

    print("✅ Tous les fichiers OK\n")
    return True


def test_network():
    """Tester la connexion réseau"""
    print("[*] Test du système réseau...")

    try:
        if os.path.exists("Test_Network.py"):
            print("    En cours d'exécution...\n")
            result = subprocess.call([sys.executable, "Test_Network.py"])

            if result == 0:
                print("\n✅ Tests réseau passés\n")
                return True
            else:
                print("\n❌ Tests réseau échoués\n")
                return False
        else:
            print("    ❌ Test_Network.py non trouvé\n")
            return False
    except Exception as e:
        print(f"    ❌ Erreur: {e}\n")
        return False


def show_quick_start():
    """Afficher un guide de démarrage rapide"""
    print("""
╔═════════════════════════════════════════════════════════════════════╗
║                     🚀 DÉMARRAGE RAPIDE 🚀                         ║
╚═════════════════════════════════════════════════════════════════════╝

JOUEUR 1 (Serveur/HOST):
  1. Lancez: python Main.py
  2. Allez dans: Menu → Multijoueur → Héberger
  3. Notez votre IP locale (ex: 192.168.1.100)

JOUEUR 2 (Client):
  1. Lancez: python Main.py
  2. Allez dans: Menu → Multijoueur → Rejoindre
  3. Entrez l'IP du joueur 1
  4. Cliquez sur CONNECTER

COMMANDES DE JEU:
  • Souris: Orienter le canon
  • Clic gauche: Tirer
  • ESC: Quitter

═════════════════════════════════════════════════════════════════════

POUR TESTER SANS PYGAME:
  Terminal 1: python Demo_Server.py
  Terminal 2: python Demo_Client.py 127.0.0.1

═════════════════════════════════════════════════════════════════════
    """)


def main():
    """Fonction principale"""
    print_banner()

    # Vérifier Python
    if not check_python():
        return False

    # Vérifier Pygame
    if not check_pygame():
        print("[?] Voulez-vous installer Pygame? (y/n): ", end="")
        response = input().lower()
        if response == "y":
            if not install_pygame():
                return False
        else:
            print("Pygame est requis pour jouer\n")
            return False

    # Vérifier les fichiers
    if not check_files():
        print("Veuillez vous assurer que tous les fichiers sont présents\n")
        return False

    # Tester le réseau
    print("[?] Voulez-vous tester le système réseau? (y/n): ", end="")
    response = input().lower()
    if response == "y":
        if not test_network():
            print("⚠️  Les tests ont échoué, mais vous pouvez quand même jouer\n")

    # Afficher le guide de démarrage
    show_quick_start()

    print("✅ Configuration terminée !")
    print("Vous pouvez maintenant jouer en réseau local !\n")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[*] Annulation par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

