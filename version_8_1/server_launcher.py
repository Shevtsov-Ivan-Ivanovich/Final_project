# server_launcher.py
import sys
import os
import subprocess
from pathlib import Path

if __name__ == "__main__":
    print("=" * 50)
    print("Запуск сервера ДПЖ...")
    print("=" * 50)
    
    # Запускаем сервер
    subprocess.run([sys.executable, "server/run.py"])