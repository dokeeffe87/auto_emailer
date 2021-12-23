"""
  ___        _          _____                _ _
 / _ \      | |        |  ___|              (_) |
/ /_\ \_   _| |_ ___   | |__ _ __ ___   __ _ _| | ___ _ __
|  _  | | | | __/ _ \  |  __| '_ ` _ \ / _` | | |/ _ \ '__|
| | | | |_| | || (_) | | |__| | | | | | (_| | | |  __/ |
\_| |_/\__,_|\__\___/  \____/_| |_| |_|\__,_|_|_|\___|_|


V1.0.0: Class for defining and creating the character personas.  It should also auto-generate email text fitting the character persona. You don't need to use this, this is just for fun
"""

import os
import sys


class Persona:
    def __init__(self, name, signature, text):
        self.name = name
        self.signature = signature
        self.text = text

