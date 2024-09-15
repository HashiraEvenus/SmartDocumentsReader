import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, font, ttk
from tkinter.colorchooser import askcolor
from doc_reader import read_file, save_file, export_to_pdf, export_to_html
import json
import os
from themes import light_theme, dark_theme
import openai
from config import OPENAI_API_KEY
from openai import OpenAI
from pygments import lex
from pygments.lexers import get_lexer_for_filename, guess_lexer, get_lexer_by_name
from pygments.token import Token
from pygments.util import ClassNotFound
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import PanedWindow

class SyntaxHighlightingText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.configure(font=("Courier", 10))
        self.tag_configure("Token.Keyword", foreground="#CC7A00", font=("Courier", 10, "bold"))
        self.tag_configure("Token.String", foreground="#36B300")
        self.tag_configure("Token.Name.Function", foreground="#00A3CC")
        self.tag_configure("Token.Name.Class", foreground="#00A3CC", font=("Courier", 10, "bold"))
        self.tag_configure("Token.Comment", foreground="#919191", font=("Courier", 10, "italic"))
        self.tag_configure("Token.Operator", foreground="#687687")
        self.tag_configure("Token.Number", foreground="#FF00FF")

    def highlight(self, content, lexer=None):
        self.delete(1.0, tk.END)
        if lexer:
            formatter = get_formatter_by_name('text', style='default')
            highlighted = highlight(content, lexer, formatter)
            self.insert(tk.END, highlighted)
            for token, value in lexer.get_tokens(content):
                start = f"1.0 + {len(self.get('1.0', 'end')[:self.search(value, '1.0', 'end')])} chars"
                end = f"{start} + {len(value)} chars"
                self.tag_add(str(token), start, end)
        else:
            self.insert(tk.END, content)

    def clear_highlighting(self):
        for tag in self.tag_names():
            if tag.startswith("Token"):
                self.tag_remove(tag, "1.0", tk.END)

class DocxReaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Reader")
        self.current_file = None
        self.recent_files = self.load_recent_files()
        self.current_theme = dark_theme
        self.create_widgets()
        self.set_document_placeholder()
        self.create_menu()
        self.setup_drag_drop()
        self.apply_theme()
        self.setup_ai()

    def create_widgets(self):
        # Create a main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a toolbar
        self.create_toolbar()

        # Create a frame for text manipulation tools
        tools_frame = ttk.Frame(self.main_frame)
        tools_frame.pack(pady=5, fill=tk.X)

        # Font style dropdown
        self.font_style = tk.StringVar(value="Arial")
        font_styles = ["Arial", "Times New Roman", "Courier"]
        font_style_menu = ttk.OptionMenu(tools_frame, self.font_style, "Arial", *font_styles, command=self.change_font)
        font_style_menu.pack(side=tk.LEFT, padx=5)

        # Font size dropdown
        self.font_size = tk.StringVar(value="12")
        font_size_menu = ttk.OptionMenu(tools_frame, self.font_size, "12", "8", "10", "12", "14", "16", "18", "20", command=self.change_font)
        font_size_menu.pack(side=tk.LEFT, padx=5)

        # Color chooser button
        color_button = ttk.Button(tools_frame, text="Text Color", command=self.choose_color)
        color_button.pack(side=tk.LEFT, padx=5)

        # Create a paned window to hold the text area and AI suggestions
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Create a frame for the document content
        doc_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(doc_frame, weight=60)

        # Add a label for the document content
        doc_label = ttk.Label(doc_frame, text="Document Content", font=("Arial", 12, "bold"))
        doc_label.pack(pady=(0, 5))

        # Create a scrolled text area to display the document content
        self.text_area = SyntaxHighlightingText(doc_frame, wrap=tk.WORD, font=("Arial", 12))
        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.text_area.tag_configure("placeholder", foreground="gray")

        # Create a frame for AI suggestions
        ai_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(ai_frame, weight=40)

        # Add a label for the AI conversation
        ai_label = ttk.Label(ai_frame, text="Conversation", font=("Arial", 12, "bold"))
        ai_label.pack(pady=(0, 5))

        # Create a scrolled text area for AI suggestions
        self.ai_suggestion_area = SyntaxHighlightingText(ai_frame, wrap=tk.WORD)
        self.ai_suggestion_area.insert(tk.END, "Hello, I am your AI assistant. How can I help you today?")
        self.ai_suggestion_area.config(state=tk.DISABLED)
        self.ai_suggestion_area.pack(expand=True, fill=tk.BOTH)

        # Replace the search frame with a prompt frame
        prompt_frame = ttk.Frame(self.main_frame)
        prompt_frame.pack(pady=5, fill=tk.X)

        # Create a Text widget for the prompt instead of Entry
        self.prompt_text = tk.Text(prompt_frame, wrap=tk.WORD, height=3, font=("Arial", 11))
        self.prompt_text.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        send_button = ttk.Button(prompt_frame, text="Send", command=self.send_prompt)
        send_button.pack(side=tk.LEFT)

        # Set the initial position of the sash (divider) to 60% of the window width
        self.root.update()  # Ensure the window is drawn before we calculate sizes
        window_width = self.root.winfo_width()
        self.paned_window.sashpos(0, int(window_width * 0.6))

    def create_toolbar(self):
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        open_button = ttk.Button(toolbar, text="Open", command=self.open_file)
        open_button.pack(side=tk.LEFT, padx=2, pady=2)

        save_button = ttk.Button(toolbar, text="Save", command=self.save_file)
        save_button.pack(side=tk.LEFT, padx=2, pady=2)

        theme_button = ttk.Button(toolbar, text="Toggle Theme", command=self.toggle_theme)
        theme_button.pack(side=tk.RIGHT, padx=2, pady=2)

        clear_ai_button = ttk.Button(toolbar, text="Clear AI", command=self.clear_ai_suggestions)
        clear_ai_button.pack(side=tk.LEFT, padx=2, pady=2)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        
        recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=recent_menu)
        self.update_recent_menu(recent_menu)

        file_menu.add_separator()
        file_menu.add_command(label="Export to PDF", command=self.export_to_pdf)
        file_menu.add_command(label="Export to HTML", command=self.export_to_html)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)

    def toggle_theme(self):
        self.current_theme = dark_theme if self.current_theme == light_theme else light_theme
        self.apply_theme()

    def apply_theme(self):
        self.root.configure(bg=self.current_theme.bg)
        self.main_frame.configure(style='TFrame')
        self.text_area.configure(bg=self.current_theme.text_bg, fg=self.current_theme.text_fg)
        self.ai_suggestion_area.configure(bg=self.current_theme.text_bg, fg=self.current_theme.text_fg)
        self.prompt_text.configure(bg=self.current_theme.text_bg, fg=self.current_theme.text_fg)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.current_theme.bg)
        style.configure('TButton', background=self.current_theme.button_bg, foreground=self.current_theme.button_fg)
        style.configure('TEntry', fieldbackground=self.current_theme.text_bg, foreground=self.current_theme.text_fg)
        style.configure('TOptionMenu', background=self.current_theme.button_bg, foreground=self.current_theme.button_fg)
        
        # Configure additional styles for better theme integration
        style.configure('TLabel', background=self.current_theme.bg, foreground=self.current_theme.fg)
        style.configure('TMenubutton', background=self.current_theme.button_bg, foreground=self.current_theme.button_fg)
        style.map('TButton', 
                  background=[('active', self.current_theme.highlight_bg)],
                  foreground=[('active', self.current_theme.highlight_fg)])
        style.map('TMenubutton', 
                  background=[('active', self.current_theme.highlight_bg)],
                  foreground=[('active', self.current_theme.highlight_fg)])
        
        # Configure the sash color to match the theme
        style.configure('TPanedwindow', background=self.current_theme.bg)
        
        # Update menu colors
        self.update_menu_colors()

    def update_menu_colors(self):
        menubar = self.root.nametowidget(self.root.cget("menu"))
        menubar.configure(bg=self.current_theme.button_bg, fg=self.current_theme.button_fg)
        self.update_menu_item_colors(menubar)

    def update_menu_item_colors(self, menu):
        menu.configure(bg=self.current_theme.button_bg, fg=self.current_theme.button_fg)
        for item in menu.winfo_children():
            if isinstance(item, tk.Menu):
                self.update_menu_item_colors(item)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("All Supported Files", "*.docx *.pdf *.txt"),
            ("Word Documents", "*.docx"),
            ("PDF Files", "*.pdf"),
            ("Text Files", "*.txt")
        ])
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        # Remove the placeholder before loading the file
        if self.text_area.get("1.0", "end-1c") == "Open a document or drag and drop a file here...":
            self.text_area.delete("1.0", "end")
            self.text_area.tag_remove("placeholder", "1.0", "end")

        text = read_file(file_path)
        lexer = None
        try:
            lexer = get_lexer_for_filename(file_path)
        except ClassNotFound:
            if file_path.lower().endswith(('.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs', '.ts')):
                try:
                    lexer = guess_lexer(text)
                except ClassNotFound:
                    pass  # If we can't guess, we'll treat it as plain text

        self.text_area.highlight(text, lexer)
        self.current_file = file_path
        self.add_recent_file(file_path)

    def save_file(self):
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("Word Documents", "*.docx")]
            )
        if self.current_file:
            content = self.text_area.get(1.0, tk.END)
            save_file(self.current_file, content)
            messagebox.showinfo("Success", "File saved successfully.")

    def setup_drag_drop(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_file)

    def drop_file(self, event):
        file_path = event.data
        if file_path:
            self.load_file(file_path)

    def change_font(self, *args):
        current_font = font.Font(font=self.text_area['font'])
        current_font.configure(family=self.font_style.get(), size=int(self.font_size.get()))
        self.text_area.configure(font=current_font)

    def choose_color(self):
        color = askcolor()[1]
        if color:
            self.text_area.config(fg=color)

    def export_to_pdf(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file is currently open.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            content = self.text_area.get(1.0, tk.END)
            export_to_pdf(file_path, content)
            messagebox.showinfo("Success", "File exported to PDF successfully.")

    def export_to_html(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file is currently open.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])
        if file_path:
            content = self.text_area.get(1.0, tk.END)
            export_to_html(file_path, content)
            messagebox.showinfo("Success", "File exported to HTML successfully.")

    def load_recent_files(self):
        try:
            with open('recent_files.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_recent_files(self):
        with open('recent_files.json', 'w') as f:
            json.dump(self.recent_files, f)

    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:5]  # Keep only the 5 most recent files
        self.save_recent_files()
        self.update_recent_menu()

    def update_recent_menu(self, menu=None):
        if menu is None:
            menu = self.root.nametowidget(self.root.cget("menu")).nametowidget("File").nametowidget("Recent Files")
        menu.delete(0, tk.END)
        for file_path in self.recent_files:
            menu.add_command(label=os.path.basename(file_path), command=lambda fp=file_path: self.load_file(fp))

    def setup_ai(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def send_prompt(self):
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            return

        document_content = self.text_area.get(1.0, tk.END).strip()
        if document_content == "Open a document or drag and drop a file here...":
            document_content = "No document is currently loaded."

        full_prompt = f"Given the following document content:\n\n{document_content}\n\nUser question: {prompt}\n\nPlease provide a response:"

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions about documents."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=300,
                n=1,
                temperature=0.7,
            )
            ai_response = response.choices[0].message.content.strip()
            
            self.ai_suggestion_area.config(state=tk.NORMAL)
            self.ai_suggestion_area.clear_highlighting()
            self.ai_suggestion_area.delete(1.0, tk.END)
            full_response = f"Q: {prompt}\n\nA: {ai_response}"
            self.ai_suggestion_area.insert(tk.END, full_response)
            # Don't apply syntax highlighting to AI responses
            self.ai_suggestion_area.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Detailed error: {str(e)}")  # This will print the full error to the console
            messagebox.showerror("Error", f"Failed to get AI response: {str(e)}")

        # Clear the prompt text after sending
        self.prompt_text.delete("1.0", tk.END)

    def clear_ai_suggestions(self):
        self.ai_suggestion_area.config(state=tk.NORMAL)
        self.ai_suggestion_area.clear_highlighting()
        self.ai_suggestion_area.delete(1.0, tk.END)
        self.ai_suggestion_area.insert(tk.END, "AI responses will appear here...")
        self.ai_suggestion_area.config(state=tk.DISABLED)

    def set_document_placeholder(self):
        placeholder_text = "Open a document or drag and drop a file here..."
        self.text_area.insert("1.0", placeholder_text)
        self.text_area.tag_add("placeholder", "1.0", "end")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = DocxReaderGUI(root)
    root.geometry("800x600")  # Set initial window size
    root.mainloop()
