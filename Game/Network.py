"""
Network.py - Gestion de la communication réseau pour le jeu multijoueur
Utilise les sockets TCP pour communiquer entre joueurs
"""

import socket
import json
import threading
import time
from Game.Network_Config import (
    CONNECTION_TIMEOUT, RECEIVE_TIMEOUT, MAX_MESSAGE_SIZE,
    SERVER_BIND_ADDRESS, DEBUG
)


class NetworkServer:
    """Serveur réseau pour accueillir un joueur"""

    def __init__(self, port=5555):
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.is_running = False
        self.received_data = None
        self.lock = threading.Lock()

    def start(self):
        """Démarrer le serveur et attendre une connexion"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((SERVER_BIND_ADDRESS, self.port))
            self.server_socket.listen(1)
            self.is_running = True

            if DEBUG:
                print(f"[NETWORK] Serveur démarré sur {SERVER_BIND_ADDRESS}:{self.port}")

            # Thread d'écoute
            thread = threading.Thread(target=self._listen, daemon=True)
            thread.start()

            return True
        except Exception as e:
            print(f"Erreur démarrage serveur: {e}")
            return False

    def _listen(self):
        """Écouter les connexions entrantes"""
        try:
            self.client_socket, addr = self.server_socket.accept()
            self.client_socket.settimeout(RECEIVE_TIMEOUT)
            if DEBUG:
                print(f"[NETWORK] Client connecté depuis {addr}")

            while self.is_running:
                try:
                    data = self.client_socket.recv(MAX_MESSAGE_SIZE).decode('utf-8')
                    if data:
                        with self.lock:
                            self.received_data = data
                except socket.timeout:
                    continue
                except:
                    break
        except Exception as e:
            if DEBUG:
                print(f"Erreur écoute: {e}")

    def send(self, data):
        """Envoyer des données au client"""
        try:
            if self.client_socket:
                message = json.dumps(data).encode('utf-8')
                if DEBUG:
                    print(f"[NETWORK-SERVER] Envoi: {data}")
                self.client_socket.sendall(message)
                return True
        except Exception as e:
            if DEBUG:
                print(f"Erreur envoi: {e}")
        return False

    def receive(self):
        """Recevoir des données du client"""
        with self.lock:
            if self.received_data:
                data = self.received_data
                self.received_data = None
                try:
                    return json.loads(data)
                except:
                    return None
        return None

    def stop(self):
        """Arrêter le serveur"""
        self.is_running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()


class NetworkClient:
    """Client réseau pour rejoindre un serveur"""

    def __init__(self, host, port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.is_running = False
        self.received_data = None
        self.lock = threading.Lock()

    def connect(self):
        """Se connecter au serveur"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(CONNECTION_TIMEOUT)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(RECEIVE_TIMEOUT)
            self.is_running = True

            if DEBUG:
                print(f"[NETWORK-CLIENT] Connecté à {self.host}:{self.port}")

            # Thread d'écoute
            thread = threading.Thread(target=self._listen, daemon=True)
            thread.start()

            return True
        except Exception as e:
            print(f"Erreur connexion: {e}")
            return False

    def _listen(self):
        """Écouter les messages du serveur"""
        try:
            while self.is_running:
                try:
                    data = self.socket.recv(MAX_MESSAGE_SIZE).decode('utf-8')
                    if data:
                        with self.lock:
                            self.received_data = data
                        if DEBUG:
                            print(f"[NETWORK-CLIENT] Reçu: {data}")
                except socket.timeout:
                    continue
                except:
                    break
        except Exception as e:
            if DEBUG:
                print(f"Erreur écoute client: {e}")

    def send(self, data):
        """Envoyer des données au serveur"""
        try:
            if self.socket:
                message = json.dumps(data).encode('utf-8')
                if DEBUG:
                    print(f"[NETWORK-CLIENT] Envoi: {data}")
                self.socket.sendall(message)
                return True
        except Exception as e:
            if DEBUG:
                print(f"Erreur envoi client: {e}")
        return False

    def receive(self):
        """Recevoir des données du serveur"""
        with self.lock:
            if self.received_data:
                data = self.received_data
                self.received_data = None
                try:
                    return json.loads(data)
                except:
                    return None
        return None

    def disconnect(self):
        """Se déconnecter du serveur"""
        self.is_running = False
        if self.socket:
            self.socket.close()








