#! /usr/bin/python3
# -*- coding: utf8 -*-

import sys

def to2(x):
    rest = ''
    while x >= 1:
        rest = rest + str(x % 2)
        x //= 2
    print(rest)
        
    
    
def from2(x):
    val = 0
    x = x[::-1]
    j = 0
    for i in x:
        val += int(i) * 2**j
        j += 1
    print(val)

if __name__ == "__main__":
    n = int(sys.argv[1])
    x = str(sys.argv[2])
    
    to2(n)
    from2(x)
