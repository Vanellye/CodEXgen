# Auto-generated module: UserProfile
from typing import Any

class UserProfile(SecureEntity):
    def __init__(self, data: dict[str, Any]):
        super().__init__()
        self.user_id = data.get("user_id", None)
        self.username = data.get("username", None)
        self.clearance_level = data.get("clearance_level", None)
        self.active_status = data.get("active_status", None)

    def __repr__(self) -> str:
        return f"<UserProfile attributes=['user_id', 'username', 'clearance_level', 'active_status']>"
