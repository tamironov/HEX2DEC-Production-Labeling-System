import tkinter as tk
from tkinter import ttk, messagebox
import win32print
import os
import sys
import ctypes
import json

# --- Default Settings ---
DEFAULT_FO_X = 4
DEFAULT_FO_Y = 20
DEFAULT_FT_X = 40
DEFAULT_FT_Y = 43
DEFAULT_HEX_CHARS = 7

# --- App Folder & Settings File ---
APP_FOLDER = os.path.join(os.environ["APPDATA"], "HEX2DEC Label")
SETTINGS_FILE = os.path.join(APP_FOLDER, "settings.json")

# --- Logic Functions ---
def hex_to_decimal_last(hex_number, hex_chars=DEFAULT_HEX_CHARS):
    """Extracts last N chars and converts to decimal string."""
    try:
        last_n = hex_number[-hex_chars:]
        decimal_number = str(int(last_n, 16)).zfill(hex_chars + 2)
        return decimal_number
    except ValueError:
        return None

def generate_zpl_from_decimal(decimal_value, fo_x, fo_y, ft_x, ft_y):
    """Generates ZPL using an already converted decimal string."""
    zpl = f"""
^XA
^PW124
^MD20
^PR3,3,3
^FO{fo_x},{fo_y}^BY1
^BXN,2,200,16,16,1
^FD{decimal_value}^FS
^FT{ft_x},{ft_y}^ABN,11,7^FD{decimal_value}^FS
^XZ
"""
    return zpl

# --- Settings Functions ---
def load_settings():
    if not os.path.exists(APP_FOLDER):
        os.makedirs(APP_FOLDER)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    # Defaults
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
        messagebox.showerror("Save Error", str(e))

