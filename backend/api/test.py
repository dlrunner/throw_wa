import ctypes
import os

if os.name == "nt":
    libc_name = "msvcrt.dll"
else:
    import ctypes.util
    libc_name = ctypes.util.find_library("c")

if libc_name is None:
    raise ValueError("Could not find libc library")

libc = ctypes.CDLL(libc_name)