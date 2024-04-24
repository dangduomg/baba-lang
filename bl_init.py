# babalang initialization script

import sys

if __name__ == '__main__':
    print('this is not intended to run as a standalone script')
    sys.exit()
    
    
import time
import operator

import info
from state import State
from intr_classes import PythonWrapper


state = State()


def import_native(name):
    return lambda f: state.new_var(name, PythonWrapper(f))

# basic functions

import_native('print')(print)
import_native('exit')(sys.exit)
import_native('input')(input)
import_native('sleep')(time.sleep)
import_native('now')(time.asctime)
import_native('version')(lambda: info.VERSION)
import_native('about')(lambda: print(info.ABOUT))

# arithmetic functions

import_native('bit_and')(operator.and_)
import_native('bit_or')(operator.or_)
import_native('bit_xor')(operator.xor)
import_native('bit_not')(operator.inv)
import_native('bit_lsh')(operator.lshift)
import_native('bit_rsh')(operator.rshift)

# import python functions

@import_native('py_function')
def _py_function(m, f):
    module = __import__(m)
    return PythonWrapper(getattr(module, f))

# generic collection operations

import_native('length')(len)
import_native('has')(operator.contains)
import_native('delete_')(operator.delitem)

# list operations

import_native('list_push')(list.append)
import_native('list_pop')(list.pop)

# dict operations

import_native('dict_pairs')(dict.items)
import_native('dict_pop')(dict.pop)