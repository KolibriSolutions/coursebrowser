import re

def validate_course_code(code):
    return re.match(r'\b([A-Z0-9\-]{4,14})\b', code)