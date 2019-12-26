

def reverse_lookup(dic, value):
    for key in dic:
        if dic[key] == value:
            return key
    return None


