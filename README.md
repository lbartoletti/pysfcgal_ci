# PySFCGAL

An official wrapper around the SFCGAL library for Python in the style of Shapely.

http://www.sfcgal.org/

This modules is in the *very* early stages of development!

## Installation

Install SFCGAL with you package manager (apt, yum, pacman, pkg, etc)

And build the module with:

On Unix-like:
```
env CFLAGS=-Ipath\to\include LDFLAGS=-Lpath\to\libs python3 setup.py build install --user
```

On Windows:
```
$Env:INCLUDE='path\to\include'
$Env:LIB='path\to\libs'
python3.exe setup.py build install --user
```

where `path\to\include` is your include path where SFCGAL is and `path\to\lib` the library path (.so, .dll) where SFCGAL is.

## Credits
 
Initial work from https://github.com/snorfalorpagus/pysfcgal/
