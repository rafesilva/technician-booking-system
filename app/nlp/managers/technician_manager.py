import random
from typing import List
from app.nlp.constants import TECHNICIANS


class TechnicianManager:
    @classmethod
    def get_available_technicians(cls, specialty: str) -> List[str]:
        return TECHNICIANS.get(specialty, TECHNICIANS["Technician"])

    @classmethod
    def assign_technician(cls, specialty: str) -> str:
        available = cls.get_available_technicians(specialty)
        return random.choice(available)

    @classmethod
    def get_available_technicians_static(cls, specialty: str) -> List[str]:
        return cls.get_available_technicians(specialty)
