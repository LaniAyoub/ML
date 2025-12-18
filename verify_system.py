"""
System Verification Test Suite
Run this to verify all components are working correctly before demo/presentation
"""
import requests
import time
import json
from pathlib import Path


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}{'='*70}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}{text.center(70)}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}{'='*70}{bcolors.ENDC}\n")


def print_test(test_name, status, message=""):
    if status:
        print(f"{bcolors.OKGREEN}✓ {test_name}{bcolors.ENDC}")
        if message:
            print(f"  {bcolors.OKCYAN}{message}{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}✗ {test_name}{bcolors.ENDC}")
        if message:
            print(f"  {bcolors.WARNING}{message}{bcolors.ENDC}")


def test_file_structure():
    """Test if project structure is correct"""
    print_header("FILE STRUCTURE VERIFICATION")
    
    required_dirs = [
        "src", "frontend", "monitoring", "models", "data", 
        "logs", "tests", "docs"
    ]
    required_files = [
        "src/data_preprocessing.py",
        "src/train_model.py",
        "src/predict_api.py",
        "preprocessing.py",
        "frontend/index.html",
        "frontend/script.js",
        "frontend/Dockerfile",
        "frontend/nginx.conf",
        "Dockerfile",
        "docker-compose.yml",
        "requirements.txt",
        "README.md",
        "setup_project.py"
    ]
    
    all_pass = True
    
    for dir_name in required_dirs:
        exists = Path(dir_name).exists()
        print_test(f"Directory: {dir_name}", exists)
        all_pass = all_pass and exists
    
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_test(f"File: {file_path}", exists)
        all_pass = all_pass and exists
    
    # Check for model file
    model_exists = Path("models/final_churn_prediction_pipeline.pkl").exists()
    print_test(
        "Model file", 
        model_exists,
        "models/final_churn_prediction_pipeline.pkl"
    )
    all_pass = all_pass and model_exists
    
    # Check for data file
    data_exists = Path("data/WA_Fn-UseC_-Telco-Customer-Churn.csv").exists()
    print_test(
        "Dataset file",
        data_exists,
        "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
    )
    all_pass = all_pass and data_exists
    
    return all_pass


def test_api_service():
    """Test if API is running and responding"""
    print_header("API SERVICE VERIFICATION")
    
    base_url = "http://localhost:8000"
    all_pass = True
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health_pass = response.status_code == 200
        print_test(
            "GET /health",
            health_pass,
            f"Status: {response.status_code}"
        )
        all_pass = all_pass and health_pass
        
        if health_pass:
            data = response.json()
            model_loaded = data.get("model_loaded", False)
            print_test(
                "Model loaded",
                model_loaded,
                f"Status: {data.get('status')}"
            )
            all_pass = all_pass and model_loaded
    except Exception as e:
        print_test("GET /health", False, f"Error: {str(e)}")
        all_pass = False
    
    # Test metrics endpoint
    try:
        response = requests.get(f"{base_url}/metrics", timeout=5)
        metrics_pass = response.status_code == 200
        print_test(
            "GET /metrics",
            metrics_pass,
            f"Status: {response.status_code}"
        )
        all_pass = all_pass and metrics_pass
    except Exception as e:
        print_test("GET /metrics", False, f"Error: {str(e)}")
        all_pass = False
    
    # Test prediction endpoint
    test_data = {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 70.35,
        "TotalCharges": "70.35"
    }
    
    try:
        response = requests.post(
            f"{base_url}/predict",
            json=test_data,
            timeout=10
        )
        predict_pass = response.status_code == 200
        print_test(
            "POST /predict",
            predict_pass,
            f"Status: {response.status_code}"
        )
        
        if predict_pass:
            result = response.json()
            has_prediction = "churn_prediction" in result
            has_probability = "churn_probability" in result
            has_risk = "risk_level" in result
            
            print_test(
                "Response format",
                has_prediction and has_probability and has_risk,
                f"Prediction: {result.get('churn_prediction')}, "
                f"Probability: {result.get('churn_probability'):.2f}, "
                f"Risk: {result.get('risk_level')}"
            )
            all_pass = all_pass and predict_pass and has_prediction
    except Exception as e:
        print_test("POST /predict", False, f"Error: {str(e)}")
        all_pass = False
    
    return all_pass


