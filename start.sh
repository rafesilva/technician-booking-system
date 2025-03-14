#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Technician Booking System${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is not installed. Please install Python 3 to run this application.${NC}"
    exit 1
fi

chmod +x start.py

python3 start.py 