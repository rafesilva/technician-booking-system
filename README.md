# Technician Booking System

Welcome to the Technician Booking System - a full-stack application that lets you book technicians using natural language.

![Technician Booking System](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103.1-blue)
![React](https://img.shields.io/badge/React-Latest-blue)

## What's This All About?

Frustrated with complicated booking systems? This application simplifies the process by allowing you to type natural language requests like "I need a plumber tomorrow afternoon" and get an immediate response. The system combines a React frontend, FastAPI backend, and natural language processing to create a conversational booking experience.

## Key Features

- **Natural Language Interface**: Type requests like "I need an electrician on Friday" and the system understands
- **Multi-specialty Support**: Book plumbers, electricians, HVAC technicians, and more
- **Conflict Prevention**: Automatically checks for and prevents double-bookings
- **Modern Web Interface**: Clean, responsive UI built with React
- **API Access**: Well-documented API for integration with other systems
- **Command-line Option**: Alternative terminal interface for those who prefer it
- **Intelligent Time Parsing**: Understands phrases like "tomorrow afternoon" or "next Tuesday"
- **Flexible Booking Management**: Easily reschedule or modify existing bookings
- **Context-Aware Conversations**: The system maintains context throughout your interaction

## System Architecture

The application is built on a three-tier architecture:

1. **Frontend**: React with Material UI components
2. **Backend**: FastAPI server for fast and efficient API responses
3. **Database**: In-memory database (for demonstration purposes)

## Project Structure

```
technician_booking_system/
├── app/                    # FastAPI backend application
│   ├── api/                # API routes and endpoints
│   │   ├── endpoints/      # Endpoint implementations
│   │   └── routes/         # Route definitions
│   ├── console/            # Command-line interface components
│   ├── core/               # Core application settings
│   ├── db/                 # Database models and operations
│   │   └── database.py     # Database connection and operations
│   ├── models/             # Data models and validation
│   ├── nlp/                # Natural language processing modules
│   │   ├── context/        # Context management for conversations
│   │   ├── handlers/       # Request handlers for different scenarios
│   │   ├── managers/       # Business logic managers
│   │   ├── models/         # NLP-specific models
│   │   ├── processors/     # Text processors and parsers
│   │   └── utils/          # NLP utility functions
│   ├── static/             # Static assets
│   ├── tests/              # Testing suite
│   │   ├── e2e/            # End-to-end tests
│   │   ├── integration/    # Integration tests
│   │   ├── unit/           # Unit tests
│   │   ├── mocks/          # Test mocks
│   │   ├── conftest.py     # Pytest configuration
│   │   ├── pytest.ini      # Pytest settings
│   │   └── utils.py        # Testing utilities
│   └── main.py             # Application entry point
├── booking-ui/             # React frontend application
│   ├── public/             # Public assets
│   ├── src/                # Source code
│   │   ├── components/     # React components
│   │   ├── services/       # API service integrations
│   │   ├── types/          # TypeScript type definitions
│   │   └── App.tsx         # Main React component
│   ├── package.json        # Node dependencies
│   └── build/              # Production build
├── utility scripts         # Helper scripts
├── requirements.txt        # Python dependencies
└── start scripts           # Application startup scripts
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 14 or higher
- npm 6 or higher
- pip (Python package manager)

Verify your system meets all requirements by running:

```bash
python check_requirements.py
```

### Backend Setup

Create a virtual environment for Python packages:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Frontend Setup

Navigate to the frontend directory:

```bash
cd booking-ui
```

Install Node.js packages:

```bash
npm install
```

## Running the Application

### Quick Start

Use the provided scripts for a streamlined setup:

```bash
# macOS/Linux
chmod +x start.sh  # Make executable (first time only)
./start.sh

# Windows
start.bat
```

This script handles:
1. Setting up the virtual environment
2. Installing dependencies
3. Starting the backend server
4. Starting the frontend
5. Opening the application in your browser

### Manual Start

If you prefer to start components individually:

#### Backend

```bash
# macOS/Linux
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Windows
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

#### Frontend

```bash
cd booking-ui
npm start
```

The UI will be available at http://localhost:3000

#### Console Application

```bash
# With activated virtual environment
python console_app.py
```

### Shutting Down

Press `Ctrl+C` in the terminal to stop the application.

### Troubleshooting

If you encounter issues:

1. Run `python check_requirements.py` to verify prerequisites
2. Check that ports 8000 and 3000 are available
3. For frontend issues, try running `npm install` manually
4. For backend issues, reinstall dependencies:
   ```bash
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

## Usage Guide

### Web Application

The web interface provides a chat interface where you can:

1. **Create Bookings**: "I need a plumber tomorrow at 2pm"
2. **Check Bookings**: "What appointments do I have?"
3. **Update Bookings**: "Move my appointment to Monday at 3pm"
4. **Cancel Bookings**: "Cancel my plumber appointment"

Your bookings are displayed in a list on the left side for easy reference.

### API Documentation

Access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Debug Endpoints

For troubleshooting purposes:
- `/api/v1/nlp/debug/reset-context/{session_id}`: Reset a chat session
- `/api/v1/nlp/debug/context/{session_id}`: View the current conversation context

## Conversational Features

The system understands natural language and maintains context throughout conversations.

### Starting a Conversation

You can begin with a greeting or a direct request:
- "Hello" - The system will greet you
- "I need a plumber" - Begins the booking process

### Booking Process

A typical booking conversation:

1. **User**: "I need an electrician tomorrow"
2. **System**: "What time would you like to book the electrician for tomorrow?"
3. **User**: "3 pm"
4. **System**: *Checks for available electricians*
5. **System**: "For 3:00 PM, we have these Electricians available: 1. Franky Flay, 2. Sarah Johnson..."
6. **User**: "Franky Flay"
7. **System**: "Your booking with Franky Flay is confirmed for tomorrow at 3:00 PM. Your booking ID is 4."

### Flexible Conversations

The system handles changes during the conversation:

- "Actually, I need a plumber instead" - Changes the specialty
- "Never mind" - Cancels the current process
- If there's a scheduling conflict, the system offers alternatives

### Managing Bookings

You can manage existing bookings with natural commands:

1. **View Bookings**:
   - "Show my bookings"
   - "What appointments do I have?"

2. **Modify Bookings**:
   - "Reschedule booking 3 to Friday"
   - "Move my plumber appointment to next week"

3. **Cancel Bookings**:
   - "Cancel booking 2"
   - "I don't need that electrician appointment anymore"

### Time Input Handling

The system accepts various time formats:

1. **Standard Times**:
   - "3:14 PM", "5:50 AM", etc.

2. **Ambiguous Times**:
   - The system will request clarification for ambiguous times (like "6 o'clock")
   - For non-ambiguous times, reasonable defaults are applied

3. **Natural Language Times**:
   - "Tomorrow morning"
   - "Next Friday afternoon"
   - "3 in the evening"

4. **Flexible Inputs**:
   - "April 16 at 5" or "April 16 5 AM"

### Common Commands

Examples of effective commands:

| Purpose | Sample Commands |
|--------|------------------|
| Book a technician | "I need an electrician on Friday at 3pm" |
|  | "Schedule a plumber for tomorrow morning" |
|  | "Book HVAC service next Tuesday at 10" |
| Check bookings | "What are my bookings?" |
|  | "Show me my appointments" |
|  | "What's scheduled?" |
| Update a booking | "Update booking 3 to next week" |
|  | "Change my appointment to 4pm" |
|  | "Move my booking to tomorrow" |
| Cancel a booking | "Cancel booking 3" |
|  | "Delete my plumber appointment" |
|  | "Remove my booking" |

## System Constraints

- Bookings are one hour in duration
- Technicians cannot be double-booked
- Booking times are on the hour (2:00 PM, not 2:30 PM)
- 12-hour time format with AM/PM designation is used

## Sample Data

The system includes these example bookings:

| ID | Technician | Specialty | Date & Time |
|----|------------|-----------|-------------|
| 1 | Nicolas Woollett | Plumber | 15/10/2022 at 10:00 AM |
| 2 | Franky Flay | Electrician | 16/10/2022 at 6:00 PM |
| 3 | Griselda Dickson | Welder | 18/10/2022 at 11:00 AM |

## Testing

The application includes comprehensive test coverage.

### Using the Test Script

```bash
# Run all tests
./run_tests.sh

# Run unit tests only
./run_tests.sh --unit

# Run integration tests only
./run_tests.sh --integration

# Run end-to-end tests only
./run_tests.sh --e2e

# Run with verbose output
./run_tests.sh -v

# Run with pytest directly
./run_tests.sh --pytest
```

### Using pytest Directly

```bash
# All tests
python -m pytest app/tests

# Specific test categories
python -m pytest app/tests/unit/
python -m pytest app/tests/integration/
python -m pytest app/tests/e2e/

# Specific test file
python -m pytest app/tests/unit/test_ampm_clarification.py

# Specific test function
python -m pytest app/tests/unit/test_ampm_clarification.py::TestAMPMClarification::test_ampm_clarification

# Verbose mode
python -m pytest -v
```

### Test Dependencies

Required packages:
- pytest
- termcolor (for colored output)

The test script installs these automatically, or you can install them manually:

```bash
pip install pytest termcolor
```