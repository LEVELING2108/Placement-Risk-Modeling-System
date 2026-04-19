"""
Comprehensive validation script for Placement-Risk Modeling System
Validates all dependencies, models, and configurations before deployment
"""

import sys
import os
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_success(text):
    """Print success message"""
    print(f"[OK] {text}")


def print_error(text):
    """Print error message"""
    print(f"[FAIL] {text}")


def print_warning(text):
    """Print warning message"""
    print(f"[WARN] {text}")


def check_python_version():
    """Check Python version"""
    print_header("1. PYTHON VERSION CHECK")
    required_version = (3, 9)
    current_version = sys.version_info[:2]

    if current_version >= required_version:
        print_success(f"Python version {sys.version.split()[0]} is compatible")
        return True
    else:
        print_error(f"Python {required_version[0]}.{required_version[1]}+ required, found {current_version[0]}.{current_version[1]}")
        return False


def check_dependencies():
    """Check if all required dependencies are installed"""
    print_header("2. DEPENDENCY CHECK")

    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'sklearn': 'Scikit-learn',
        'xgboost': 'XGBoost',
        'joblib': 'Joblib'
    }

    all_installed = True

    for package, name in required_packages.items():
        try:
            __import__(package)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed")
            all_installed = False

    return all_installed


def check_directory_structure():
    """Check if required directories exist"""
    print_header("3. DIRECTORY STRUCTURE CHECK")

    required_dirs = [
        'app',
        'app/api',
        'app/core',
        'app/models',
        'app/schemas',
        'app/services',
        'models',
        'data',
        'static'
    ]

    all_exist = True

    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_success(f"Directory '{dir_path}' exists")
        else:
            print_error(f"Directory '{dir_path}' NOT found")
            all_exist = False

    return all_exist


def check_models():
    """Check if trained models exist"""
    print_header("4. TRAINED MODELS CHECK")

    model_files = [
        'models/placement_model.pkl',
        'models/salary_model.pkl'
    ]

    all_exist = True

    for model_path in model_files:
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            print_success(f"Model '{model_path}' exists ({size_mb:.2f} MB)")
        else:
            print_warning(f"Model '{model_path}' NOT found - need to train")
            all_exist = False

    return all_exist


def check_data_files():
    """Check if data files exist"""
    print_header("5. DATA FILES CHECK")

    data_files = {
        'data/training_data.csv': False,  # Optional
        'data/training_metrics.json': False,  # Optional
        'data/portfolio.json': True  # Required
    }

    all_required_exist = True

    for file_path, required in data_files.items():
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print_success(f"File '{file_path}' exists ({size_kb:.2f} KB)")
        else:
            if required:
                print_error(f"Required file '{file_path}' NOT found")
                all_required_exist = False
            else:
                print_warning(f"Optional file '{file_path}' NOT found")

    return all_required_exist


def check_imports():
    """Check if core modules can be imported"""
    print_header("6. MODULE IMPORT CHECK")

    modules_to_test = [
        ('app.core.config', 'Configuration'),
        ('app.schemas.prediction', 'Schemas'),
        ('app.services.preprocessing', 'Preprocessing'),
        ('app.services.feature_engineering', 'Feature Engineering'),
        ('app.models.placement_model', 'Placement Model'),
        ('app.models.salary_model', 'Salary Model'),
        ('app.services.risk_scoring', 'Risk Scoring'),
        ('app.services.recommendation', 'Recommendations'),
        ('app.services.prediction_service', 'Prediction Service'),
        ('app.api.routes', 'API Routes')
    ]

    all_imported = True

    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print_success(f"{display_name} module imported successfully")
        except Exception as e:
            print_error(f"{display_name} module import failed: {str(e)}")
            all_imported = False

    return all_imported


def check_model_loading():
    """Check if models can be loaded"""
    print_header("7. MODEL LOADING CHECK")

    try:
        from app.services.prediction_service import PredictionService

        ps = PredictionService()

        if ps.models_loaded:
            print_success("Models loaded successfully")
            print_success("Placement model ready")
            print_success("Salary model ready")
            return True
        else:
            print_warning("Models not loaded - may need training")
            return False
    except Exception as e:
        print_error(f"Model loading failed: {str(e)}")
        return False


def check_api_configuration():
    """Check API configuration"""
    print_header("8. API CONFIGURATION CHECK")

    try:
        from app.core.config import settings

        print_success(f"App Name: {settings.APP_NAME}")
        print_success(f"App Version: {settings.APP_VERSION}")
        print_success(f"Placement Model Path: {settings.PLACEMENT_MODEL_PATH}")
        print_success(f"Salary Model Path: {settings.SALARY_MODEL_PATH}")
        return True
    except Exception as e:
        print_error(f"Configuration check failed: {str(e)}")
        return False


def test_prediction_pipeline():
    """Test the prediction pipeline with sample data"""
    print_header("9. PREDICTION PIPELINE TEST")

    try:
        from app.services.data_generator import SampleDataGenerator
        from app.services.prediction_service import PredictionService

        # Generate sample student
        generator = SampleDataGenerator(seed=42)
        student = generator.generate_single_student(
            student_id="VALIDATION_TEST",
            risk_profile='medium'
        )

        print_success("Sample student generated")

        # Test prediction
        predictor = PredictionService()

        if not predictor.models_loaded:
            print_warning("Models not loaded - skipping prediction test")
            return False

        result = predictor.predict_single(student)

        print_success("Prediction completed successfully")
        print(f"    - Timeline: {result.placement_prediction.predicted_timeline}")
        print(f"    - Risk Level: {result.risk_assessment.risk_level}")
        print(f"    - Expected Salary: Rs.{result.salary_prediction.expected_salary_avg:,.0f}")

        return True
    except Exception as e:
        print_error(f"Prediction pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation checks"""
    print("\n" + "=" * 70)
    print("  PLACEMENT-RISK MODELING SYSTEM - VALIDATION")
    print("=" * 70)

    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("Directory Structure", check_directory_structure()),
        ("Trained Models", check_models()),
        ("Data Files", check_data_files()),
        ("Module Imports", check_imports()),
        ("Model Loading", check_model_loading()),
        ("API Configuration", check_api_configuration()),
        ("Prediction Pipeline", test_prediction_pipeline())
    ]

    # Summary
    print_header("VALIDATION SUMMARY")

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    for check_name, result in checks:
        status = "PASS" if result else "FAIL"
        symbol = "[OK]" if result else "[FAIL]"
        print(f"{symbol} {check_name}: {status}")

    print("\n" + "-" * 70)
    print(f"Total: {passed}/{total} checks passed")

    if passed == total:
        print("\n*** ALL CHECKS PASSED! System is ready for deployment. ***")
        print("\nNext steps:")
        print("  1. Start the server: python main.py")
        print("  2. Visit: http://localhost:8000")
        print("  3. API Docs: http://localhost:8000/docs")
        return 0
    else:
        print("\n*** SOME CHECKS FAILED! Please review the errors above. ***")

        if not checks[3][1]:  # Models check failed
            print("\nTo train models:")
            print("  python train.py")

        print("\nAfter fixing issues, run this script again:")
        print("  python validate_setup.py")
        return 1

    print("=" * 70 + "\n")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
