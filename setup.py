from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "excludes": ["tkinter", "unittest"],
    "zip_include_packages": ["encodings", "PySide6", "shiboken6"],
}

setup(
    name="DDNetToolBox",
    version="1.0.0",
    description="DDNetToolBox",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="gui")],
)
