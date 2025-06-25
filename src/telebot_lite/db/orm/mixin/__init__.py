import os

for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file != os.path.basename(__file__):
        name = file[: file.find(".py")]
        exec(f"from .{name} import *")