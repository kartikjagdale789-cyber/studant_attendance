# app/utils/helpers.py
import hashlib
import os
from datetime import datetime
from config.constants import GRADE_BOUNDARIES

try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False

def hash_password(plain_password: str) -> str:
    """Hash password using bcrypt if available, otherwise secure SHA-256 with salt."""
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)

    if _HAS_BCRYPT:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')
    else:
        # Fallback SHA-256 with random salt
        salt = os.urandom(16).hex()
        digest = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
        return f"sha256${salt}${digest}"

def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    if not plain_password or not password_hash:
        return False

    if password_hash.startswith("sha256$"):
        parts = password_hash.split("$")
        if len(parts) == 3:
            salt, digest = parts[1], parts[2]
            computed = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
            return computed == digest

    if _HAS_BCRYPT:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False

    return False

def calculate_percentage(obtained: float, total: float) -> float:
    """Calculate percentage safely."""
    if total <= 0:
        return 0.0
    return round((obtained / total) * 100.0, 2)

def get_grade(percentage: float) -> tuple[str, str]:
    """Return (Grade, Description) based on percentage."""
    for threshold, grade, desc in GRADE_BOUNDARIES:
        if percentage >= threshold:
            return grade, desc
    return "F", "Fail"

def now_iso() -> str:
    """Current timestamp in ISO format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def today_str() -> str:
    """Today's date in YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")
