STATUS_MESSAGES = {
    "added": "Article added successfully.",
    "duplicate": "Article already exists.",
    "download_failed": "Article download failed.",
    "extraction_failed": "Article extraction failed.",
    "deleted": "Article deleted successfully.",
    "not_deleted": "Article deletion failed."
}


def get_message(message_id: str) -> str | None:
    return STATUS_MESSAGES.get(message_id)