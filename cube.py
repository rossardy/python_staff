number = int(raw_input("Input some numbers: "))
def cube(number):
    return number*number*number
    
def by_three(number):
    if cube(number)==number*number*number:
        print number
    else:
        return False

by_three(number)