# --- Main Application ---
class ProductionLabelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HEX2DEC Printer Label")
        self.root.geometry("600x450")

        # --- Set Tkinter window icon ---
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(BASE_DIR, "H2Dico.ico")
        try:
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load window icon: {e}")

        # --- Set Taskbar icon (Windows) ---
        if sys.platform.startswith('win'):
            try:
                myappid = "HEX2DECProductionStation"  # unique ID
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception as e:
                print(f"Could not set taskbar icon: {e}")

        # --- Variables ---
        self.fo_x = tk.IntVar(value=DEFAULT_FO_X)
        self.fo_y = tk.IntVar(value=DEFAULT_FO_Y)
        self.ft_x = tk.IntVar(value=DEFAULT_FT_X)
        self.ft_y = tk.IntVar(value=DEFAULT_FT_Y)
        self.hex_chars = tk.IntVar(value=DEFAULT_HEX_CHARS)
        self.selected_printer = tk.StringVar()

        # Load settings
        settings = load_settings()
        self.fo_x.set(settings["fo_x"])
        self.fo_y.set(settings["fo_y"])
        self.ft_x.set(settings["ft_x"])
        self.ft_y.set(settings["ft_y"])
        self.hex_chars.set(settings["hex_chars"])
        self.selected_printer.set(settings["last_printer"])

        self.build_operator_ui()

    # --- UI ---
    def build_operator_ui(self):
        # Status bar
        self.status_frame = tk.Frame(self.root, bg="grey", height=60)
        self.status_frame.pack(fill="x", side="top")
        self.status_label = tk.Label(self.status_frame, text="READY TO SCAN", 
                                     bg="grey", fg="white", font=("Arial", 22, "bold"))
        self.status_label.pack(pady=10)

        # Main frame
        main_frame = tk.Frame(self.root, padx=30, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Printer selection
        tk.Label(main_frame, text="Active Printer:", font=("Arial", 10)).pack(anchor="w")
        try:
            printers = [p[2] for p in win32print.EnumPrinters(2)]
        except:
            printers = []
        self.combo_printer = ttk.Combobox(main_frame, textvariable=self.selected_printer, values=printers, state="readonly", font=("Arial", 12))
        self.combo_printer.pack(fill="x", pady=(0, 20))
        self.combo_printer.bind("<<ComboboxSelected>>", self.save_settings_trigger)

        # Hex input
        tk.Label(main_frame, text="SCAN HEX BARCODE:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.entry_hex = tk.Entry(main_frame, font=("Arial", 26), bg="#e6f3ff", justify="center")
        self.entry_hex.pack(fill="x", ipady=15, pady=5)
        self.entry_hex.bind("<Return>", self.print_label)

        # Last scanned display
        tk.Label(main_frame, text="Last scanned serial (Hex ➡ Printed Decimal):", font=("Arial", 10)).pack(anchor="w", pady=(25,0))
        res_frame = tk.Frame(main_frame, bg="#f0f0f0", bd=2, relief="sunken")
        res_frame.pack(fill="x", pady=5)
        self.lbl_last_scan = tk.Label(res_frame, text="---", font=("Courier New", 18, "bold"), fg="#333", bg="#f0f0f0")
        self.lbl_last_scan.pack(fill="both", ipady=10)

        # Footer with admin button
        footer_frame = tk.Frame(self.root, pady=10, padx=10)
        footer_frame.pack(side="bottom", fill="x")
        tk.Button(footer_frame, text="🛠 Admin / Settings", command=self.open_admin_panel, font=("Arial", 9)).pack(side="right")

        self.entry_hex.focus_set()

    # --- Admin Panel ---
    def open_admin_panel(self):
        admin_win = tk.Toplevel(self.root)
        admin_win.title("Configuration & Help")
        admin_win.geometry("750x450")
        admin_win.grab_set()

        tab_control = ttk.Notebook(admin_win)
        tab_settings = ttk.Frame(tab_control)
        tab_help = ttk.Frame(tab_control)

        tab_control.add(tab_settings, text="Settings")
        tab_control.add(tab_help, text="Help")
        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        def create_setting_row(parent, label_text, variable, row):
            tk.Label(parent, text=label_text).grid(row=row, column=0, sticky="e", pady=10, padx=10)
            tk.Entry(parent, textvariable=variable, width=15).grid(row=row, column=1, sticky="w")

        create_setting_row(tab_settings, "DataMatrix FO X:", self.fo_x, 0)
        create_setting_row(tab_settings, "DataMatrix FO Y:", self.fo_y, 1)
        create_setting_row(tab_settings, "Text FT X:", self.ft_x, 2)
        create_setting_row(tab_settings, "Text FT Y:", self.ft_y, 3)
        tk.Label(tab_settings, text="Hex Chars to Convert:").grid(row=4, column=0, sticky="e", pady=10, padx=10)
        tk.Spinbox(tab_settings, from_=1, to=16, textvariable=self.hex_chars, width=13).grid(row=4, column=1, sticky="w")

        btn_frame = tk.Frame(tab_settings)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        tk.Button(btn_frame, text="Reset Defaults", command=self.reset_defaults, bg="#ffdddd").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Save Settings", command=lambda: [self.save_settings(), messagebox.showinfo("Saved", "Settings Saved!")], bg="#ddffdd").pack(side="left", padx=10)

        # Help Tab
        help_text = tk.Text(tab_help, wrap="word", height=20)
        help_text.pack(expand=True, fill="both", padx=5, pady=5)
        help_text.insert("1.0", r"""
        📌 HELP / INSTRUCTIONS
        • Works on label Arad PN: 95000089
        • Select your printer from the list.
        • Scan a HEX barcode in the main tab.
            → It will print automatically.
        • Settings tab allows adjusting label position:
            - FO X / FO Y = DataMatrix location
            - FT X / FT Y = Text location
            - Hex Characters to Convert = number of last hex digits used for conversion
        • Press "Reset to Defaults" to restore original values.
        • Press "Save Settings" to save current settings for next time.
            → Saved at: C:\Users\<username>\AppData\Roaming\HEX2DEC Label
                         
        Created by Tamir Mironov
        """)
        help_text.config(state="disabled")

    # --- Logic & Printing ---
    def set_status(self, message, status_type):
        color = {"success": "#28a745", "error": "#dc3545"}.get(status_type, "grey")
        self.status_frame.config(bg=color)
        self.status_label.config(text=message, bg=color, fg="white")
        self.root.update_idletasks()
        if status_type == "success":
            self.root.after(1500, self.reset_status)

    def reset_status(self):
        self.status_frame.config(bg="grey")
        self.status_label.config(text="READY TO SCAN", bg="grey")

    def print_label(self, event=None):
        printer_name = self.selected_printer.get()
        hex_input = self.entry_hex.get().strip()
        if not printer_name:
            self.set_status("ERROR: SELECT PRINTER", "error")
            return
        if not hex_input:
            self.set_status("ERROR: EMPTY INPUT", "error")
            return

        decimal_val = hex_to_decimal_last(hex_input, self.hex_chars.get())
        if not decimal_val:
            self.set_status("ERROR: INVALID HEX", "error")
            return

        zpl = generate_zpl_from_decimal(decimal_val, self.fo_x.get(), self.fo_y.get(),
                                        self.ft_x.get(), self.ft_y.get())
        try:
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("ZPL Label", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, zpl.encode("utf-8"))
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
                self.set_status("PRINT SUCCESSFUL", "success")
                self.lbl_last_scan.config(text=f"{hex_input}  ➡  {decimal_val}", fg="#006400")
                self.entry_hex.delete(0, tk.END)
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception as e:
            self.set_status(f"SYS ERROR: {str(e)[:15]}...", "error")
            print(e)
        self.entry_hex.focus_set()

    def reset_defaults(self):
        self.fo_x.set(DEFAULT_FO_X)
        self.fo_y.set(DEFAULT_FO_Y)
        self.ft_x.set(DEFAULT_FT_X)
        self.ft_y.set(DEFAULT_FT_Y)
        self.hex_chars.set(DEFAULT_HEX_CHARS)

    def save_settings_trigger(self, event=None):
        self.save_settings()

    def save_settings(self):
        data = {
            "fo_x": self.fo_x.get(),
            "fo_y": self.fo_y.get(),
            "ft_x": self.ft_x.get(),
            "ft_y": self.ft_y.get(),
            "hex_chars": self.hex_chars.get(),
            "last_printer": self.selected_printer.get()
        }
        save_settings(data)

# --- Run Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ProductionLabelApp(root)
    root.mainloop()
