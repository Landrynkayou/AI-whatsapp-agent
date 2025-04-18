import tkinter as tk
from tkinter import messagebox, ttk
import pickle
import json
import random
import pyautogui
import time
import re
import threading
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# ====================== DATABASE SETUP ======================
Base = declarative_base()

class MessageHistory(Base):
    __tablename__ = 'message_history'
    id = Column(Integer, primary_key=True)
    command = Column(Text)
    generated_message = Column(Text)
    recipient = Column(String(100))
    category = Column(String(50))
    sent_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='pending')

class UserSettings(Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True)
    default_delay = Column(Float, default=1.0)
    retry_count = Column(Integer, default=3)
    theme = Column(String(20), default='light')

class CustomTemplates(Base):
    __tablename__ = 'custom_templates'
    id = Column(Integer, primary_key=True)
    category = Column(String(50))
    template_text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# Initialize database
engine = create_engine('sqlite:///whatsapp_agent.db')
Session = sessionmaker(bind=engine)

def initialize_database():
    Base.metadata.create_all(engine)
    session = Session()
    
    if not session.query(UserSettings).first():
        session.add(UserSettings())
    
    if not session.query(CustomTemplates).first():
        session.add_all([
            CustomTemplates(category='love', template_text="Hey {name}, thinking of you today ❤️"),
            CustomTemplates(category='apology', template_text="Hi {name}, I owe you an apology...")
        ])
    
    session.commit()
    session.close()

initialize_database()

# ====================== CORE FUNCTIONALITY ======================
# Load model and templates
with open("model_pipeline.pkl", "rb") as f:
    model_pipeline = pickle.load(f)

with open("categories.json", "r", encoding='utf-8') as f:
    templates = json.load(f)

