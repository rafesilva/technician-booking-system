from app.nlp.processor import NaturalLanguageProcessor
from app.nlp.utils import DateTimeParser
from app.db.database import reset_database


def test_combined_date_time():
    parser = DateTimeParser()
    result, desc = parser.parse_date_time("15 April 4:44 PM")
    print(f"15 April 4:44 PM -> {result}, {desc}")
    result, desc = parser.parse_date_time("April 15 4:44 PM")
    print(f"April 15 4:44 PM -> {result}, {desc}")
    reset_database()
    nlp = NaturalLanguageProcessor()
    print("\nTesting booking with combined date-time:")
    response1 = nlp.process_input("Book a plumber for 15 April 4:44 PM")
    print(f"Response: {response1}")
    print(f"User context: {nlp.user_context}")
    print("\nTesting another format:")
    reset_database()
    nlp = NaturalLanguageProcessor()
    response2 = nlp.process_input("Book a plumber for April 15 at 4:44 PM")
    print(f"Response: {response2}")
    print(f"User context: {nlp.user_context}")


if __name__ == "__main__":
    test_combined_date_time()
