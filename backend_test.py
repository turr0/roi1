#!/usr/bin/env python3
import requests
import json
import os
import sys
import time
from typing import Dict, Any, List, Optional

# Get backend URL from frontend/.env
def get_backend_url() -> str:
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.strip().split('=')[1].strip('"\'')
        raise ValueError("REACT_APP_BACKEND_URL not found in frontend/.env")
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        sys.exit(1)

# Test data for ROI calculation
ROI_CALCULATION_DATA = {
    "consultas_mes": 500,
    "porcentaje_automatizacion_consultas": 70.0,
    "tiempo_respuesta_manual": 4.0,
    "horas_mensuales_crm": 40.0,
    "porcentaje_automatizacion_crm": 40.0,
    "numero_empleados": 3,
    "costo_horario_empleado": 2500.0,
    "costo_licencia_anual_bitrix": 150000.0,
    "costo_implementacion": 1000000.0
}

# Test data for email submission
EMAIL_SUBMISSION_DATA = {
    "calculo_roi": {
        "consultas_mes": 500,
        "porcentaje_automatizacion_consultas": 70.0,
        "tiempo_respuesta_manual": 4.0,
        "horas_mensuales_crm": 40.0,
        "porcentaje_automatizacion_crm": 40.0,
        "numero_empleados": 3,
        "costo_horario_empleado": 2500.0,
        "costo_licencia_anual_bitrix": 150000.0,
        "costo_implementacion": 1000000.0
    },
    "contacto": {
        "nombre_completo": "Test User",
        "empresa": "Test Company",
        "email": "test@example.com"
    }
}

