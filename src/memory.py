class ConversationMemory:
    """Simple in-memory conversation state for the airport copilot."""

    def __init__(self):
        self.last_airport = None
        self.history = []

    def update(self, user_message: str, airport_code: str | None = None):
        """Store the conversation turn and update the active airport."""

        if airport_code:
            self.last_airport = airport_code.upper()

        self.history.append(
            {
                "user": user_message,
                "airport_code": self.last_airport,
            }
        )

    def resolve_airport(self, airport_code: str | None = None) -> str:
        """Resolve an explicit airport or fall back to conversation context."""

        if airport_code:
            return airport_code.upper()

        if self.last_airport:
            return self.last_airport

        raise ValueError("No airport context is available.")

    def get_history(self) -> list[dict]:
        """Return the conversation history."""

        return self.history
