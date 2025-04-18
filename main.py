import tkinter as tk
from tkinter import messagebox, ttk
import pickle
import json
import random
import pyautogui
import time
import re
import threading
from pathlib import Path
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from sklearn.base import BaseEstimator, TransformerMixin

# Download NLTK data (only needed once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

# Enhanced model and template loading with error handling
def load_resources():
    """Load model and templates with proper error handling"""
    resources = {}
    try:
        with open("model_pipeline.pkl", "rb") as f:
            resources['model'] = pickle.load(f)
        with open("categories.json", "r", encoding='utf-8') as f:
            resources['templates'] = json.load(f)
        return resources
    except FileNotFoundError as e:
        messagebox.showerror("Missing Files", f"Required files not found: {e}")
        raise
    except Exception as e:
        messagebox.showerror("Loading Error", f"Error loading resources: {e}")
        raise

resources = load_resources()
model_pipeline = resources['model']
templates = resources['templates']

class AdvancedNameExtractor:
    """Enhanced name extraction using patterns and NLTK"""
    def __init__(self):
        self.patterns = [
            r'(?:send|text|message|tell|say|write|wish|remind|ask)\s+(?:a|an|my)?\s*(?:[\w\s]+?)\s+(?:to|for)\s+([A-Z][a-z]*(?:\s[A-Z][a-z]*)*)',
            r'(?:to|for)\s+([A-Z][a-z]*(?:\s[A-Z][a-z]*)*)',
            r'(?:my|your)\s+([a-z]+\s*[a-z]*)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        ]
        
    def extract(self, text):
        """Extract name using multiple strategies"""
        # Try patterns first
        for pattern in self.patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                return self.clean_name(name)
        
        # Fall back to NLTK POS tagging
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        
        # Look for proper nouns (NNP)
        names = [word for word, pos in tagged if pos == 'NNP']
        if names:
            return self.clean_name(' '.join(names))
        
        return "Friend"
    
    def clean_name(self, name):
        """Clean and format the extracted name"""
        name = re.sub(r"'s$", "", name)
        name = ' '.join([part.capitalize() for part in name.split()])
        name = re.sub(r'[^a-zA-Z\s]', '', name)
        return name.strip() or "Friend"

name_extractor = AdvancedNameExtractor()

class ContextEnhancer(BaseEstimator, TransformerMixin):
    """Custom transformer to enhance context understanding"""
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return [self._enhance_text(text) for text in X]
    
    def _enhance_text(self, text):
        """Add contextual clues to the text"""
        enhanced = text.lower()
        
        # Add sentiment clues
        if any(word in enhanced for word in ['sorry', 'apologize', 'regret']):
            enhanced += " apology"
        if any(word in enhanced for word in ['love', 'miss you', 'adore']):
            enhanced += " love"
        if 'birthday' in enhanced:
            enhanced += " birthday celebration"
            
        return enhanced

def generate_message(command):
    """Generate context-aware message with improved error handling"""
    try:
        # Preprocess and predict
        processed_command = preprocess_with_context(command)
        category = model_pipeline.predict([processed_command])[0]
        
        if category not in templates:
            raise ValueError(f"Unknown category: {category}")
            
        name = name_extractor.extract(command)
        template = select_most_relevant_template(command, category)
        message = template.format(name=name)
        
        return message, name
        
    except Exception as e:
        error_msg = f"Error generating message: {str(e)}"
        return error_msg, "Error"

def preprocess_with_context(text):
    """Enhanced preprocessing with context preservation"""
    # Keep important context markers
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation but keep words
    return text

def select_most_relevant_template(command, category):
    """Select template that best matches the command context"""
    available_templates = templates[category]
    
    # Simple keyword matching for now - could be enhanced with embeddings
    command_words = set(preprocess_with_context(command).split())
    
    best_score = -1
    best_template = available_templates[0]
    
    for template in available_templates:
        template_words = set(preprocess_with_context(template).split())
        score = len(command_words.intersection(template_words))
        if score > best_score:
            best_score = score
            best_template = template
    
    return best_template

class WhatsAppAutomation:
    """Robust WhatsApp automation with state tracking"""
    def __init__(self):
        self.is_running = False
        self.retry_count = 3
        self.delay_between_actions = 1.0
        
    def send_message(self, contact_name, message):
        """Send message with error recovery"""
        if self.is_running:
            raise Exception("Another operation is already in progress")
            
        self.is_running = True
        try:
            self._open_whatsapp()
            self._search_contact(contact_name)
            self._type_and_send(message)
            return True
        except Exception as e:
            for _ in range(self.retry_count):
                try:
                    self._recover_from_error()
                    self._open_whatsapp()
                    self._search_contact(contact_name)
                    self._type_and_send(message)
                    return True
                except:
                    continue
            raise
        finally:
            self.is_running = False
    
    def _open_whatsapp(self):
        """Open WhatsApp desktop app"""
        pyautogui.hotkey('win', 's')
        time.sleep(self.delay_between_actions)
        pyautogui.write('WhatsApp', interval=0.1)
        time.sleep(self.delay_between_actions)
        pyautogui.press('enter')
        time.sleep(7)  # Wait for app to load
        
    def _search_contact(self, name):
        """Search for contact"""
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(self.delay_between_actions)
        pyautogui.write(name, interval=0.2)
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(self.delay_between_actions)
        pyautogui.press('enter')
        time.sleep(2)
        
    def _type_and_send(self, message):
        """Type and send message"""
        pyautogui.write(message, interval=0.05)
        time.sleep(1)
        pyautogui.press('enter')
        
    def _recover_from_error(self):
        """Attempt to recover from error state"""
        pyautogui.hotkey('alt', 'f4')
        time.sleep(2)

whatsapp = WhatsAppAutomation()

def handle_send():
    """Handle send button click with improved UX"""
    command = command_entry.get().strip()
    if not command:
        messagebox.showwarning("Empty Input", "Please enter a command.")
        return
    
    # Update UI to show processing
    send_button.config(state='disabled', text="Processing...")
    root.update()
    
    try:
        # Generate message in a separate thread to keep UI responsive
        def generate_and_display():
            try:
                generated_msg, name = generate_message(command)
                
                # Update UI on main thread
                root.after(0, lambda: update_output(generated_msg, name))
                
                # Ask for confirmation
                root.after(0, lambda: confirm_send(generated_msg, name))
                
            except Exception as e:
                root.after(0, lambda: show_error(f"Generation error: {str(e)}"))
            finally:
                root.after(0, lambda: send_button.config(state='normal', text="✨ Generate & Send"))
        
        threading.Thread(target=generate_and_display, daemon=True).start()
        
    except Exception as e:
        show_error(f"Error: {str(e)}")
        send_button.config(state='normal', text="✨ Generate & Send")

def update_output(message, name):
    """Update the output text widget"""
    output_text.config(state='normal')
    output_text.delete(1.0, tk.END)
    
    # Format the output nicely
    output_text.insert(tk.END, f"To: {name}\n\n", 'header')
    output_text.insert(tk.END, f"{message}\n\n", 'message')
    
    # Add metadata
    output_text.insert(tk.END, "─" * 50 + "\n", 'divider')
    output_text.insert(tk.END, "Tip: You can edit the message before sending!", 'footer')
    
    output_text.config(state='disabled')

def confirm_send(message, name):
    """Ask for confirmation before sending"""
    confirm = messagebox.askyesno(
        "Confirm Send",
        f"Send this message to {name}?",
        detail=message,
        icon='question'
    )
    
    if confirm:
        # Show sending progress
        progress = tk.Toplevel(root)
        progress.title("Sending...")
        progress.geometry("300x100")
        tk.Label(progress, text=f"Sending to {name}...").pack(pady=10)
        progress_bar = ttk.Progressbar(progress, mode='indeterminate')
        progress_bar.pack(fill='x', padx=20, pady=5)
        progress_bar.start()
        root.update()
        
        def send_in_thread():
            try:
                whatsapp.send_message(name, message)
                root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Message successfully sent to {name}!",
                    parent=root
                ))
            except Exception as e:
                root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    f"Failed to send message: {str(e)}",
                    parent=root
                ))
            finally:
                root.after(0, progress.destroy)
        
        threading.Thread(target=send_in_thread, daemon=True).start()

