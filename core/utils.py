import os
import uuid

ALLOWED_AVATAR_EXTENSIONS = ("jpg", "jpeg", "png", "gif", "webp")
MAX_AVATAR_SIZE_MB = 5


def upload_to(folder, filename):
    # Unpredictable path for uploaded avatars
    ext = os.path.splitext(filename)[1].lower().lstrip(".") or "bin"
    new_name = f"{uuid.uuid4().hex}.{ext}"
    # Some sort of sharding by 2-char prefix to avoid huge flat directories
    return os.path.join(folder, new_name[:2], new_name)
