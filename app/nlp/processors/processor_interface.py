from typing import Dict, Optional


class ProcessorInterface:
    def process_input(self, text: str, user_context: Optional[Dict] = None) -> str:
        raise NotImplementedError("Subclasses must implement process_input")
