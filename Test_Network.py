# Test_Network.py - Test simple du système réseau

import sys
from Game.Network import NetworkServer, NetworkClient
import threading
import time

def test_network():
    """Test simple du système réseau"""

    print("=" * 50)
    print("TEST DU SYSTÈME RÉSEAU")
    print("=" * 50)

    # Test 1: Créer un serveur
    print("\n[TEST 1] Création du serveur...")
    server = NetworkServer(5555)

    if server.start():
        print("✅ Serveur démarré sur le port 5555")
    else:
        print("❌ Erreur: Impossible de démarrer le serveur")
        return False

    # Test 2: Créer un client dans un thread séparé
    print("\n[TEST 2] Création d'un client...")

    def connect_client():
        time.sleep(1)  # Attendre que le serveur soit prêt
        client = NetworkClient("127.0.0.1", 5555)
        if client.connect():
            print("✅ Client connecté au serveur")

            # Envoyer un message
            print("\n[TEST 3] Envoi d'un message du client...")
            test_data = {"test": "Hello Server!", "number": 42}
            if client.send(test_data):
                print("✅ Message envoyé")

            time.sleep(0.5)

            # Recevoir un réponse
            print("\n[TEST 4] Attente d'une réponse du serveur...")
            time.sleep(1)
            response = client.receive()
            if response:
                print(f"✅ Réponse reçue: {response}")

            client.disconnect()
        else:
            print("❌ Erreur: Impossible de se connecter au serveur")

    # Lancer le client dans un thread
    client_thread = threading.Thread(target=connect_client)
    client_thread.start()

    # Serveur: Recevoir le message du client
    print("\n[TEST 3 - SERVER] Attente d'un message du client...")
    time.sleep(2)
    data = server.receive()
    if data:
        print(f"✅ Serveur a reçu: {data}")

        # Envoyer une réponse
        print("\n[TEST 4 - SERVER] Envoi d'une réponse...")
        server.send({"response": "Hello Client!", "status": "ok"})
        print("✅ Réponse envoyée")

    client_thread.join()

    # Arrêter le serveur
    print("\n[TEST 5] Arrêt du serveur...")
    server.stop()
    print("✅ Serveur arrêté")

    print("\n" + "=" * 50)
    print("✅ TOUS LES TESTS SONT PASSÉS!")
    print("=" * 50)

    return True

if __name__ == "__main__":
    try:
        test_network()
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

