import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CONSOLIDATED_TEST_SCRIPTS = [
    "e2e/test_cancel_bookings.py",
    "e2e/test_create_bookings.py",
    "e2e/test_update_bookings.py",
    "e2e/test_nlp_edge_cases.py",
    "e2e/test_booking_conflicts.py",
    "e2e/test_time_formats.py",
    "integration/test_booking_flow_integration.py",
    "unit/test_utils.py",
    "unit/test_booking_handler.py",
    "unit/test_conflict_checker.py",
    "unit/test_ampm_clarification.py",
    "unit/test_time_input_variations.py",
    "unit/test_specific_minutes.py",
    "unit/test_combined_inputs.py"
]


def run_tests():
    for test_script in CONSOLIDATED_TEST_SCRIPTS:
        test_path = os.path.join(os.path.dirname(__file__), test_script)
        if os.path.exists(test_path):
            pytest.main(["-v", test_path])
        else:
            print(f"Warning: Test script {test_path} not found")


if __name__ == "__main__":
    run_tests()
