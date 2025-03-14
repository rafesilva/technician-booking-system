#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_header() {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================================${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

cd "$(dirname "$0")"
BASE_DIR=$(pwd)

echo_header "Starting Comprehensive Test Suite"
echo "Current directory: $BASE_DIR"
echo "Date: $(date)"
echo ""

run_test() {
    TEST_NAME=$1
    TEST_CMD=$2
    
    echo_header "Running $TEST_NAME"
    echo "Command: $TEST_CMD"
    
    eval $TEST_CMD
    TEST_RESULT=$?
    
    if [ $TEST_RESULT -eq 0 ]; then
        echo_success "$TEST_NAME tests PASSED"
    else
        echo_error "$TEST_NAME tests FAILED"
        FAILED_TESTS="$FAILED_TESTS $TEST_NAME"
    fi
    
    return $TEST_RESULT
}

FAILED_TESTS=""
TESTS_PASSED=0
TESTS_FAILED=0

if run_test "Unit Tests" "python -m pytest app/tests/unit/ -v"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

if run_test "Integration Tests" "python -m pytest app/tests/integration/ -v"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

if run_test "End-to-End Tests" "python -m pytest app/tests/e2e/ -v"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo_header "Running Specific Test Scenarios"

if run_test "Combined Date Time Test" "python -m pytest app/tests/unit/test_combined_inputs.py::TestCombinedInputs::test_combined_date_time_inputs -v"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

if run_test "AM/PM Clarification Test" "python -m pytest app/tests/unit/test_ampm_clarification.py -v"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

if run_test "Time Input Variations Test" "python -m pytest app/tests/unit/test_time_input_variations.py -v"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

if run_test "Chat Issues Test" "python -m pytest app/tests/unit/test_chat_issues.py -v"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

if run_test "Specialty Change Test" "python -m pytest app/tests/e2e/test_nlp_edge_cases.py::test_multi_turn_correction -v"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo_header "Test Summary"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"

if [ $TESTS_FAILED -eq 0 ]; then
    echo_success "ALL TESTS PASSED! 🎉"
    exit 0
else
    echo_error "Some tests failed: $FAILED_TESTS"
    exit 1
fi