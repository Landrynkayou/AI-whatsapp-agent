import tkinter as tk
from tkinter import messagebox
import pickle, json
import random
import pyautogui
import time
import re
import threading

# Load model, vectorizer, and templates
with open("generator.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("categories.json", "r", encoding='utf-8') as f:
    templates = json.load(f)

# Improved name extraction using regex
def extract_name(text):
    match = re.search(r'\bto\s+([A-Za-z]+)', text)
    return match.group(1) if match else "Friend"

# Generate message with fallback
def generate_message(command):
    try:
        X_vect = vectorizer.transform([command])
        category = model.predict(X_vect)[0]
        if category in templates:
            name = extract_name(command)
            template = random.choice(templates[category])
            return template.format(name=name)
        else:
            return "Sorry, I couldn't understand that."
    except Exception as e:
        return f"Error generating message: {e}"

# Message sending function
def send_message(original_msg, generated_msg):
    try:
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.write('WhatsApp', interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')  # Launch WhatsApp
        time.sleep(7)

        pyautogui.hotkey('ctrl', 'f')
        time.sleep(1)

        name = extract_name(original_msg)
        pyautogui.write(name, interval=0.5)
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        pyautogui.write(generated_msg, interval=0.1)
        time.sleep(3)
        pyautogui.press('enter')

        messagebox.showinfo("Success", f"Message sent to {name}!")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# Thread handler
def handle_send():
    command = entry.get()
    if not command.strip():
        messagebox.showwarning("Empty Input", "Please enter a command.")
        return

    try:
        msg = generate_message(command)
        output_text.config(state='normal')
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"Generated Message:\n{msg}")
        output_text.config(state='disabled')
        threading.Thread(target=send_message, args=(command, msg), daemon=True).start()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

# GUI setup
root = tk.Tk()
root.title("💬 AI WhatsApp Agent")
root.geometry("500x420")
root.config(bg="#f0f4ff")

title = tk.Label(root, text="AI WhatsApp Agent", font=("Helvetica", 20, "bold"), bg="#f0f4ff", fg="#4a4aff")
title.pack(pady=20)

entry = tk.Entry(root, font=("Helvetica", 14), width=40)
entry.pack(pady=10)
entry.insert(0, "Send a birthday message to Daniel")

send_btn = tk.Button(root, text="Send Message", command=handle_send, font=("Helvetica", 12), bg="#4a4aff", fg="white", width=20)
send_btn.pack(pady=15)

output_text = tk.Text(root, height=5, width=50, font=("Helvetica", 12), state='disabled', wrap='word')
output_text.pack(pady=10)

note = tk.Label(root, text="⚠️ Ensure WhatsApp Desktop is running and logged in.", bg="#f0f4ff", fg="gray", font=("Helvetica", 10))
note.pack(pady=5)

root.mainloop()
