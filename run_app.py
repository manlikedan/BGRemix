# run_app.py
import subprocess
import sys
import os

def main():
    # The path to your Streamlit script
    script_path = os.path.join(os.path.dirname(__file__), "app.py")
    # Launch streamlit in a subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path])

if __name__ == "__main__":
    main()