class AdvancedNameExtractor:
    def __init__(self):
        self.patterns = [
            r'(?:send|text|message|tell|say|write|wish|remind|ask)\s+(?:a|an|my)?\s*(?:[\w\s]+?)\s+(?:to|for)\s+([A-Z][a-z]*(?:\s[A-Z][a-z]*)*)',
            r'(?:to|for)\s+([A-Z][a-z]*(?:\s[A-Z][a-z]*)*)',
            r'(?:my|your)\s+([a-z]+\s*[a-z]*)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        ]
        
    def extract(self, text):
        for pattern in self.patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                return self.clean_name(name)
        return "Friend"
    
    def clean_name(self, name):
        name = re.sub(r"'s$", "", name)
        name = ' '.join([part.capitalize() for part in name.split()])
        name = re.sub(r'[^a-zA-Z\s]', '', name)
        return name.strip() or "Friend"

name_extractor = AdvancedNameExtractor()

# ====================== WHATSAPP AUTOMATION ======================
class WhatsAppAutomation:
    def __init__(self):
        self.is_running = False
        session = Session()
        settings = session.query(UserSettings).first()
        session.close()
        self.retry_count = settings.retry_count
        self.delay_between_actions = settings.default_delay
        
    def send_message(self, contact_name, message):
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
        pyautogui.hotkey('win', 's')
        time.sleep(self.delay_between_actions)
        pyautogui.write('WhatsApp', interval=0.1)
        time.sleep(self.delay_between_actions)
        pyautogui.press('enter')
        time.sleep(7)
        
    def _search_contact(self, name):
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(self.delay_between_actions)
        pyautogui.write(name, interval=0.2)
        time.sleep(1.5)
        pyautogui.press('tab')
        time.sleep(self.delay_between_actions)
        pyautogui.press('enter')
        time.sleep(2)
        
    def _type_and_send(self, message):
        pyautogui.write(message, interval=0.05)
        time.sleep(1)
        pyautogui.press('enter')
        
    def _recover_from_error(self):
        pyautogui.hotkey('alt', 'f4')
        time.sleep(2)

whatsapp = WhatsAppAutomation()

# ====================== MESSAGE PROCESSING ======================
def preprocess_with_context(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def get_merged_templates():
    merged = templates.copy()
    session = Session()
    custom_templates = session.query(CustomTemplates).all()
    session.close()
    
    for ct in custom_templates:
        if ct.category in merged:
            merged[ct.category].append(ct.template_text)
        else:
            merged[ct.category] = [ct.template_text]
    return merged

def select_most_relevant_template(command, category):
    available_templates = get_merged_templates()[category]
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

def generate_message(command):
    try:
        processed_command = preprocess_with_context(command)
        category = model_pipeline.predict([processed_command])[0]
        
        if category not in get_merged_templates():
            raise ValueError(f"Unknown category: {category}")
            
        name = name_extractor.extract(command)
        template = select_most_relevant_template(command, category)
        message = template.format(name=name)
        
        return message, name, category
        
    except Exception as e:
        error_msg = f"Error generating message: {str(e)}"
        return error_msg, "Error", "error"

# ====================== DATABASE OPERATIONS ======================
def log_message(command, message, recipient, category, status='pending'):
    session = Session()
    try:
        msg = MessageHistory(
            command=command,
            generated_message=message,
            recipient=recipient,
            category=category,
            status=status
        )
        session.add(msg)
        session.commit()
        return msg.id
    except SQLAlchemyError as e:
        session.rollback()
        raise
    finally:
        session.close()

def update_message_status(msg_id, status):
    session = Session()
    try:
        msg = session.query(MessageHistory).get(msg_id)
        if msg:
            msg.status = status
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise
    finally:
        session.close()

def get_message_history(limit=50):
    session = Session()
    try:
        return session.query(MessageHistory)\
            .order_by(MessageHistory.sent_at.desc())\
            .limit(limit)\
            .all()
    finally:
        session.close()

# ====================== GUI FUNCTIONS ======================
def show_history():
    history_window = tk.Toplevel(root)
    history_window.title("Message History")
    history_window.geometry("800x500")
    
    tree = ttk.Treeview(history_window, columns=('time', 'recipient', 'category', 'status', 'preview'), show='headings')
    tree.heading('time', text='Time')
    tree.heading('recipient', text='Recipient')
    tree.heading('category', text='Category')
    tree.heading('status', text='Status')
    tree.heading('preview', text='Preview')
    
    scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    tree.pack(fill='both', expand=True)
    
    for msg in get_message_history():
        preview = msg.generated_message[:50] + "..." if len(msg.generated_message) > 50 else msg.generated_message
        tree.insert('', tk.END, values=(
            msg.sent_at.strftime("%Y-%m-%d %H:%M"),
            msg.recipient,
            msg.category,
            msg.status,
            preview
        ))
    
    def on_double_click(event):
        item = tree.selection()[0]
        values = tree.item(item, 'values')
        messagebox.showinfo(
            "Message Details",
            f"Time: {values[0]}\nRecipient: {values[1]}\n\n{values[4]}",
            parent=history_window
        )
    
    tree.bind("<Double-1>", on_double_click)

def show_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x300")
    
    session = Session()
    settings = session.query(UserSettings).first()
    session.close()
    
    ttk.Label(settings_window, text="Default Delay (seconds):").pack(pady=(10, 0))
    delay_var = tk.DoubleVar(value=settings.default_delay)
    ttk.Entry(settings_window, textvariable=delay_var).pack()
    
    ttk.Label(settings_window, text="Retry Count:").pack(pady=(10, 0))
    retry_var = tk.IntVar(value=settings.retry_count)
    ttk.Entry(settings_window, textvariable=retry_var).pack()
    
    def save_settings():
        session = Session()
        try:
            settings = session.query(UserSettings).first()
            settings.default_delay = delay_var.get()
            settings.retry_count = retry_var.get()
            session.commit()
            messagebox.showinfo("Saved", "Settings updated successfully", parent=settings_window)
            settings_window.destroy()
        except SQLAlchemyError as e:
            session.rollback()
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}", parent=settings_window)
        finally:
            session.close()
    
    ttk.Button(settings_window, text="💾 Save Settings", command=save_settings).pack(pady=20)

def update_output(message, name):
    output_text.config(state='normal')
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"To: {name}\n\n", 'header')
    output_text.insert(tk.END, f"{message}\n\n", 'message')
    output_text.insert(tk.END, "─" * 50 + "\n", 'divider')
    output_text.insert(tk.END, "Tip: You can edit the message before sending!", 'footer')
    output_text.config(state='disabled')

