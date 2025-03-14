import sys
import platform
import subprocess
from pathlib import Path


def check_python_version():
    python_version = sys.version_info
    if python_version.major < 3 or (
            python_version.major == 3 and python_version.minor < 6):
        print("❌ Python 3.6 or higher is required")
        print(
            f"   Current version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return False
    else:
        print(
            f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return True


def check_pip():
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                       check=True, capture_output=True)
        print("✅ pip is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip is not installed")
        return False


def check_node():
    try:
        node_process = subprocess.run(
            ["node", "--version"], check=True, capture_output=True, text=True)
        node_version = node_process.stdout.strip()
        print(f"✅ Node.js version: {node_version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js is not installed")
        return False


def check_npm():
    try:
        npm_process = subprocess.run(
            ["npm", "--version"], check=True, capture_output=True, text=True)
        npm_version = npm_process.stdout.strip()
        print(f"✅ npm version: {npm_version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm is not installed")
        return False


def check_backend_dependencies():
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Backend dependencies are installed")
        return True
    except ImportError:
        print("❌ Backend dependencies are not installed")
        print("   Run: pip install -r requirements.txt")
        return False


def check_frontend_dependencies():
    frontend_dir = Path("booking-ui")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found in frontend directory")
        return False
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists() or not node_modules.is_dir():
        print("❌ Frontend dependencies are not installed")
        print(f"   Run: cd {frontend_dir} && npm install")
        return False
    print("✅ Frontend dependencies are installed")
    return True


def check_venv():
    in_venv = hasattr(
        sys,
        'real_prefix') or (
        hasattr(
            sys,
            'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("✅ Running in a virtual environment")
    else:
        print("⚠️ Not running in a virtual environment")
        print("   It's recommended to use a virtual environment")
    return True


def main():
    print("Checking system requirements for Technician Booking System...\n")
    python_ok = check_python_version()
    pip_ok = check_pip()
    node_ok = check_node()
    npm_ok = check_npm()
    venv_ok = check_venv()
    print("\nChecking dependencies...")
    backend_ok = check_backend_dependencies() if pip_ok else False
    frontend_ok = check_frontend_dependencies() if npm_ok else False
    print("\nSummary:")
    all_ok = python_ok and pip_ok and node_ok and npm_ok and backend_ok and frontend_ok
    if all_ok:
        print("\n✅ All requirements are met! You're ready to run the application.")
        print("   Run './start.sh' (Linux/macOS) or 'start.bat' (Windows) to start the application.")
    else:
        print("\n❌ Some requirements are not met. Please fix the issues above before running the application.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
