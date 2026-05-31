import string

chars = string.ascii_letters + string.digits

def encode_base62(num):
    if num == 0:
        return chars[0]

    result = ""

    while num:
        num, rem = divmod(num, 62)
        result = chars[rem] + result

    return result