def handle_send():
    command = command_entry.get().strip()
    if not command:
        messagebox.showwarning("Empty Input", "Please enter a command.")
        return
    
    send_button.config(state='disabled', text="Processing...")
    root.update()
    
    def generate_and_display():
        try:
            generated_msg, name, category = generate_message(command)
            
            root.after(0, lambda: update_output(generated_msg, name))
            
            confirm = messagebox.askyesno(
                "Confirm Send",
                f"Send this message to {name}?",
                detail=generated_msg,
                parent=root
            )
            
            if confirm:
                progress = tk.Toplevel(root)
                progress.title("Sending...")
                tk.Label(progress, text=f"Sending to {name}...").pack(pady=10)
                progress_bar = ttk.Progressbar(progress, mode='indeterminate')
                progress_bar.pack(fill='x', padx=20, pady=5)
                progress_bar.start()
                root.update()

                # Log message before sending
                msg_id = log_message(
                    command=command,
                    message=generated_msg,
                    recipient=name,
                    category=category,
                    status='sending'
                )
                
                try:
                    whatsapp.send_message(name, generated_msg)
                    update_message_status(msg_id, 'sent')
                    root.after(0, lambda: messagebox.showinfo(
                        "Success", 
                        f"Message successfully sent to {name}!",
                        parent=root
                    ))
                except Exception as e:
                    update_message_status(msg_id, 'failed')
                    root.after(0, lambda: messagebox.showerror(
                        "Error", 
                        f"Failed to send message: {str(e)}",
                        parent=root
                    ))
                finally:
                    root.after(0, progress.destroy)
                    
        except Exception as e:
            root.after(0, lambda: show_error(f"Error: {str(e)}"))
        finally:
            root.after(0, lambda: send_button.config(state='normal', text="✨ Generate & Send"))
    
    threading.Thread(target=generate_and_display, daemon=True).start()

def show_error(message):
    messagebox.showerror("Error", message, parent=root)

# ====================== MAIN GUI ======================
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
title = ttk.Label(main_frame, text="AI WhatsApp Assistant Pro", font=FONT_MAIN, foreground=PRIMARY_COLOR)
title.pack(pady=(0, 15))

# Input frame
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill='x', pady=5)

ttk.Label(input_frame, text="Enter your message command:", font=("Segoe UI", 10)).pack(anchor='w')

command_entry = ttk.Entry(input_frame, font=FONT_INPUT, width=50)
command_entry.pack(fill='x', pady=5)
command_entry.insert(0, "Send a birthday message to Daniel")

# Buttons
button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=10)

send_button = ttk.Button(button_frame, text="✨ Generate & Send", command=handle_send, style='TButton')
send_button.pack(side='left', padx=5)

history_button = ttk.Button(button_frame, text="📜 History", command=show_history, style='TButton')
history_button.pack(side='left', padx=5)

settings_button = ttk.Button(button_frame, text="⚙️ Settings", command=show_settings, style='TButton')
settings_button.pack(side='left', padx=5)

# Output frame
output_frame = ttk.LabelFrame(main_frame, text="Generated Message", padding=10)
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
status_bar = ttk.Label(main_frame, text="Ready", relief='sunken', anchor='w', font=("Segoe UI", 9))
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

# Start the application
root.mainloop()