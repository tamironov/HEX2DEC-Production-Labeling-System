import os

# --- Default Settings ---
DEFAULT_FO_X = 4
DEFAULT_FO_Y = 20
DEFAULT_FT_X = 40
DEFAULT_FT_Y = 43
DEFAULT_HEX_CHARS = 7 

# --- App Folder & Settings File ---
APP_FOLDER = os.path.join(os.environ["APPDATA"], "HEX2DEC Label")
SETTINGS_FILE = os.path.join(APP_FOLDER, "settings.json")
