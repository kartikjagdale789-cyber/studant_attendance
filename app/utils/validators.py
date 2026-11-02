# app/utils/validators.py
import re

def validate_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email.strip()))

def validate_marks(marks: float, max_marks: float = 100.0) -> tuple[bool, str]:
    try:
        m = float(marks)
        mx = float(max_marks)
    except (ValueError, TypeError):
        return False, "Marks and maximum marks must be numeric values."

    if mx <= 0:
        return False, "Maximum marks must be greater than zero."
    if m < 0:
        return False, "Marks cannot be negative."
    if m > mx:
        return False, f"Marks ({m}) cannot exceed maximum marks ({mx})."
    return True, ""

def validate_roll_number(roll: str) -> bool:
    if not roll or not isinstance(roll, str):
        return False
    return len(roll.strip()) >= 2

def validate_username(username: str) -> bool:
    if not username or not isinstance(username, str):
        return False
    return len(username.strip()) >= 3 and username.strip().isalnum()