def test_frontend_service():
    """Test if frontend is accessible"""
    print_header("FRONTEND SERVICE VERIFICATION")
    
    all_pass = True
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        frontend_pass = response.status_code == 200
        print_test(
            "Frontend accessible",
            frontend_pass,
            f"Status: {response.status_code}"
        )
        all_pass = all_pass and frontend_pass
        
        if frontend_pass:
            content = response.text
            has_title = "Churn Prediction" in content
            has_bootstrap = "bootstrap" in content.lower()
            has_chartjs = "chart.js" in content.lower()
            
            print_test("HTML title", has_title)
            print_test("Bootstrap loaded", has_bootstrap)
            print_test("Chart.js loaded", has_chartjs)
            all_pass = all_pass and has_title and has_bootstrap
    except Exception as e:
        print_test("Frontend accessible", False, f"Error: {str(e)}")
        all_pass = False
    
    return all_pass


def test_monitoring_services():
    """Test if monitoring services are running"""
    print_header("MONITORING SERVICES VERIFICATION")
    
    all_pass = True
    
    # Test Prometheus
    try:
        response = requests.get("http://localhost:9090/-/healthy", timeout=5)
        prom_pass = response.status_code == 200
        print_test(
            "Prometheus healthy",
            prom_pass,
            f"Status: {response.status_code}"
        )
        all_pass = all_pass and prom_pass
    except Exception as e:
        print_test("Prometheus healthy", False, f"Error: {str(e)}")
        all_pass = False
    
    # Test Grafana
    try:
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        grafana_pass = response.status_code == 200
        print_test(
            "Grafana healthy",
            grafana_pass,
            f"Status: {response.status_code}"
        )
        all_pass = all_pass and grafana_pass
    except Exception as e:
        print_test("Grafana healthy", False, f"Error: {str(e)}")
        all_pass = False
    
    return all_pass


def test_logs():
    """Test if logging is working"""
    print_header("LOGGING VERIFICATION")
    
    all_pass = True
    
    logs_dir = Path("logs")
    log_file = logs_dir / "predictions.jsonl"
    
    dir_exists = logs_dir.exists()
    print_test("Logs directory exists", dir_exists)
    all_pass = all_pass and dir_exists
    
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    has_timestamp = "timestamp" in last_entry
                    has_prediction = "prediction" in last_entry
                    
                    print_test(
                        "Prediction logs working",
                        has_timestamp and has_prediction,
                        f"Total predictions logged: {len(lines)}"
                    )
                    all_pass = all_pass and has_timestamp and has_prediction
                else:
                    print_test(
                        "Prediction logs",
                        True,
                        "File exists but no predictions yet"
                    )
        except Exception as e:
            print_test("Reading log file", False, f"Error: {str(e)}")
            all_pass = False
    else:
        print_test(
            "Prediction log file",
            True,
            "Will be created on first prediction"
        )
    
    return all_pass


