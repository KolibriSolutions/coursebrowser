

#TODO: use regex here?
def validate_course_code(code):
    try:
        int(code[0])
    except ValueError:
        return False
    return len(code) <= 6