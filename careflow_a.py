import sys
import pyautogui
import time
import re
from threading import Thread
import tkinter as tk
from tkinter import scrolledtext
import pygetwindow as gw
from openai import OpenAI
from dotenv import load_dotenv
import os
import io
import base64
import json
import ctypes

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
load_dotenv()
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# We will handle FailSafe manually in the click function
pyautogui.FAILSAFE = True 
pyautogui.PAUSE = 0.5

# ---------------------------------------------------------
# 👇 YOUR COORDINATES (Keep these!)
# ---------------------------------------------------------
MANUAL_MAP = {
    # PATIENTS
    "Diana Rossi":    (320, 425),
    "Elena Martinez": (333, 503),

    # TABS
    "Summary":        (366, 275),
    "Consultations":  (702, 268),
    "Medications":    (957, 270),
    "Labs":           (1249, 267),
    "Imaging":        (1531, 503)
}
# ---------------------------------------------------------

class CareflowHybridAgent:
    def __init__(self):
        self.is_running = False
        self.chat_window = None
        self.screen_w, self.screen_h = pyautogui.size()
        
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ ERROR: OPENAI_API_KEY missing in .env")
            sys.exit(1)
            
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Ensure we only look for tabs that exist in your map
        self.tabs = ["Summary", "Consultations", "Medications"]

    # ==========================================
    # 🖥️ GUI
    # ==========================================
    def create_chat_window(self):
        self.chat_window = tk.Tk()
        self.chat_window.title("Careflow AI (Safe Mode)")
        self.chat_window.geometry("500x600")
        self.chat_window.attributes('-topmost', True)
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_window, wrap=tk.WORD, width=55, height=25,
            state='disabled', font=('Consolas', 9)
        )
        self.chat_display.pack(padx=10, pady=10)
        
        input_frame = tk.Frame(self.chat_window)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.chat_input = tk.Entry(input_frame, width=42)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_input.bind('<Return>', lambda e: self.process_command())
        
        send_btn = tk.Button(input_frame, text="Run", command=self.process_command, bg="#0096D6", fg="white")
        send_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.add_chat_message("System", "🤖 Ready. (Crash Protection: ON)")
        self.chat_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        self.chat_window.mainloop()

    def add_chat_message(self, sender, message):
        if not self.chat_display: return
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {sender}: {message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def process_command(self):
        command = self.chat_input.get().strip()
        if not command: return
        self.chat_input.delete(0, tk.END)
        self.add_chat_message("You", command)
        
        match = re.search(r'(?:get|find|search).*?(?:on|of|for)\s+([a-z\s]+)', command.lower())
        if match:
            patient_name = match.group(1).strip().title()
            Thread(target=self.execute_automation, args=(patient_name,), daemon=True).start()

    def execute_automation(self, patient_name):
        # Focus App
        wins = gw.getWindowsWithTitle("Careflow") or gw.getWindowsWithTitle("Chrome")
        if wins:
            try: wins[0].activate()
            except: pass
            time.sleep(0.5)

        self.get_patient_history(patient_name)

    def get_patient_history(self, patient_name):
        self.add_chat_message("Agent", f"🔍 Locating '{patient_name}'...")

        if patient_name in MANUAL_MAP:
            target_x, target_y = MANUAL_MAP[patient_name]
            self.human_click(target_x, target_y)
            time.sleep(3.0) 
        else:
            self.add_chat_message("System", f"⚠️ Name '{patient_name}' not in MANUAL_MAP. Skipping click.")

        self.gather_data_hybrid(patient_name)

    def gather_data_hybrid(self, patient_name):
        collected_data = {}
        
        for tab in self.tabs:
            self.add_chat_message("Agent", f"➡️ Switching to '{tab}'...")
            
            if tab in MANUAL_MAP:
                tx, ty = MANUAL_MAP[tab]
                self.human_click(tx, ty)
                time.sleep(1.5)
                
                self.add_chat_message("Agent", f"👁️ Reading {tab}...")
                screenshot = self.take_clean_screenshot()
                prompt = f"Extract key medical info from this {tab} screen. Be brief."
                data = self.ask_gpt_vision(screenshot, prompt)
                collected_data[tab] = data
            else:
                self.add_chat_message("System", f"⚠️ Tab '{tab}' not in map. Skipping.")

        self.generate_report(patient_name, collected_data)

    # ==========================================
    # 🛡️ SAFE CLICK FUNCTION (The Fix)
    # ==========================================
    def human_click(self, x, y):
        # Prevent crash if x,y are invalid
        if x <= 0 or y <= 0:
            self.add_log("Error", f"❌ Invalid Coordinates: {x},{y}")
            return
            
        self.add_chat_message("Debug", f"Moving to {x}, {y}")
        
        try:
            # DISABLE FailSafe momentarily so hitting a corner doesn't crash the app
            pyautogui.FAILSAFE = False 
            
            pyautogui.moveTo(x, y, duration=0.6, tween=pyautogui.easeInOutQuad)
            pyautogui.click()
            
            # Re-enable FailSafe
            pyautogui.FAILSAFE = True 
        except Exception as e:
            self.add_chat_message("Error", f"Click failed: {e}")

    def take_clean_screenshot(self):
        if self.chat_window:
            self.chat_window.withdraw()
            self.chat_window.update_idletasks()
            self.chat_window.update()
        time.sleep(0.3)
        shot = pyautogui.screenshot()
        if self.chat_window: self.chat_window.deiconify()
        return shot

    def ask_gpt_vision(self, image, prompt):
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        b64 = base64.b64encode(buffered.getvalue()).decode()
        try:
            return self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]}], max_tokens=400
            ).choices[0].message.content
        except: return "Error reading screen."

    def generate_report(self, name, data):
        self.add_chat_message("Agent", "📝 Compiling Report...")
        full_text = "\n".join([f"## {k}\n{v}" for k,v in data.items()])
        
        if not full_text.strip():
            self.add_chat_message("System", "⚠️ No data collected. Check coordinates.")
            return

        final = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user", "content":f"Summarize for {name}:\n{full_text}"}]
        ).choices[0].message.content
        self.add_chat_message("System", f"✅ REPORT:\n{final}")

if __name__ == "__main__":
    app = CareflowHybridAgent()
    app.create_chat_window()