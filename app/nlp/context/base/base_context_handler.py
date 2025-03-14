from typing import Dict, List, Optional, Any
from app.nlp.constants import DEFAULT_USER_CONTEXT
from app.nlp.context.interfaces.context_handler import ContextHandler


class BaseContextHandler(ContextHandler):
    def create_default_context(self) -> Dict[str, Any]:
        return DEFAULT_USER_CONTEXT.copy()

    def reset_context(self, user_context: Dict, fields: Optional[List[str]] = None) -> None:
        if fields:
            for field in fields:
                if field in DEFAULT_USER_CONTEXT:
                    user_context[field] = DEFAULT_USER_CONTEXT[field]
        else:
            user_context.clear()
            user_context.update(DEFAULT_USER_CONTEXT.copy())
