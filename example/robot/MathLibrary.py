from ctypes import CDLL, c_int
import os


class MathLibrary:
    def __init__(self):
        lib_path = os.path.join(os.path.dirname(__file__), "../build/libmath.so")
        self.lib = CDLL(lib_path)

    def add(self, a: int, b: int) -> int:
        return self.lib.add(c_int(a), c_int(b))

    def multiply(self, a: int, b: int) -> int:
        return self.lib.multiply(c_int(a), c_int(b))