class BackendTester:
    def __init__(self):
        self.backend_url = get_backend_url()
        self.api_url = f"{self.backend_url}/api"
        self.test_results = []
        print(f"Backend URL: {self.backend_url}")
        print(f"API URL: {self.api_url}")
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """Run a test and record the result"""
        print(f"\n{'='*80}\nRunning test: {test_name}\n{'='*80}")
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            success = result.get('success', False)
            duration = time.time() - start_time
            
            if success:
                print(f"✅ Test '{test_name}' PASSED in {duration:.2f}s")
            else:
                print(f"❌ Test '{test_name}' FAILED in {duration:.2f}s")
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            self.test_results.append({
                'name': test_name,
                'success': success,
                'duration': duration,
                'details': result
            })
            
            return success
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ Test '{test_name}' FAILED with exception in {duration:.2f}s")
            print(f"Exception: {str(e)}")
            
            self.test_results.append({
                'name': test_name,
                'success': False,
                'duration': duration,
                'details': {'error': str(e)}
            })
            
            return False
    
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the /api/health endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health")
            response.raise_for_status()
            data = response.json()
            
            # Check if SMTP is configured
            smtp_configured = data.get('smtp_configured', False)
            
            if not smtp_configured:
                return {
                    'success': False,
                    'error': 'SMTP is not configured',
                    'response': data
                }
            
            return {
                'success': True,
                'response': data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_roi_calculation(self) -> Dict[str, Any]:
        """Test the /api/calculate-roi endpoint"""
        try:
            response = requests.post(
                f"{self.api_url}/calculate-roi",
                json=ROI_CALCULATION_DATA
            )
            response.raise_for_status()
            data = response.json()
            
            # Verify calculation results
            expected_results = self.calculate_expected_roi(ROI_CALCULATION_DATA)
            validation_errors = self.validate_roi_results(data, expected_results)
            
            if validation_errors:
                return {
                    'success': False,
                    'error': 'ROI calculation validation failed',
                    'validation_errors': validation_errors,
                    'response': data,
                    'expected': expected_results
                }
            
            return {
                'success': True,
                'response': data,
                'expected': expected_results
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_email_submission(self) -> Dict[str, Any]:
        """Test the /api/submit-roi endpoint"""
        try:
            response = requests.post(
                f"{self.api_url}/submit-roi",
                json=EMAIL_SUBMISSION_DATA
            )
            response.raise_for_status()
            data = response.json()
            
            # Check if submission was successful
            if not data.get('success', False):
                return {
                    'success': False,
                    'error': 'Email submission failed',
                    'response': data
                }
            
            return {
                'success': True,
                'response': data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_expected_roi(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate expected ROI results based on the same formulas used in the backend"""
        # Cálculo ahorro tiempo mensual chatbot (horas)
        consultas_automatizables = input_data['consultas_mes'] * (input_data['porcentaje_automatizacion_consultas'] / 100)
        tiempo_ahorro_mensual_chatbot = (consultas_automatizables * input_data['tiempo_respuesta_manual']) / 60
        
        # Cálculo ahorro económico anual chatbot
        ahorro_economico_anual_chatbot = tiempo_ahorro_mensual_chatbot * 12 * input_data['costo_horario_empleado']
        
        # Cálculo ahorro tiempo anual CRM (horas)
        tiempo_crm_automatizable = input_data['horas_mensuales_crm'] * (input_data['porcentaje_automatizacion_crm'] / 100)
        ahorro_tiempo_anual_crm = tiempo_crm_automatizable * 12 * input_data['numero_empleados']
        
        # Cálculo ahorro económico anual CRM
        ahorro_economico_anual_crm = ahorro_tiempo_anual_crm * input_data['costo_horario_empleado']
        
        # Ahorro total anual
        ahorro_total_anual = ahorro_economico_anual_chatbot + ahorro_economico_anual_crm
        
        # Inversión total
        inversion_total = input_data['costo_implementacion'] + input_data['costo_licencia_anual_bitrix']
        
        # ROI porcentaje
        roi_porcentaje = ((ahorro_total_anual - inversion_total) / inversion_total) * 100 if inversion_total > 0 else 0
        
        # Round values to 2 decimal places
        return {
            'ahorro_tiempo_mensual_chatbot': round(tiempo_ahorro_mensual_chatbot, 2),
            'ahorro_economico_anual_chatbot': round(ahorro_economico_anual_chatbot, 2),
            'ahorro_tiempo_anual_crm': round(ahorro_tiempo_anual_crm, 2),
            'ahorro_economico_anual_crm': round(ahorro_economico_anual_crm, 2),
            'ahorro_total_anual': round(ahorro_total_anual, 2),
            'inversion_total': round(inversion_total, 2),
            'roi_porcentaje': round(roi_porcentaje, 2),
            'ingresos_adicionales_estimados': None
        }
    
    def validate_roi_results(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> List[str]:
        """Validate ROI calculation results against expected values"""
        errors = []
        
        for key, expected_value in expected.items():
            if key not in actual:
                errors.append(f"Missing field: {key}")
                continue
            
            actual_value = actual[key]
            
            # Skip None values
            if expected_value is None and actual_value is None:
                continue
            
            # For numeric values, check if they're close enough (within 0.01)
            if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                if abs(expected_value - actual_value) > 0.01:
                    errors.append(f"Field {key}: Expected {expected_value}, got {actual_value}")
            elif expected_value != actual_value:
                errors.append(f"Field {key}: Expected {expected_value}, got {actual_value}")
        
        return errors
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return a summary"""
        tests = [
            ('Health Check', self.test_health_endpoint),
            ('ROI Calculation', self.test_roi_calculation),
            ('Email Submission', self.test_email_submission)
        ]
        
        results = {
            'total': len(tests),
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        for test_name, test_func in tests:
            success = self.run_test(test_name, test_func)
            if success:
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        results['tests'] = self.test_results
        results['success_rate'] = (results['passed'] / results['total']) * 100 if results['total'] > 0 else 0
        
        return results
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print a summary of test results"""
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total tests: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Success rate: {results['success_rate']:.2f}%")
        print(f"{'='*80}")
        
        for test in results['tests']:
            status = "✅ PASSED" if test['success'] else "❌ FAILED"
            print(f"{status} - {test['name']} ({test['duration']:.2f}s)")
            
            if not test['success'] and 'error' in test['details']:
                print(f"  Error: {test['details']['error']}")
            
            if not test['success'] and 'validation_errors' in test['details']:
                print("  Validation errors:")
                for error in test['details']['validation_errors']:
                    print(f"  - {error}")
        
        print(f"{'='*80}")

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()
    tester.print_summary(results)