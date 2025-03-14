from app.tests.utils import reset_database, generate_session_id, send_request, print_header
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def test_simple():
    print_header("Simple Test")
    reset_database()
    session_id = generate_session_id()
    response = send_request(session_id, "Hello")
    print(f"Response: {response}")
    assert response, "Should get a response"
    print("Test passed!")
    return True


if __name__ == "__main__":
    test_simple()
