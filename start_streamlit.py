#!/usr/bin/env python3
"""
AgriPrice Assistant Streamlit Launcher
Run this file to start the Streamlit app automatically
"""

import os
import sys
import webbrowser
import time
import subprocess
import socket

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("🌾 AgriPrice Assistant Streamlit Launcher")
    print("=" * 50)
    print("🚀 Starting Streamlit application...")

    print("📁 Working directory:", script_dir)
    print()

    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("   Make sure you have created .env with your API keys")
        print()

    # Check if Streamlit is already running
    if is_port_in_use(8501):
        print("ℹ️  Streamlit app is already running!")
        print("🌐 Opening browser to: http://localhost:8501")
        webbrowser.open('http://localhost:8501')
        print()
        print("💡 If you want to restart, first stop the existing app (Ctrl+C in the terminal)")
        return

    try:
        # Start the Streamlit app
        print("🌐 Launching Streamlit app...")
        process = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True)

        # Wait a moment for Streamlit to start
        time.sleep(5)

        # Check if process is still running
        if process.poll() is None:
            print("✅ Streamlit app started successfully!")
            print("🌐 Opening browser to: http://localhost:8501")
            print()
            print("💡 Quick tips:")
            print("   • Ask about crop prices: 'wheat price in Punjab'")
            print("   • Get farming advice: 'how to improve tomato yield'")
            print("   • Press Ctrl+C in terminal to stop")
            print()

            # Open browser only if not already running
            webbrowser.open('http://localhost:8501')

            # Keep the script running to show output
            try:
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())
            except KeyboardInterrupt:
                print("\n🛑 Stopping Streamlit app...")
                process.terminate()
                process.wait()
        else:
            print("❌ Failed to start Streamlit app")
            stdout, stderr = process.communicate()
            print("Error:", stdout)

    except FileNotFoundError:
        print("❌ Error: streamlit_app.py not found in current directory")
    except Exception as e:
        print(f"❌ Error starting Streamlit app: {e}")

if __name__ == "__main__":
    main()