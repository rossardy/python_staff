#! /usr/bin/python3
# -*- coding: utf8 -*-

def e_bekon(exp):
    a = exp.replace(' ', '').lower()
    out = ''
    for i in a:
        if i.isalpha():
            out = out + KEY[ord(i)-97:ord(i)-92] + ' '
    print('Encrypted phrase is: {}'.format(out))
    return True
    
def d_bekon(exp):
    l = exp.split()
    out = ''
    for i in l:
        num = KEY.find(i) + 97
        alpha = chr(num)
        out = out + alpha
    print('Decrypted phrase is: {}'.format(out))
    return True
        
    

KEY = 'aaaaabbbbbabbbaabbababbaaababaab'
will = input('Would you like encrypt or decrypt? Y/N ?')
if will == 'Y':
    exp = input('Please input expresion for enciphering by Bekon cipher :')
    e_bekon(exp)
if will == 'N':
    exp = input('Please input expresion for deciphering by Bekon cipher :')
    d_bekon(exp)
