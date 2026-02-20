#!/usr/bin/env python3
"""
Demo_Client.py - Démonstration simple d'un client réseau
Utile pour tester sans avoir besoin de pygame
"""

import sys
import time
import socket
from Game.Network import NetworkClient
from Game.Network_Config import DEBUG, DEFAULT_PORT

def demo_client(host="127.0.0.1"):
    """Client de démonstration"""

    print("╔═════════════════════════════════════════════════════════════╗")
    print("║     🎮 TANK BATTLE - CLIENT DE DÉMONSTRATION 🎮            ║")
    print("╚═════════════════════════════════════════════════════════════╝\n")

    # Créer le client
    print(f"[*] Connexion au serveur {host}:{DEFAULT_PORT}...")
    client = NetworkClient(host, DEFAULT_PORT)

    if not client.connect():
        print("❌ Erreur: Impossible de se connecter au serveur")
        print(f"   └─ Vérifiez que le serveur est lancé sur {host}:{DEFAULT_PORT}")
        return False

    print(f"✅ Connecté au serveur !\n")

    # Boucle d'interaction
    print("🔄 Boucle d'interaction (appuyez sur Ctrl+C pour quitter)\n")

    try:
        counter = 0
        while True:
            # Envoyer des données de test
            test_data = {
                "type": "client_test",
                "timestamp": time.time(),
                "counter": counter,
                "message": f"Message #{counter} du client"
            }

            if client.send(test_data):
                print(f"[CLIENT] Envoi: Message #{counter}")
            else:
                print(f"[CLIENT] Erreur lors de l'envoi du message #{counter}")

            # Recevoir des données du serveur
            data = client.receive()
            if data:
                print(f"[CLIENT] Reçu: {data}")

            counter += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[*] Déconnexion du serveur...")
        client.disconnect()
        print("✅ Déconnecté")
        return True


if __name__ == "__main__":
    host = "127.0.0.1"  # localhost par défaut

    # Permettre de passer l'adresse IP en paramètre
    if len(sys.argv) > 1:
        host = sys.argv[1]
        print(f"🔗 Utilisation de l'hôte: {host}")

    try:
        demo_client(host)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

