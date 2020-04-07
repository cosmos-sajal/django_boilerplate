import re


def validate(regex, string):
    print(re.search(regex, string))
    return True if re.search(regex, string) is not None else False


def is_valid_email(email):
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    return validate(regex, email)


def is_strong_password(password):
    regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"

    return validate(regex, password)


def is_valid_mobile_number(mobile_number):
    regex = r"^[0-9]{10}$"

    return validate(regex, mobile_number)