def show_error(message):
    """Show error message"""
    messagebox.showerror("Error", message, parent=root)

# Setup modern UI
root = tk.Tk()
root.title("AI WhatsApp Agent Pro")
root.geometry("600x500")
root.resizable(True, True)
root.configure(bg="#f5f7ff")

# Fonts and styles
FONT_MAIN = ("Segoe UI", 18, "bold")
FONT_INPUT = ("Segoe UI", 12)
FONT_OUTPUT = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 12, "bold")

style = ttk.Style()
style.configure('TButton', font=FONT_BUTTON, padding=6)
style.configure('TEntry', font=FONT_INPUT, padding=5)

# Colors
PRIMARY_COLOR = "#5e72e4"
SECONDARY_COLOR = "#f7fafc"
TEXT_COLOR = "#2d3748"

# Main container
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill='both', expand=True)

# Title
title = ttk.Label(
    main_frame, 
    text="AI WhatsApp Assistant Pro", 
    font=FONT_MAIN, 
    foreground=PRIMARY_COLOR
)
title.pack(pady=(0, 15))

# Input frame
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill='x', pady=5)

ttk.Label(
    input_frame, 
    text="Enter your message command:", 
    font=("Segoe UI", 10)
).pack(anchor='w')

command_entry = ttk.Entry(
    input_frame, 
    font=FONT_INPUT, 
    width=50
)
command_entry.pack(fill='x', pady=5)
command_entry.insert(0, "Send a birthday message to Daniel")

# Button
send_button = ttk.Button(
    main_frame, 
    text="✨ Generate & Send", 
    command=handle_send, 
    style='TButton'
)
send_button.pack(pady=10)

# Output frame
output_frame = ttk.LabelFrame(
    main_frame, 
    text="Generated Message", 
    padding=10
)
output_frame.pack(fill='both', expand=True, pady=5)

output_text = tk.Text(
    output_frame, 
    height=10, 
    width=60, 
    font=FONT_OUTPUT, 
    wrap='word', 
    padx=10, 
    pady=10,
    bg=SECONDARY_COLOR,
    fg=TEXT_COLOR,
    relief='flat'
)
output_text.pack(fill='both', expand=True)

# Configure text tags
output_text.tag_configure('header', font=("Segoe UI", 11, "bold"))
output_text.tag_configure('message', foreground="#4a5568")
output_text.tag_configure('divider', foreground="#cbd5e0")
output_text.tag_configure('footer', font=("Segoe UI", 9), foreground="#718096")

# Status bar
status_bar = ttk.Label(
    main_frame, 
    text="Ready", 
    relief='sunken', 
    anchor='w',
    font=("Segoe UI", 9)
)
status_bar.pack(fill='x', pady=(5, 0))

# Tooltip
tooltip = ttk.Label(
    main_frame, 
    text="Tip: You can say things like 'Tell John I miss him' or 'Wish happy birthday to Sarah'",
    font=("Segoe UI", 9),
    foreground="#718096",
    wraplength=500
)
tooltip.pack(fill='x', pady=(5, 0))

# Start the UI
root.mainloop()