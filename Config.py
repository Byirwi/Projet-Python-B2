# config.py

# =============================================================================================
# DIMENSIONS
# =============================================================================================

# Menu
MENU_WIDTH = 1024
MENU_HEIGHT = 768
FPS = 60

# Map
MAP_WIDTH = 2560
MAP_HEIGHT = 1600

# Tank
TANK_WIDTH = 50
TANK_HEIGHT = 50

# Shell
SHELL_WIDTH = 3
SHELL_HEIGHT = 7

# =============================================================================================
# COULEURS
# =============================================================================================

# Fond
COLOR_BG = (20, 20, 30)            # Fond sombre
COLOR_BG_GRADIENT = (10, 10, 20)   # Fond dégradé (pour animations)

# Texte
COLOR_TEXT = (255, 255, 255)       # Blanc
COLOR_TEXT_DARK = (100, 100, 100)  # Gris foncé

# Menu principal
COLOR_TITLE = (255, 200, 0)        # Or pour le titre
COLOR_SELECTED = (255, 255, 255)   # Blanc pour option sélectionnée
COLOR_NORMAL = (100, 100, 100)     # Gris pour options normales
COLOR_ACCENT = (255, 200, 0)       # Or pour accents

# Menu multijoueur (pour différencier)
COLOR_TITLE_MULTI = (100, 200, 255)  # Bleu pour menu multi
COLOR_ACCENT_MULTI = (100, 200, 255) # Bleu pour accents multi

# Informations réseau
COLOR_INFO = (0, 255, 100)         # Vert pour IP/Port

# Champs de saisie
COLOR_INPUT_BG = (40, 40, 50)      # Fond du champ
COLOR_INPUT_ACTIVE = (255, 200, 0) # Bordure active (or)

# =============================================================================================
# RÉSEAU
# =============================================================================================

SERVER_PORT = 5555