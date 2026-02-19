"""
Network.py - Gestion de la communication réseau pour le jeu multijoueur
Utilise les sockets TCP avec un protocole à délimiteur (newline) pour
garantir que chaque message JSON est reçu intégralement et séparément.
"""

import socket
import json
import threading
from collections import deque
from Game.Network_Config import (
    CONNECTION_TIMEOUT, RECEIVE_TIMEOUT, MAX_MESSAGE_SIZE,
    SERVER_BIND_ADDRESS, DEBUG
)

# Délimiteur de fin de message (ne doit pas apparaître dans le JSON)
_DELIMITER = b'\n'


class NetworkServer:
    """Serveur réseau pour accueillir un joueur"""

    def __init__(self, port=5555):
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.is_running = False
        self._queue = deque(maxlen=120)   # file de messages reçus
        self._buffer = b""                # buffer TCP partiel
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
                    chunk = self.client_socket.recv(MAX_MESSAGE_SIZE)
                    if not chunk:
                        break  # connexion fermée
                    self._buffer += chunk

                    # Découper le buffer en messages complets (délimités par \n)
                    while _DELIMITER in self._buffer:
                        msg_bytes, self._buffer = self._buffer.split(_DELIMITER, 1)
                        if msg_bytes:
                            try:
                                parsed = json.loads(msg_bytes.decode('utf-8'))
                                with self.lock:
                                    self._queue.append(parsed)
                                if DEBUG:
                                    print(f"[NETWORK-SERVER] Reçu: {parsed}")
                            except json.JSONDecodeError:
                                pass  # message corrompu, on l'ignore

                except socket.timeout:
                    continue
                except Exception:
                    break
        except Exception as e:
            if DEBUG:
                print(f"Erreur écoute: {e}")

    def send(self, data):
        """Envoyer des données au client (JSON + délimiteur)"""
        try:
            if self.client_socket:
                message = json.dumps(data, separators=(',', ':')).encode('utf-8') + _DELIMITER
                if DEBUG:
                    print(f"[NETWORK-SERVER] Envoi: {data}")
                self.client_socket.sendall(message)
                return True
        except Exception as e:
            if DEBUG:
                print(f"Erreur envoi: {e}")
        return False

    def receive(self):
        """Recevoir le prochain message de la file d'attente"""
        with self.lock:
            if self._queue:
                return self._queue.popleft()
        return None

    def stop(self):
        """Arrêter le serveur"""
        self.is_running = False
        try:
            if self.client_socket:
                self.client_socket.close()
        except Exception:
            pass
        try:
            if self.server_socket:
                self.server_socket.close()
        except Exception:
            pass


class NetworkClient:
    """Client réseau pour rejoindre un serveur"""

    def __init__(self, host, port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.is_running = False
        self._queue = deque(maxlen=120)
        self._buffer = b""
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
                    chunk = self.socket.recv(MAX_MESSAGE_SIZE)
                    if not chunk:
                        break
                    self._buffer += chunk

                    while _DELIMITER in self._buffer:
                        msg_bytes, self._buffer = self._buffer.split(_DELIMITER, 1)
                        if msg_bytes:
                            try:
                                parsed = json.loads(msg_bytes.decode('utf-8'))
                                with self.lock:
                                    self._queue.append(parsed)
                                if DEBUG:
                                    print(f"[NETWORK-CLIENT] Reçu: {parsed}")
                            except json.JSONDecodeError:
                                pass

                except socket.timeout:
                    continue
                except Exception:
                    break
        except Exception as e:
            if DEBUG:
                print(f"Erreur écoute client: {e}")

    def send(self, data):
        """Envoyer des données au serveur (JSON + délimiteur)"""
        try:
            if self.socket:
                message = json.dumps(data, separators=(',', ':')).encode('utf-8') + _DELIMITER
                if DEBUG:
                    print(f"[NETWORK-CLIENT] Envoi: {data}")
                self.socket.sendall(message)
                return True
        except Exception as e:
            if DEBUG:
                print(f"Erreur envoi client: {e}")
        return False

    def receive(self):
        """Recevoir le prochain message de la file d'attente"""
        with self.lock:
            if self._queue:
                return self._queue.popleft()
        return None

    def disconnect(self):
        """Se déconnecter du serveur"""
        self.is_running = False
        try:
            if self.socket:
                self.socket.close()
        except Exception:
            pass



