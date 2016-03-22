#!/bin/bash

pip install numpy
pip install pandas
pip install -e git+https://github.com/berkerpeksag/astor.git#egg=astor
pip install -e git+https://github.com/dalejung/asttools#egg=astools
pip install -e git+https://github.com/dalejung/earthdragon#egg=earthdragon
pip install .
