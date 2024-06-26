# babalang initialization script

import sys

if __name__ == '__main__':
    print('this is not intended to run as a standalone script')
    sys.exit()
    
    
import time
import operator

import info
from state import State
import intr_classes


state = State()


def import_native(name):
    return lambda f: state.new_var(name, intr_classes.PythonWrapper(f))

def import_native_pure(name):
    return lambda f: state.new_var(name, intr_classes.PythonPureWrapper(f))

# basic functions

import_native('exit')(sys.exit)
import_native('input')(input)
import_native('sleep')(time.sleep)
import_native('now')(time.asctime)
import_native('version')(lambda: info.VERSION)
import_native('about')(lambda: print(info.ABOUT))

@import_native_pure('print')
def _print(v):
    print(v.print_repr())
    return intr_classes.Null()

# import python functions

@import_native('py_function')
def _py_function(m, f):
    module = __import__(m)
    return intr_classes.PythonWrapper(getattr(module, f))

# generic collection operations

import_native('length')(len)
import_native('has')(operator.contains)

# list operations

@import_native_pure('list_push')
def _list_push(lst, item):
    lst.elems.append(item)
    return intr_classes.Null()

@import_native_pure('list_pop')
def _list_pop(lst, i):
    return lst.elems.pop(i)

# dict operations

import_native('dict_pairs')(dict.items)

@import_native_pure('dict_pop')
def _dict_pop(dct, k):
    return dct.elems.pop(k)

@import_native_pure('dict_pop_pair')
def _dict_pop_pair(dct):
    return dct.elems.popitem()

# type conversions

import_native('int')(int)
import_native('float')(float)
import_native('bool')(bool)

@import_native_pure('str')
def _str(v):
    return intr_classes.String(v.code_repr())