from math import pow, sqrt
import datetime


def phone_number_check(number):
    if number.startswith("+7") and len(number) == 12 and number[1:].isdigit():
        return True
    return False


def link_to_profile_check(link):
    starts = ["https://vk.com/", "https://facebook.com/", "https://linkedin.com/", "https://instagram.com/"]
    for start in starts:
        if link.startswith(start):
            return True
    return False
