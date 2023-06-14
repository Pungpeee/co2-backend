
#66 893055323
def reformat_phone_number(number):
    #TODO : @Jade for next phase use pypl phone number lib for track all phone number aroung the world
    pl = len(number)
    if pl == 11:
        if number[:2] == '66':
            return number
    elif pl == 10:
        if number[:1] == '0':
            return '66' + number[1:]
    return None
