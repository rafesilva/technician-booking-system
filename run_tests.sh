#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}======================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

print_info() {
    echo -e "${BLUE}i $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 and try again."
        exit 1
    fi
    
    print_success "Python 3 is installed."
}

check_pytest() {
    if ! python3 -c "import pytest" &> /dev/null; then
        print_warning "pytest is not installed. Installing..."
        python3 -m pip install pytest
        if [ $? -ne 0 ]; then
            print_error "Failed to install pytest. Please install it manually with 'pip install pytest'."
            exit 1
        fi
        print_success "pytest installed successfully."
    else
        print_success "pytest is already installed."
    fi
}

check_termcolor() {
    if ! python3 -c "import termcolor" &> /dev/null; then
        print_warning "termcolor is not installed. Installing..."
        python3 -m pip install termcolor
        if [ $? -ne 0 ]; then
            print_warning "Failed to install termcolor. The test runner will work, but without colored output."
        else
            print_success "termcolor installed successfully."
        fi
    else
        print_success "termcolor is already installed."
    fi
}

run_tests() {
    TESTS_DIR="app/tests"
    
    TEST_DIRS=()
    PYTEST_ARGS=()
    RUN_UNIT=false
    RUN_INTEGRATION=false
    RUN_E2E=false
    
    for arg in "$@"; do
        case $arg in
            --unit)
                RUN_UNIT=true
                ;;
            --integration)
                RUN_INTEGRATION=true
                ;;
            --e2e)
                RUN_E2E=true
                ;;
            -v|--verbose|-x|--fail-fast|-xvs)
                PYTEST_ARGS+=("$arg")
                ;;
            *)
                PYTEST_ARGS+=("$arg")
                ;;
        esac
    done
    
    if [ "$RUN_UNIT" = false ] && [ "$RUN_INTEGRATION" = false ] && [ "$RUN_E2E" = false ]; then
        if [ -f "$TESTS_DIR/run_tests.py" ]; then
            print_info "Running tests with run_tests.py..."
            python3 "$TESTS_DIR/run_tests.py" "${PYTEST_ARGS[@]}"
        else
            print_error "run_tests.py not found. Running tests with pytest directly."
            python3 -m pytest "$TESTS_DIR" "${PYTEST_ARGS[@]}"
        fi
    else
        if [ "$RUN_UNIT" = true ]; then
            TEST_DIRS+=("$TESTS_DIR/unit/")
        fi
        if [ "$RUN_INTEGRATION" = true ]; then
            TEST_DIRS+=("$TESTS_DIR/integration/")
        fi
        if [ "$RUN_E2E" = true ]; then
            TEST_DIRS+=("$TESTS_DIR/e2e/")
        fi
        
        print_info "Running tests with pytest directly..."
        python3 -m pytest "${TEST_DIRS[@]}" "${PYTEST_ARGS[@]}"
    fi
}

run_pytest() {
    TESTS_DIR="app/tests"
    
    TEST_DIRS=()
    PYTEST_ARGS=()
    
    for arg in "$@"; do
        case $arg in
            --unit)
                TEST_DIRS+=("$TESTS_DIR/unit/")
                ;;
            --integration)
                TEST_DIRS+=("$TESTS_DIR/integration/")
                ;;
            --e2e)
                TEST_DIRS+=("$TESTS_DIR/e2e/")
                ;;
            -v|--verbose|-x|--fail-fast|-xvs)
                PYTEST_ARGS+=("$arg")
                ;;
            *)
                PYTEST_ARGS+=("$arg")
                ;;
        esac
    done
    
    if [ ${#TEST_DIRS[@]} -eq 0 ]; then
        TEST_DIRS=("$TESTS_DIR")
    fi
    
    python3 -m pytest "${TEST_DIRS[@]}" "${PYTEST_ARGS[@]}"
}

show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --unit         Run only unit tests"
    echo "  --integration  Run only integration tests"
    echo "  --e2e          Run only end-to-end tests"
    echo "  --pytest       Run tests directly with pytest instead of using run_all_tests.py"
    echo "  -v, --verbose  Run tests in verbose mode"
    echo "  -x, --fail-fast Stop on first failure"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Run all tests"
    echo "  $0 --unit           # Run only unit tests"
    echo "  $0 --integration    # Run only integration tests"
    echo "  $0 --e2e            # Run only end-to-end tests"
    echo "  $0 --unit -v        # Run unit tests in verbose mode"
    echo "  $0 --pytest -v      # Run all tests with pytest directly in verbose mode"
    echo "  $0 --pytest --unit -v # Run unit tests with pytest directly in verbose mode"
}

main() {
    USE_PYTEST=false
    ARGS=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --pytest)
                USE_PYTEST=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                ARGS+=("$1")
                shift
                ;;
        esac
    done
    
    print_header "Technician Booking System Test Runner"
    
    check_python
    check_pytest
    check_termcolor
    
    print_header "Running Tests"
    
    if [ "$USE_PYTEST" = true ]; then
        print_info "Running tests directly with pytest..."
        run_pytest "${ARGS[@]}"
    else
        run_tests "${ARGS[@]}"
    fi
}

main "$@"