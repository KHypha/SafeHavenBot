import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import subprocess
import sys

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        elif event.event_type == 'modified':
            print(f'Restarting bot due to changes in {event.src_path}')
            restart_bot()

def restart_bot():
    stop_bot()
    start_bot()

def start_bot():
    global bot_process
    python = sys.executable
    bot_process = subprocess.Popen([python, 'main.py'])
    print(' bot Started...')
def stop_bot():
    global bot_process
    if bot_process:
        print('Stopping bot...')
        bot_process.terminate()
        bot_process.wait()
        print('Bot stopped.')
        bot_process = None

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()

    # Add directories to the observer 
    for root, dirs, files in os.walk("."):
        observer.schedule(event_handler, path=root, recursive=False)

    observer.start()

    bot_process = None

    try:
        start_bot()
        while True:
            # Sleep for a short interval, e.g., 1 second
            time.sleep(1)
    except KeyboardInterrupt:
        stop_bot()
        observer.stop()

    observer.join()
