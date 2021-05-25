import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os", "tkinter"]}

base = None

setup(  name = "main",
        version = "0.1",
        description = "GUI2 for T-schakt",
        options = {"build_exe": build_exe_options},
        executables = [Executable("main.py", base=base)])