import os, json
from config import APP_FOLDER, SETTINGS_FILE, DEFAULT_FO_X, DEFAULT_FO_Y, DEFAULT_FT_X, DEFAULT_FT_Y, DEFAULT_HEX_CHARS

def load_settings():
    if not os.path.exists(APP_FOLDER):
        os.makedirs(APP_FOLDER)

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return {
                    "fo_x": data.get("fo_x", DEFAULT_FO_X),
                    "fo_y": data.get("fo_y", DEFAULT_FO_Y),
                    "ft_x": data.get("ft_x", DEFAULT_FT_X),
                    "ft_y": data.get("ft_y", DEFAULT_FT_Y),
                    "hex_chars": data.get("hex_chars", DEFAULT_HEX_CHARS),
                    "last_printer": data.get("last_printer", "")
                }
        except:
            pass
    # Defaults if nothing exists
    return {
        "fo_x": DEFAULT_FO_X,
        "fo_y": DEFAULT_FO_Y,
        "ft_x": DEFAULT_FT_X,
        "ft_y": DEFAULT_FT_Y,
        "hex_chars": DEFAULT_HEX_CHARS,
        "last_printer": ""
    }

def save_settings(data):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Save Error", str(e))