def run_integration_test():
    """Run a complete integration test"""
    print_header("INTEGRATION TEST")
    
    print(f"{bcolors.OKCYAN}Running complete workflow test...{bcolors.ENDC}\n")
    
    # Step 1: Make prediction
    test_customers = [
        {
            "name": "High Risk Customer",
            "data": {
                "gender": "Female",
                "SeniorCitizen": 0,
                "Partner": "No",
                "Dependents": "No",
                "tenure": 1,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "No",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 70.35,
                "TotalCharges": "70.35"
            },
            "expected_risk": "high"
        },
        {
            "name": "Low Risk Customer",
            "data": {
                "gender": "Male",
                "SeniorCitizen": 0,
                "Partner": "Yes",
                "Dependents": "Yes",
                "tenure": 36,
                "PhoneService": "Yes",
                "MultipleLines": "Yes",
                "InternetService": "DSL",
                "OnlineSecurity": "Yes",
                "OnlineBackup": "Yes",
                "DeviceProtection": "Yes",
                "TechSupport": "Yes",
                "StreamingTV": "Yes",
                "StreamingMovies": "Yes",
                "Contract": "Two year",
                "PaperlessBilling": "No",
                "PaymentMethod": "Bank transfer (automatic)",
                "MonthlyCharges": 90.0,
                "TotalCharges": "3240.0"
            },
            "expected_risk": "low"
        }
    ]
    
    all_pass = True
    
    for customer in test_customers:
        print(f"\n{bcolors.BOLD}Testing: {customer['name']}{bcolors.ENDC}")
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json=customer["data"],
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                risk_level = result.get("risk_level")
                probability = result.get("churn_probability")
                
                risk_match = risk_level == customer["expected_risk"]
                print_test(
                    f"Risk level",
                    risk_match,
                    f"Got: {risk_level}, Probability: {probability:.2f}"
                )
                all_pass = all_pass and risk_match
            else:
                print_test(
                    f"Prediction request",
                    False,
                    f"Status: {response.status_code}"
                )
                all_pass = False
        except Exception as e:
            print_test(f"Integration test", False, f"Error: {str(e)}")
            all_pass = False
    
    # Check if metrics updated
    try:
        time.sleep(1)  # Give time for metrics to update
        response = requests.get("http://localhost:8000/metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            total = metrics.get("total_predictions", 0)
            print_test(
                "Metrics updated",
                total >= len(test_customers),
                f"Total predictions: {total}"
            )
    except Exception as e:
        print_test("Metrics check", False, f"Error: {str(e)}")
        all_pass = False
    
    return all_pass


def main():
    """Run all verification tests"""
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                      ║")
    print("║           CHURN PREDICTION SYSTEM VERIFICATION                       ║")
    print("║                                                                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"{bcolors.ENDC}")
    
    print(f"\n{bcolors.OKCYAN}Starting system verification...{bcolors.ENDC}")
    print(f"{bcolors.WARNING}Make sure Docker services are running (docker-compose up){bcolors.ENDC}\n")
    
    time.sleep(2)
    
    # Run all tests
    results = {}
    
    results["File Structure"] = test_file_structure()
    results["API Service"] = test_api_service()
    results["Frontend Service"] = test_frontend_service()
    results["Monitoring Services"] = test_monitoring_services()
    results["Logging"] = test_logs()
    results["Integration Test"] = run_integration_test()
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status_icon = "✓" if passed else "✗"
        color = bcolors.OKGREEN if passed else bcolors.FAIL
        print(f"{color}{status_icon} {test_name:.<50}{'PASS' if passed else 'FAIL'}{bcolors.ENDC}")
    
    print(f"\n{bcolors.BOLD}{'='*70}{bcolors.ENDC}")
    
    if all_passed:
        print(f"\n{bcolors.OKGREEN}{bcolors.BOLD}")
        print("🎉 ALL TESTS PASSED! System is ready for demo/presentation.")
        print(f"{bcolors.ENDC}")
        
        print(f"\n{bcolors.OKCYAN}Access your services at:{bcolors.ENDC}")
        print(f"  📊 Dashboard:  http://localhost:3000")
        print(f"  🔌 API Docs:   http://localhost:8000/docs")
        print(f"  📈 Grafana:    http://localhost:3001")
        print(f"  📉 Prometheus: http://localhost:9090")
        
        return 0
    else:
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}")
        print("❌ SOME TESTS FAILED! Please fix issues before demo.")
        print(f"{bcolors.ENDC}")
        
        print(f"\n{bcolors.WARNING}Troubleshooting steps:{bcolors.ENDC}")
        print("  1. Check if Docker services are running: docker-compose ps")
        print("  2. View service logs: docker-compose logs")
        print("  3. Restart services: docker-compose down && docker-compose up --build")
        print("  4. Check setup: python setup_project.py")
        
        return 1


if __name__ == "__main__":
    exit(main())
