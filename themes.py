class Theme:
    def __init__(self, bg, fg, text_bg, text_fg, button_bg, button_fg, highlight_bg, highlight_fg):
        self.bg = bg
        self.fg = fg
        self.text_bg = text_bg
        self.text_fg = text_fg
        self.button_bg = button_bg
        self.button_fg = button_fg
        self.highlight_bg = highlight_bg
        self.highlight_fg = highlight_fg

light_theme = Theme(
    bg="#f0f0f0",
    fg="#000000",
    text_bg="#ffffff",
    text_fg="#000000",
    button_bg="#e0e0e0",
    button_fg="#000000",
    highlight_bg="#d0d0d0",
    highlight_fg="#000000"
)

dark_theme = Theme(
    bg="#2c2c2c",
    fg="#e0e0e0",
    text_bg="#333333",
    text_fg="#e0e0e0",
    button_bg="#3c3c3c",
    button_fg="#e0e0e0",
    highlight_bg="#4c4c4c",
    highlight_fg="#ffffff"
)