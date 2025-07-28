##Jarvis AI Assistant - Setup Guide
This file explains how to install and run Jarvis AI Assistant.

Prerequisites
Windows 10/11 machine (64-bit)
Microphone and speakers/headset
Python 3.8 – 3.12 installed and added to PATH
Internet connection (for weather, speech recognition)
OpenWeatherMap API KEY (free tier) – https://openweathermap.org/api
1. Clone/Download the Folder
# Using Git
git clone <repository-url>
cd jarvis-ai
Or download the zip, extract and open a terminal inside the folder.

2. Create Virtual Environment (recommended)
python -m venv venv
venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
If you encounter audio driver errors, also install:

pip install pyaudio
4. Add Your Weather API Key
Open jarvis_ai.py and replace:

self.weather_api_key = "YOUR_OPENWEATHER_API_KEY"
with your actual key.

5. First Run (development mode)
python jarvis_ai.py
Jarvis starts, greets you and shows a modern GUI. Press Start Listening and speak.

6. Build Stand-Alone EXE (optional)
Install PyInstaller once:

pip install pyinstaller
Build single-file executable:

pyinstaller --noconsole --onefile --icon=NONE jarvis_ai.py
The EXE appears in the dist directory. Copy the dist/jarvis_ai.exe anywhere.

7. Auto-Start on Boot
Inside Jarvis click Settings → Add to Startup or run:

python -c "import jarvis_ai as j; print(j.JarvisAI().add_to_startup())"
8. Voice Commands (examples)
Category	Example	Effect
Greet	"Hi Jarvis"	Responds
Time	"What’s the time?"	Current time
Date	"What’s today’s date?"	Current date
Weather	"What’s the weather like?"	Tiruvallur weather
App	"Open notepad"	Launches Notepad
Web	"Search YouTube for lo-fi music"	Opens browser
System	"Shutdown"	Shuts down PC
Exit	"Bye Jarvis"	Closes assistant
9. Packaging Tips
• Add your own icons inside create_system_tray() • Extend open_application() dictionary with paths of favorite apps. • To change female → male voice set voices[0].id.

Troubleshooting
• Microphone not detected – check Windows privacy settings. • “Could not request results” – internet connectivity or Google speech API quota. • Weather returns error – ensure correct API key & city spelling.

Enjoy your personal JARVIS-like assistant!
