from app.db.database import create_booking, delete_booking, get_all_bookings, reset_database
from app.models.booking import BookingCreate
from app.nlp.handlers.conflict_checker import BookingConflictChecker
import unittest
import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestConflictChecker(unittest.TestCase):
    def setUp(self):
        reset_database()
        self.base_date = datetime(2030, 1, 15, 10, 0)
        self.technician_name = "Test Technician"
        self.specialty = "Test Specialty"
        booking_create = BookingCreate(
            technician_name=self.technician_name,
            specialty=self.specialty,
            booking_time=self.base_date
        )
        self.booking_id = create_booking(booking_create)

    def tearDown(self):
        reset_database()

    def test_exact_time_conflict_same_technician(self):
        conflict = BookingConflictChecker.check_conflict(self.base_date)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict["booking_id"], self.booking_id)
        self.assertEqual(conflict["technician_name"], self.technician_name)

    def test_no_conflict_different_technician(self):
        different_tech_time = self.base_date
        conflict = BookingConflictChecker.check_conflict(different_tech_time)
        booking_create = BookingCreate(
            technician_name="Different Technician",
            specialty=self.specialty,
            booking_time=different_tech_time
        )
        try:
            create_booking(booking_create)
            success = True
        except ValueError:
            success = False
        self.assertTrue(success)

    def test_overlap_start_conflict(self):
        overlap_time = self.base_date + timedelta(minutes=30)
        conflict = BookingConflictChecker.check_conflict(overlap_time)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict["booking_id"], self.booking_id)

    def test_overlap_end_conflict(self):
        overlap_time = self.base_date + timedelta(minutes=45)
        conflict = BookingConflictChecker.check_conflict(overlap_time)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict["booking_id"], self.booking_id)

    def test_no_conflict_adjacent_slots(self):
        adjacent_time = self.base_date + timedelta(hours=1)
        conflict = BookingConflictChecker.check_conflict(adjacent_time)
        self.assertIsNone(conflict)

    def test_no_conflict_different_day(self):
        different_day = self.base_date + timedelta(days=1)
        conflict = BookingConflictChecker.check_conflict(different_day)
        self.assertIsNone(conflict)

    def test_multiple_technician_bookings(self):
        technicians = ["Tech A", "Tech B", "Tech C"]
        times = [
            self.base_date,
            self.base_date + timedelta(minutes=30),
            self.base_date + timedelta(minutes=45)
        ]
        for i, (tech, time) in enumerate(zip(technicians, times)):
            booking_create = BookingCreate(
                technician_name=tech,
                specialty=self.specialty,
                booking_time=time
            )
            try:
                create_booking(booking_create)
                success = True
            except ValueError:
                success = False
            self.assertTrue(success, f"Should be able to book {tech} at {time}")

    def test_exclude_booking_id(self):
        conflict = BookingConflictChecker.check_conflict(
            self.base_date,
            exclude_booking_id=self.booking_id
        )
        self.assertIsNone(conflict)

    def test_conflict_across_hour_boundary(self):
        booking_time = self.base_date + timedelta(minutes=45)
        conflict_time = self.base_date + timedelta(minutes=90)
        booking_create = BookingCreate(
            technician_name=self.technician_name,
            specialty=self.specialty,
            booking_time=booking_time
        )
        create_booking(booking_create)
        conflict = BookingConflictChecker.check_conflict(conflict_time)
        self.assertIsNotNone(conflict)

    def test_sequential_bookings(self):
        times = [
            self.base_date + timedelta(hours=i)
            for i in range(3)
        ]
        for i, time in enumerate(times):
            booking_create = BookingCreate(
                technician_name=self.technician_name,
                specialty=self.specialty,
                booking_time=time
            )
            try:
                create_booking(booking_create)
                success = True
            except ValueError:
                success = False
            self.assertTrue(success, f"Should be able to book sequential slot {i}")


if __name__ == "__main__":
    unittest.main()
