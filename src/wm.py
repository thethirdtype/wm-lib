import tkinter as tk
import ctypes


'''

wm-lib
Window Manager Library for Tkinter

Author: thirdtype
https://github.com/thethirdtype

'''


def is_dark_mode():
    try:
        # Check the system-wide color preferences using GETCLIENTAREAANIMATION
        ui_param = ctypes.c_uint(0)
        ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(ui_param), 0)
        return ui_param.value == 1
    except Exception as e:
        print(f"Error detecting dark mode: {e}")
        return None


def load_color_schemes_from_css(css_file):
    color_schemes = {}
    if css_file:
        try:
            with open(css_file, 'r') as f:
                lines = f.readlines()
                current_widget = None
                for line in lines:
                    line = line.strip()
                    if line.startswith('.'):
                        current_widget = line.split('.')[1].split('{')[0].strip()
                        color_schemes[current_widget] = {}
                    elif current_widget and ':' in line:
                        key, value = line.split(':')
                        key = key.strip()
                        value = value.strip().rstrip(';')
                        color_schemes[current_widget][key] = value
        except FileNotFoundError:
            print(f"CSS file '{css_file}' not found. Skipping color scheme loading.")
        except Exception as e:
            print(f"Error loading color schemes from CSS file: {e}")
    return color_schemes


class Window:
    def __init__(self, title=None, width=300, height=200, center_screen=True, x=0, y=0, icon=None,
                 disable_dark_mode=False, force_dark_mode=False, css_file="dark_theme.css"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")

        if center_screen:
            self.root.eval("tk::PlaceWindow . center")
        else:
            self.root.geometry(f"+{x}+{y}")

        # Check if dark mode is enabled
        dark_mode = is_dark_mode()

        # Set window colors for dark mode
        if force_dark_mode or (not disable_dark_mode and dark_mode):
            # Load color schemes from CSS file if provided
            self.color_schemes = load_color_schemes_from_css(css_file)

            # Set background color for the root window
            if "Toplevel" in self.color_schemes:
                color_scheme = self.color_schemes["Toplevel"]
                bg_color = color_scheme.get("background-color", "")
                if bg_color:
                    self.root.configure(bg=bg_color)

        # Set Icon
        if icon:
            self.root.iconbitmap(icon)

    def create(self, widget_type, **kwargs):
        if not isinstance(widget_type, type):
            # Prepend tk. if widget_type is not a class
            widget_type = getattr(tk, widget_type)

        # Create the widget with provided parameters
        widget = widget_type(self.root, **kwargs)

        # Apply color scheme if available
        if widget.winfo_class() in self.color_schemes:
            color_scheme = self.color_schemes[widget.winfo_class()]
            bg_color = color_scheme.get("background-color", "")
            fg_color = color_scheme.get("foreground-color", "")
            if bg_color:
                widget.config(bg=bg_color)
            if fg_color:
                widget.config(fg=fg_color)

        # Pack the widget into the window
        widget.pack()

        # Return the created widget
        return widget

    def run(self):
        self.root.mainloop()
