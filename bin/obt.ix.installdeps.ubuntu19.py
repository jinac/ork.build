#!/usr/bin/env python3

import os

deplist =  ["libboost-dev","gcc-8","gcc-9"]
deplist += ["libboost-filesystem-dev","libboost-system-dev","libboost-thread-dev"]
deplist += ["libglfw3-dev","libflac++-dev","scons","git"]
deplist += ["rapidjson-dev","graphviz","doxygen","clang","libtiff-dev"]
deplist += ["portaudio19-dev", "pybind11-dev"]
deplist += ["libpng-dev","clang-format","python-dev"]
deplist += ["iverilog","nvidia-cg-dev","nvidia-cuda-dev", "nvidia-cuda-toolkit"]
deplist += ["libxcb-cursor-dev","libxcb-proto-dev","libxcb-keysyms1-dev"]
deplist += ["libxcb-xkb-dev","libxkbcommon-x11-dev"]
deplist += ["libgtkmm-3.0-dev"]

for item in deplist:
    os.system("sudo apt install %s" % item)
