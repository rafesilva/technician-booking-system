from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class ContextHandler(ABC):
    @abstractmethod
    def create_default_context(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def reset_context(self, user_context: Dict, fields: Optional[List[str]] = None) -> None:
        pass
