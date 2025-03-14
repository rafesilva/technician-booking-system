from app.db.database import get_all_bookings
from app.nlp.processor import NaturalLanguageProcessor


def run_console_app():
    print("Welcome to the Technician Booking System!")
    print("I can help you schedule appointments with our technicians.")
    print("Type 'quit' to exit.")
    nlp = NaturalLanguageProcessor()
    bookings = get_all_bookings()
    if bookings:
        print("\n> I see you have existing bookings. Would you like to see your current bookings or schedule a new appointment?")
        nlp.user_context["booking_in_progress"] = True
    else:
        print("\n> How can I help you today? You can book a technician, check your booking ID, or cancel a booking.")
    while True:
        user_input = input("\nEnter your message or 'quit' to exit: ")
        if user_input.lower() == 'quit':
            print("Thank you for using the Technician Booking System. Goodbye!")
            break
        response = nlp.process_input(user_input)
        print(f"> {response}")
