"""Gestion du leaderboard local (scores.json)."""

import json
import os

SCORES_FILE = os.path.join(os.path.dirname(__file__), "scores.json")


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_scores(scores):
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def add_score(name, won):
    """Incrémente wins ou losses pour `name`. Crée l'entrée si nouvelle."""
    scores = load_scores()

    entry = next((e for e in scores if e["name"].lower() == name.lower()), None)
    if entry is None:
        entry = {"name": name, "wins": 0, "losses": 0, "games": 0}
        scores.append(entry)

    entry["games"] += 1
    if won:
        entry["wins"] += 1
    else:
        entry["losses"] += 1

    scores.sort(key=lambda s: s["wins"], reverse=True)
    save_scores(scores)
    return scores


def clear_scores():
    save_scores([])


def get_leaderboard():
    """Retourne les scores triés par victoires décroissantes."""
    scores = load_scores()
    scores.sort(key=lambda s: s["wins"], reverse=True)
    return scores


def merge_scores(remote_scores):
    """Fusionne un leaderboard distant avec le local (max de chaque stat).

    Utilisé en multi pour synchroniser les deux joueurs.
    """
    local = load_scores()
    index = {e["name"].lower(): e for e in local}

    for r in remote_scores:
        key = r["name"].lower()
        if key in index:
            for field in ("wins", "losses", "games"):
                index[key][field] = max(index[key][field], r.get(field, 0))
        else:
            entry = {"name": r["name"], "wins": r.get("wins", 0),
                     "losses": r.get("losses", 0), "games": r.get("games", 0)}
            local.append(entry)
            index[key] = entry

    local.sort(key=lambda s: s["wins"], reverse=True)
    save_scores(local)
    return local
