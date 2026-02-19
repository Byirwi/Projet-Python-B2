"""Réseau TCP avec protocole newline-delimited JSON.

Chaque message est un objet JSON terminé par \\n.
Les messages sont stockés dans une deque (FIFO) côté réception.
"""

import socket
import json
import threading
from collections import deque
from Game.Network_Config import (
    CONNECTION_TIMEOUT, RECEIVE_TIMEOUT, MAX_MESSAGE_SIZE,
    SERVER_BIND_ADDRESS, DEBUG
)

_DELIMITER = b'\n'


class NetworkServer:
    """Serveur TCP — accepte un seul client."""

    def __init__(self, port=5555):
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.is_running = False
        self._queue = deque(maxlen=120)
        self._buffer = b""
        self.lock = threading.Lock()

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((SERVER_BIND_ADDRESS, self.port))
            self.server_socket.listen(1)
            self.is_running = True
            if DEBUG:
                print(f"[SERVER] Écoute sur {SERVER_BIND_ADDRESS}:{self.port}")
            threading.Thread(target=self._listen, daemon=True).start()
            return True
        except Exception as e:
            print(f"Erreur démarrage serveur: {e}")
            return False

    def _listen(self):
        try:
            self.client_socket, addr = self.server_socket.accept()
            self.client_socket.settimeout(RECEIVE_TIMEOUT)
            if DEBUG:
                print(f"[SERVER] Client connecté : {addr}")
            self._read_loop(self.client_socket)
        except Exception as e:
            if DEBUG:
                print(f"[SERVER] Erreur écoute : {e}")

    def _read_loop(self, sock):
        """Boucle de lecture commune : découpe le flux TCP en messages JSON."""
        while self.is_running:
            try:
                chunk = sock.recv(MAX_MESSAGE_SIZE)
                if not chunk:
                    break
                self._buffer += chunk
                while _DELIMITER in self._buffer:
                    raw, self._buffer = self._buffer.split(_DELIMITER, 1)
                    if raw:
                        try:
                            with self.lock:
                                self._queue.append(json.loads(raw))
                        except json.JSONDecodeError:
                            pass
            except socket.timeout:
                continue
            except Exception:
                break

    def send(self, data):
        try:
            if self.client_socket:
                self.client_socket.sendall(
                    json.dumps(data, separators=(',', ':')).encode() + _DELIMITER
                )
                return True
        except Exception as e:
            if DEBUG:
                print(f"[SERVER] Erreur envoi : {e}")
        return False

    def receive(self):
        with self.lock:
            return self._queue.popleft() if self._queue else None

    def stop(self):
        self.is_running = False
        for s in (self.client_socket, self.server_socket):
            try:
                if s: s.close()
            except Exception:
                pass


class NetworkClient:
    """Client TCP — se connecte à un NetworkServer."""

    def __init__(self, host, port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.is_running = False
        self._queue = deque(maxlen=120)
        self._buffer = b""
        self.lock = threading.Lock()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(CONNECTION_TIMEOUT)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(RECEIVE_TIMEOUT)
            self.is_running = True
            if DEBUG:
                print(f"[CLIENT] Connecté à {self.host}:{self.port}")
            threading.Thread(target=self._listen, daemon=True).start()
            return True
        except Exception as e:
            print(f"Erreur connexion: {e}")
            return False

    def _listen(self):
        """Boucle de lecture : même logique que le serveur."""
        while self.is_running:
            try:
                chunk = self.socket.recv(MAX_MESSAGE_SIZE)
                if not chunk:
                    break
                self._buffer += chunk
                while _DELIMITER in self._buffer:
                    raw, self._buffer = self._buffer.split(_DELIMITER, 1)
                    if raw:
                        try:
                            with self.lock:
                                self._queue.append(json.loads(raw))
                        except json.JSONDecodeError:
                            pass
            except socket.timeout:
                continue
            except Exception:
                break

    def send(self, data):
        try:
            if self.socket:
                self.socket.sendall(
                    json.dumps(data, separators=(',', ':')).encode() + _DELIMITER
                )
                return True
        except Exception as e:
            if DEBUG:
                print(f"[CLIENT] Erreur envoi : {e}")
        return False

    def receive(self):
        with self.lock:
            return self._queue.popleft() if self._queue else None

    def disconnect(self):
        self.is_running = False
        try:
            if self.socket:
                self.socket.close()
        except Exception:
            pass
