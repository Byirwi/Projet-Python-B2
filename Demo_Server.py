#!/usr/bin/env python3
"""
Demo_Server.py - Démonstration simple d'un serveur réseau
Utile pour tester sans avoir besoin de pygame
"""

import sys
import time
from Game.Network import NetworkServer
from Game.Network_Config import DEBUG, DEFAULT_PORT

def demo_server():
    """Serveur de démonstration"""

    print("╔═════════════════════════════════════════════════════════════╗")
    print("║     🎮 TANK BATTLE - SERVEUR DE DÉMONSTRATION 🎮           ║")
    print("╚═════════════════════════════════════════════════════════════╝\n")

    # Créer et démarrer le serveur
    print(f"[*] Démarrage du serveur sur le port {DEFAULT_PORT}...")
    server = NetworkServer(DEFAULT_PORT)

    if not server.start():
        print("❌ Erreur: Impossible de démarrer le serveur")
        return False

    print(f"✅ Serveur démarré avec succès !")
    print(f"\n📝 Informations de connexion :")
    print(f"   └─ Adresse: 127.0.0.1:{DEFAULT_PORT}")
    print(f"   └─ Port: {DEFAULT_PORT}\n")

    print("⏳ En attente d'une connexion client...")
    print("   (Lancez Demo_Client.py dans un autre terminal)\n")

    # Attendre la connexion
    start_time = time.time()
    timeout = 60  # 60 secondes de timeout

    while time.time() - start_time < timeout:
        if server.client_socket is not None:
            print("✅ Client connecté !\n")
            break
        time.sleep(0.1)
    else:
        print("❌ Timeout: Aucun client ne s'est connecté")
        server.stop()
        return False

    # Boucle d'interaction
    print("🔄 Boucle d'interaction (appuyez sur Ctrl+C pour quitter)\n")

    try:
        counter = 0
        while True:
            # Envoyer des données de test
            test_data = {
                "type": "server_test",
                "timestamp": time.time(),
                "counter": counter,
                "message": f"Message #{counter} du serveur"
            }

            if server.send(test_data):
                print(f"[SERVER] Envoi: Message #{counter}")
            else:
                print(f"[SERVER] Erreur lors de l'envoi du message #{counter}")

            # Recevoir des données du client
            data = server.receive()
            if data:
                print(f"[SERVER] Reçu: {data}")

            counter += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[*] Arrêt du serveur...")
        server.stop()
        print("✅ Serveur arrêté")
        return True


if __name__ == "__main__":
    try:
        demo_server()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

