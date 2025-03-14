import os
import subprocess
import sys
import time
import signal
import platform
import webbrowser
from pathlib import Path


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


backend_process = None
frontend_process = None


def is_venv_activated():
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)


def activate_venv():
    if not is_venv_activated():
        venv_path = Path("venv")
        if not venv_path.exists():
            print(f"{Colors.YELLOW}Virtual environment not found. Creating one...{Colors.ENDC}")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        if platform.system() == "Windows":
            pip_path = venv_path / "Scripts" / "pip"
        else:
            pip_path = venv_path / "bin" / "pip"
        print(f"{Colors.BLUE}Installing backend dependencies...{Colors.ENDC}")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)


def start_backend():
    global backend_process
    print(f"{Colors.BLUE}Starting backend server...{Colors.ENDC}")
    if is_venv_activated():
        python_executable = sys.executable
    else:
        if platform.system() == "Windows":
            python_executable = str(Path("venv") / "Scripts" / "python")
        else:
            python_executable = str(Path("venv") / "bin" / "python")
    backend_cmd = [
        python_executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload"]
    if platform.system() == "Windows":
        backend_process = subprocess.Popen(
            backend_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        backend_process = subprocess.Popen(backend_cmd)
    print(f"{Colors.YELLOW}Waiting for backend to start...{Colors.ENDC}")
    time.sleep(2)
    try:
        import requests
        for _ in range(5):
            try:
                response = requests.get("http://localhost:8000/api/v1/bookings/")
                if response.status_code == 200:
                    print(f"{Colors.GREEN}Backend server started successfully!{Colors.ENDC}")
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        print(f"{Colors.RED}Failed to connect to backend server.{Colors.ENDC}")
        return False
    except ImportError:
        print(f"{Colors.YELLOW}Could not verify backend server (requests module not available).{Colors.ENDC}")
        return True


def start_frontend():
    global frontend_process
    print(f"{Colors.BLUE}Starting frontend server...{Colors.ENDC}")
    frontend_dir = Path("booking-ui")
    if not (frontend_dir / "node_modules").exists():
        print(f"{Colors.YELLOW}Installing frontend dependencies...{Colors.ENDC}")
        subprocess.run(["npm", "install"], cwd=str(frontend_dir), check=True)
    if platform.system() == "Windows":
        frontend_process = subprocess.Popen(["npm", "start"], cwd=str(
            frontend_dir), creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        frontend_process = subprocess.Popen(["npm", "start"], cwd=str(frontend_dir))
    print(f"{Colors.GREEN}Frontend server starting...{Colors.ENDC}")
    time.sleep(3)
    webbrowser.open("http://localhost:3000")


def cleanup(signum=None, frame=None):
    print(f"\n{Colors.YELLOW}Shutting down servers...{Colors.ENDC}")
    if frontend_process:
        print(f"{Colors.BLUE}Stopping frontend server...{Colors.ENDC}")
        if platform.system() == "Windows":
            frontend_process.terminate()
        else:
            frontend_process.send_signal(signal.SIGTERM)
    if backend_process:
        print(f"{Colors.BLUE}Stopping backend server...{Colors.ENDC}")
        if platform.system() == "Windows":
            backend_process.terminate()
        else:
            backend_process.send_signal(signal.SIGTERM)
    print(f"{Colors.GREEN}All servers stopped. Goodbye!{Colors.ENDC}")
    sys.exit(0)


def main():
    print(f"{Colors.HEADER}{Colors.BOLD}Starting Technician Booking System{Colors.ENDC}")
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    try:
        activate_venv()
        if not start_backend():
            print(f"{Colors.RED}Failed to start backend. Exiting.{Colors.ENDC}")
            cleanup()
            return 1
        start_frontend()
        print(f"{Colors.GREEN}Application started successfully!{Colors.ENDC}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop the servers.{Colors.ENDC}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
        return 0
    except Exception as e:
        print(f"{Colors.RED}Error: {str(e)}{Colors.ENDC}")
        cleanup()
        return 1


if __name__ == "__main__":
    sys.exit(main())
