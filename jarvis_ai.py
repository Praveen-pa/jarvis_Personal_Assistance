
import speech_recognition as sr
import pyttsx3
import datetime
import os
import webbrowser
import subprocess
import requests
import json
import threading
import time
import customtkinter as ctk
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
import sys
from pathlib import Path
import winreg
import getpass

class JarvisAI:
    def __init__(self):
        self.engine = pyttsx3.init('sapi5')
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Configure voice settings
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)  # Female voice
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('volume', 0.9)

        # Weather API key (Free tier from OpenWeatherMap)
        self.weather_api_key = "YOUR_OPENWEATHER_API_KEY"  # User needs to get this

        # Initialize GUI
        self.setup_gui()

        # Check if first run today
        self.is_first_run_today = self.check_first_run_today()

        # Start in system tray
        self.create_system_tray()

    def setup_gui(self):
        """Setup the modern GUI using CustomTkinter"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Jarvis AI Assistant")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="JARVIS AI Assistant", 
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.title_label.pack(pady=20)

        # Status display
        self.status_label = ctk.CTkLabel(
            self.main_frame, 
            text="Ready to assist...", 
            font=ctk.CTkFont(size=16)
        )
        self.status_label.pack(pady=10)

        # Log display
        self.log_text = ctk.CTkTextbox(
            self.main_frame, 
            height=300, 
            width=700,
            font=ctk.CTkFont(size=12)
        )
        self.log_text.pack(pady=20, fill="both", expand=True)

        # Control buttons
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20, fill="x")

        self.listen_button = ctk.CTkButton(
            self.button_frame, 
            text="Start Listening", 
            command=self.toggle_listening,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.listen_button.pack(side="left", padx=10)

        self.settings_button = ctk.CTkButton(
            self.button_frame, 
            text="Settings", 
            command=self.open_settings,
            font=ctk.CTkFont(size=14)
        )
        self.settings_button.pack(side="left", padx=10)

        self.minimize_button = ctk.CTkButton(
            self.button_frame, 
            text="Minimize to Tray", 
            command=self.minimize_to_tray,
            font=ctk.CTkFont(size=14)
        )
        self.minimize_button.pack(side="right", padx=10)

        # Listening state
        self.is_listening = False

    def log_message(self, message):
        """Add message to the log display"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")

    def speak(self, text):
        """Convert text to speech"""
        self.log_message(f"Jarvis: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen for user voice input"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.log_message("Listening...")
                self.status_label.configure(text="Listening...")

                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)

                self.log_message("Processing...")
                self.status_label.configure(text="Processing...")

                text = self.recognizer.recognize_google(audio).lower()
                self.log_message(f"You said: {text}")
                return text

        except sr.UnknownValueError:
            self.log_message("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.log_message(f"Error with speech recognition: {e}")
            return None
        except sr.WaitTimeoutError:
            self.log_message("Listening timeout")
            return None

    def get_weather(self, city="Tiruvallur"):
        """Get weather information"""
        if not self.weather_api_key or self.weather_api_key == "YOUR_OPENWEATHER_API_KEY":
            return "Weather API key not configured. Please set your OpenWeatherMap API key."

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=5)
            data = response.json()

            if data["cod"] == 200:
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                return f"The weather in {city} is {description} with temperature {temp} degrees celsius and humidity {humidity} percent"
            else:
                return f"Could not get weather for {city}"
        except Exception as e:
            return f"Error getting weather: {e}"

    def get_current_time(self):
        """Get current time"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The current time is {time_str}"

    def get_current_date(self):
        """Get current date"""
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}"

    def morning_greeting(self):
        """Provide morning greeting with information"""
        now = datetime.datetime.now()
        hour = now.hour

        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # Get location (simplified - using configured location)
        location = "Tiruvallur, Tamil Nadu, India"

        greeting_text = f"{greeting}! Welcome back. I'm Jarvis, your AI assistant."
        greeting_text += f" {self.get_current_date()}. {self.get_current_time()}."
        greeting_text += f" You are in {location}. {self.get_weather()}"

        return greeting_text

    def open_application(self, app_name):
        """Open applications"""
        apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "explorer": "explorer.exe",
            "paint": "mspaint.exe"
        }

        if app_name in apps:
            try:
                subprocess.Popen(apps[app_name])
                return f"Opening {app_name}"
            except Exception as e:
                return f"Could not open {app_name}: {e}"
        else:
            return f"Application {app_name} not found"

    def search_web(self, query, platform="google"):
        """Search the web"""
        if platform == "google":
            url = f"https://www.google.com/search?q={query}"
        elif platform == "youtube":
            url = f"https://www.youtube.com/results?search_query={query}"
        else:
            url = f"https://www.google.com/search?q={query}"

        webbrowser.open(url)
        return f"Searching for {query} on {platform}"

    def file_operations(self, command, filename=None):
        """Handle file operations"""
        if "create" in command and filename:
            try:
                with open(filename, 'w') as f:
                    f.write(f"# Created by Jarvis on {datetime.datetime.now()}\n")
                return f"File {filename} created successfully"
            except Exception as e:
                return f"Error creating file: {e}"

        elif "delete" in command and filename:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                    return f"File {filename} deleted successfully"
                else:
                    return f"File {filename} not found"
            except Exception as e:
                return f"Error deleting file: {e}"

        elif "open" in command and filename:
            try:
                os.startfile(filename)
                return f"Opening {filename}"
            except Exception as e:
                return f"Error opening file: {e}"

        return "Please specify a valid file operation"

    def process_command(self, command):
        """Process voice commands"""
        if not command:
            return

        command = command.lower()

        # Greeting commands
        if any(word in command for word in ["hi", "hello", "hey", "jarvis"]):
            response = "Hello! How can I help you today?"

        # Time and date
        elif "time" in command:
            response = self.get_current_time()
        elif "date" in command:
            response = self.get_current_date()

        # Weather
        elif "weather" in command:
            response = self.get_weather()

        # Open applications
        elif "open" in command:
            if "notepad" in command:
                response = self.open_application("notepad")
            elif "calculator" in command:
                response = self.open_application("calculator")
            elif "chrome" in command:
                response = self.open_application("chrome")
            elif "explorer" in command:
                response = self.open_application("explorer")
            elif "paint" in command:
                response = self.open_application("paint")
            else:
                response = "Please specify which application to open"

        # Web search
        elif "search" in command:
            if "youtube" in command:
                query = command.replace("search", "").replace("youtube", "").strip()
                response = self.search_web(query, "youtube")
            else:
                query = command.replace("search", "").replace("google", "").strip()
                response = self.search_web(query, "google")

        # File operations
        elif any(word in command for word in ["create", "delete", "file"]):
            response = self.file_operations(command)

        # System commands
        elif "shutdown" in command:
            response = "Shutting down the system"
            os.system("shutdown /s /t 1")
        elif "restart" in command:
            response = "Restarting the system"
            os.system("shutdown /r /t 1")

        # Exit commands
        elif any(word in command for word in ["exit", "quit", "bye"]):
            response = "Goodbye! Have a great day!"
            self.speak(response)
            self.root.quit()
            return

        else:
            response = "I'm sorry, I didn't understand that command. Please try again."

        self.speak(response)
        self.status_label.configure(text="Ready to assist...")

    def toggle_listening(self):
        """Toggle listening mode"""
        if not self.is_listening:
            self.is_listening = True
            self.listen_button.configure(text="Stop Listening")
            threading.Thread(target=self.continuous_listening, daemon=True).start()
        else:
            self.is_listening = False
            self.listen_button.configure(text="Start Listening")

    def continuous_listening(self):
        """Continuous listening loop"""
        while self.is_listening:
            command = self.listen()
            if command:
                self.process_command(command)
            time.sleep(1)

    def check_first_run_today(self):
        """Check if this is the first run today"""
        today = datetime.date.today().isoformat()
        log_file = "jarvis_log.txt"

        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                last_run = f.read().strip()
                if last_run == today:
                    return False

        with open(log_file, 'w') as f:
            f.write(today)
        return True

    def startup_routine(self):
        """Run startup routine"""
        if self.is_first_run_today:
            greeting = self.morning_greeting()
            self.speak(greeting)

    def open_settings(self):
        """Open settings dialog"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Jarvis Settings")
        settings_window.geometry("400x300")

        # Weather API key setting
        api_label = ctk.CTkLabel(settings_window, text="OpenWeatherMap API Key:")
        api_label.pack(pady=10)

        api_entry = ctk.CTkEntry(settings_window, placeholder_text="Enter your API key", width=300)
        api_entry.pack(pady=5)

        def save_api_key():
            self.weather_api_key = api_entry.get()
            messagebox.showinfo("Settings", "API key saved successfully!")
            settings_window.destroy()

        save_button = ctk.CTkButton(settings_window, text="Save", command=save_api_key)
        save_button.pack(pady=20)

    def create_system_tray(self):
        """Create system tray icon"""
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')

        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Hide", self.hide_window),
            pystray.MenuItem("Quit", self.quit_application)
        )

        self.icon = pystray.Icon("Jarvis", image, "Jarvis AI Assistant", menu)

    def show_window(self, icon=None, item=None):
        """Show the main window"""
        self.root.deiconify()

    def hide_window(self, icon=None, item=None):
        """Hide the main window"""
        self.root.withdraw()

    def minimize_to_tray(self):
        """Minimize to system tray"""
        self.root.withdraw()
        if not hasattr(self, 'tray_running'):
            self.tray_running = True
            threading.Thread(target=self.icon.run, daemon=True).start()

    def quit_application(self, icon=None, item=None):
        """Quit the application"""
        if hasattr(self, 'icon'):
            self.icon.stop()
        self.root.quit()
        sys.exit()

    def add_to_startup(self):
        """Add Jarvis to Windows startup"""
        try:
            key = winreg.HKEY_CURRENT_USER
            key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"

            open_key = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(open_key, "JarvisAI", 0, winreg.REG_SZ, sys.executable + " " + os.path.abspath(__file__))
            winreg.CloseKey(open_key)

            return "Jarvis added to startup successfully!"
        except Exception as e:
            return f"Error adding to startup: {e}"

    def run(self):
        """Run the application"""
        # Run startup routine
        threading.Thread(target=self.startup_routine, daemon=True).start()

        # Start the GUI
        self.root.mainloop()

if __name__ == "__main__":
    jarvis = JarvisAI()
    jarvis.run()
