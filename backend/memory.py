
from uuid import uuid4

# Maximum number of previous messages retained
MAX_HISTORY = 10

# Store conversation histories
conversations = {}

# Track the total number of messages per conversation
message_totals = {}


def create_conversation():
    """Create a new conversation with a unique ID."""

    conversation_id = str(uuid4())

    conversations[conversation_id] = []
    message_totals[conversation_id] = 0

    return conversation_id


def get_history(conversation_id):
    """Return a copy of the conversation history."""

    history = conversations.get(conversation_id)

    if history is None:
        return None

    return [message.copy() for message in history]


def save_message(conversation_id, role, content):
    """Save a message and truncate older history."""

    if conversation_id not in conversations:
        raise ValueError("Conversation not found.")

    if role not in ("user", "model"):
        raise ValueError("Invalid message role.")

    conversations[conversation_id].append({
        "role": role,
        "content": content
    })

    message_totals[conversation_id] += 1

    # Retain only the latest 10 messages
    conversations[conversation_id] = (
        conversations[conversation_id][-MAX_HISTORY:]
    )


def get_memory_info(conversation_id):
    """Return memory statistics for the frontend."""

    history = conversations.get(conversation_id)

    if history is None:
        return None

    retained = len(history)
    total = message_totals[conversation_id]

    return {
        "retained_messages": retained,
        "max_messages": MAX_HISTORY,
        "total_messages": total,
        "truncated_messages": total - retained,
        "truncation_active": total > retained
    }
