"""
Smart startup script for Placement-Risk Modeling System
Validates setup before starting the server
"""

import sys
import os
import subprocess


def run_validation():
    """Run validation checks"""
    print("\n" + "=" * 70)
    print("  RUNNING PRE-START VALIDATION")
    print("=" * 70 + "\n")

    try:
        result = subprocess.run(
            [sys.executable, "validate_setup.py"],
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode != 0:
            print("\n[ERROR] Validation failed!")
            print("Please fix the issues above before starting the server.")
            print("\nCommon fixes:")
            print("  - Missing models? Run: python train.py")
            print("  - Missing dependencies? Run: pip install -r requirements.txt")
            return False

        return True
    except Exception as e:
        print(f"[ERROR] Could not run validation: {e}")
        return False


def start_server():
    """Start the FastAPI server"""
    print("\n" + "=" * 70)
    print("  STARTING PLACEMENT-RISK MODELING SYSTEM")
    print("=" * 70)
    print("\nServer starting at http://localhost:8000")
    print("Press Ctrl+C to stop the server\n")
    print("=" * 70 + "\n")

    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
        print("Goodbye!")
    except Exception as e:
        print(f"\n[ERROR] Server failed to start: {e}")
        return False

    return True


def main():
    """Main startup flow"""
    print("\n" + "=" * 70)
    print("  PLACEMENT-RISK MODELING SYSTEM - SMART START")
    print("=" * 70)

    # Step 1: Validate
    if not run_validation():
        print("\n[INFO] Validation failed. Starting anyway? (y/n): ", end="")
        choice = input().lower()
        if choice != 'y':
            print("Startup cancelled.")
            sys.exit(1)

    # Step 2: Start server
    start_server()


if __name__ == "__main__":
    main()
