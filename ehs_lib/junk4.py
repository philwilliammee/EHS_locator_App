'''
Created on Mar 17, 2015

@author: Phil Williammee
'''
a = 'Williammee\Desktop\EHS_locator\test'
a = repr(a).replace("\\",",")[1:-1]#remove backslash
a = a.split(',')
print a[-1]
