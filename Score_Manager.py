# Score_Manager.py
"""Gestion des scores locaux (leaderboard)"""

import json
import os

SCORES_FILE = os.path.join(os.path.dirname(__file__), "scores.json")


def load_scores():
    """Charge les scores depuis le fichier JSON"""
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_scores(scores):
    """Sauvegarde les scores dans le fichier JSON"""
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def add_score(name, won):
    """
    Ajoute une victoire ou défaite pour un joueur.

    Args:
        name: Nom du joueur
        won: True si victoire, False si défaite
    """
    scores = load_scores()

    # Chercher le joueur existant
    player_entry = None
    for entry in scores:
        if entry["name"].lower() == name.lower():
            player_entry = entry
            break

    if player_entry is None:
        player_entry = {"name": name, "wins": 0, "losses": 0, "games": 0}
        scores.append(player_entry)

    player_entry["games"] += 1
    if won:
        player_entry["wins"] += 1
    else:
        player_entry["losses"] += 1

    # Trier par nombre de victoires (décroissant)
    scores.sort(key=lambda s: s["wins"], reverse=True)

    save_scores(scores)
    return scores


def clear_scores():
    """Supprime tous les scores"""
    save_scores([])


def get_leaderboard():
    """Retourne le leaderboard trié par victoires"""
    scores = load_scores()
    scores.sort(key=lambda s: s["wins"], reverse=True)
    return scores


def merge_scores(remote_scores):
    """
    Fusionne un leaderboard distant avec le leaderboard local.
    Pour chaque joueur, on prend le maximum de wins, losses et games
    afin que les deux côtés finissent avec les mêmes données.

    Args:
        remote_scores: Liste de dicts [{"name":..., "wins":..., "losses":..., "games":...}, ...]

    Returns:
        Liste fusionnée et triée
    """
    local_scores = load_scores()

    # Indexer les scores locaux par nom (insensible à la casse)
    index = {}
    for entry in local_scores:
        index[entry["name"].lower()] = entry

    # Fusionner les scores distants
    for remote in remote_scores:
        key = remote["name"].lower()
        if key in index:
            local_entry = index[key]
            local_entry["wins"] = max(local_entry["wins"], remote.get("wins", 0))
            local_entry["losses"] = max(local_entry["losses"], remote.get("losses", 0))
            local_entry["games"] = max(local_entry["games"], remote.get("games", 0))
        else:
            new_entry = {
                "name": remote["name"],
                "wins": remote.get("wins", 0),
                "losses": remote.get("losses", 0),
                "games": remote.get("games", 0),
            }
            local_scores.append(new_entry)
            index[key] = new_entry

    local_scores.sort(key=lambda s: s["wins"], reverse=True)
    save_scores(local_scores)
    return local_scores


