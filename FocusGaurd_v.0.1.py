import os
import json
import time
import psutil
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

class FocusGuard:
    def __init__(self):
        self.app_name = ""
        self.time_limit = 900  # 15 minutes in seconds
        self.log_file = "app_usage_log.json"
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("FocusGuard")
        self.root.geometry("400x300")
        
        tk.Label(self.root, text="FocusGuard", font=("Arial", 16)).pack(pady=10)
        
        self.app_entry = tk.Entry(self.root, width=30)
        self.app_entry.pack(pady=5)
        tk.Label(self.root, text="Enter app name (e.g., chrome.exe, notepad.exe)").pack()
        
        self.time_label = tk.Label(self.root, text="Time remaining: 15:00", font=("Arial", 14))
        self.time_label.pack(pady=20)
        
        self.start_button = tk.Button(self.root, text="Start Session", command=self.start_session)
        self.start_button.pack(pady=10)
        
        self.view_logs_button = tk.Button(self.root, text="View Usage Logs", command=self.view_logs)
        self.view_logs_button.pack(pady=5)
        
        self.root.mainloop()
    
    def start_session(self):
        self.app_name = self.app_entry.get()
        if not self.app_name:
            messagebox.showerror("Error", "Please enter an app name")
            return
            
        purpose = simpledialog.askstring("Purpose", "Why are you using this app? (This will be logged)")
        if not purpose:
            messagebox.showinfo("Info", "Session cancelled")
            return
            
        self.log_session(purpose, "started")
        messagebox.showinfo("Info", f"App will close automatically after 15 minutes\nPurpose: {purpose}")
        
        self.start_countdown()
        self.monitor_app()
    
    def start_countdown(self):
        remaining = self.time_limit
        while remaining > 0:
            mins, secs = divmod(remaining, 60)
            self.time_label.config(text=f"Time remaining: {mins:02d}:{secs:02d}")
            self.root.update()
            time.sleep(1)
            remaining -= 1
        
        self.close_app()
    
    def close_app(self):
        for proc in psutil.process_iter():
            try:
                if proc.name().lower() == self.app_name.lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        self.log_session("", "closed")
        messagebox.showinfo("Info", f"{self.app_name} has been closed")
        self.time_label.config(text="Time remaining: 15:00")
    
    def monitor_app(self):
        """Check periodically if the app is running"""
        while True:
            app_running = any(proc.name().lower() == self.app_name.lower() for proc in psutil.process_iter())
            if not app_running:
                self.log_session("", "closed early")
                self.time_label.config(text="Time remaining: 15:00")
                break
            time.sleep(5)
    
    def log_session(self, purpose, action):
        """Log app usage with timestamp and purpose"""
        log_entry = {
            "app": self.app_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "purpose": purpose
        }
        
        logs = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        
        logs.append(log_entry)
        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=2)
    
    def view_logs(self):
        """Display usage logs"""
        if not os.path.exists(self.log_file):
            messagebox.showinfo("Logs", "No logs available yet")
            return
            
        with open(self.log_file, "r") as f:
            logs = json.load(f)
        
        log_text = "\n".join(
            f"{log['timestamp']} - {log['app']}: {log['action']} ({log['purpose']})"
            for log in logs[-10:]  # Show last 10 entries
        )
        messagebox.showinfo("Usage Logs", log_text or "No logs available")

if __name__ == "__main__":
    FocusGuard()

## How to Use This App

''' 1. Change self.time_limit to adjust the duration (in seconds)
    2. Modify the log file location by changing self.log_file
    3. Adjust the GUI size and elements as needed'''
    3. Adjust the GUI size and elements as needed'''