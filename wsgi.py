import os
import sys
import subprocess

def check_gunicorn():
    """Check if gunicorn is installed"""
    try:
        import gunicorn
        return True
    except ImportError:
        return False

def install_gunicorn():
    """Install gunicorn"""
    print("Installing Gunicorn...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn"])
    print("Gunicorn installed successfully")

def run_production():
    """Run the app with Gunicorn (production server)"""
    if not check_gunicorn():
        print("WARNING: Gunicorn not found")
        response = input("Install Gunicorn for production deployment? [y/N]: ")
        if response.lower() == 'y':
            install_gunicorn()
        else:
            print("ERROR: Cannot run production server without Gunicorn")
            return
    
    port = os.getenv("PORT", "5000")
    workers = os.getenv("WORKERS", "4")
    
    print("=" * 60)
    print("PRODUCTION SERVER")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Workers: {workers}")
    print(f"Host: 0.0.0.0")
    print("=" * 60)
    
    # Run gunicorn
    cmd = [
        "gunicorn",
        "--bind", f"0.0.0.0:{port}",
        "--workers", workers,
        "--timeout", "120",
        "--worker-class", "sync",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "app_improved:app"
    ]
    
    print(f"\nCommand: {' '.join(cmd)}\n")
    subprocess.call(cmd)

def run_development():
    """Run the app with Flask's development server"""
    print("=" * 60)
    print("DEVELOPMENT SERVER")
    print("=" * 60)
    print("WARNING: This is a development server")
    print("WARNING: Do NOT use in production")
    print("=" * 60)
    
    import app
    port = int(os.getenv("PORT", "5000"))
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=port
    )

if __name__ == "__main__":
    print("Anime Recommendation API Server")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        run_development()
    else:
        print("Usage:")
        print("  python wsgy.py          # Production (Gunicorn)")
        print("  python wsgy.py --dev    # Development (Flask)")
        print()
        
        mode = input("Run in production mode? [Y/n]: ")
        if mode.lower() in ['', 'y', 'yes']:
            run_production()
        else:
            run_development()