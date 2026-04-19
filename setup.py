"""
Setup script for the Placement-Risk Modeling System
"""

import subprocess
import sys
import os


def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "="*70)
    print(text)
    print("="*70)


def run_command(command, description):
    """Run a shell command"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print(f"✓ {description} - SUCCESS")
            return True
        else:
            print(f"✗ {description} - FAILED")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ {description} - ERROR: {e}")
        return False


def check_python_version():
    """Check if Python version is 3.9+"""
    print_banner("CHECKING PYTHON VERSION")
    
    if sys.version_info < (3, 9):
        print(f"✗ Python {sys.version_info.major}.{sys.version_info.minor} detected")
        print("⚠️ Python 3.9 or higher is required")
        return False
    else:
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
        return True


def install_dependencies():
    """Install required packages"""
    print_banner("INSTALLING DEPENDENCIES")
    
    requirements_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'requirements.txt'
    )
    
    if not os.path.exists(requirements_file):
        print(f"✗ requirements.txt not found at {requirements_file}")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python packages"
    )


def create_directories():
    """Create necessary directories"""
    print_banner("CREATING DIRECTORIES")
    
    directories = ['models', 'data']
    
    for directory in directories:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)
        os.makedirs(path, exist_ok=True)
        print(f"✓ Created {directory}/")
    
    return True


def verify_installation():
    """Verify that key packages are installed"""
    print_banner("VERIFYING INSTALLATION")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'sklearn',
        'pydantic'
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            if package == 'sklearn':
                __import__('sklearn')
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT FOUND")
            all_installed = False
    
    return all_installed


def run_quick_demo():
    """Run a quick demonstration"""
    print_banner("RUNNING QUICK DEMO")
    
    demo_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'quick_start.py'
    )
    
    if os.path.exists(demo_file):
        return run_command(
            f"{sys.executable} {demo_file}",
            "Running quick start demo"
        )
    else:
        print("✗ quick_start.py not found")
        return False


def main():
    """Main setup routine"""
    print_banner("PLACEMENT-RISK MODELING SYSTEM - SETUP")
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Create Directories", create_directories),
        ("Verify Installation", verify_installation),
    ]
    
    completed = 0
    total = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n[{completed+1}/{total}] {step_name}")
        if step_func():
            completed += 1
    
    print_banner("SETUP SUMMARY")
    print(f"\nCompleted: {completed}/{total} steps")
    
    if completed == total:
        print("\n✅ SETUP COMPLETE!")
        print("\nNext Steps:")
        print("1. Train models: python train.py")
        print("2. Start API: python main.py")
        print("3. Run tests: python test_api.py")
        print("4. View examples: python examples.py")
        print("5. Read docs: README.md")
    else:
        print("\n⚠️ SETUP INCOMPLETE - Please check errors above")
        print("You may need to:")
        print("  - Install Python 3.9+")
        print("  - Fix network connectivity for pip install")
        print("  - Check file permissions")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
