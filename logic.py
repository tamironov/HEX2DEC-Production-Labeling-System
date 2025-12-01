from config import DEFAULT_HEX_CHARS

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
