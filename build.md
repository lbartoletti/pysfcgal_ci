# Installation

## Build dependencies

The dependencies required for the build are : 
- gmp
- boost
- mpfr
- cmake
- cgal*

**Install SFCGAL with your package manager (apt, yum, pacman, pkg, etc) or with the sources if your system doesn't offer the package.*

Example for debian/ubuntu users

```shell
apt install -y cmake libgmp-dev libmpfr-dev libboost-dev libboost-timer-dev libboost-test-dev
```

## CGAL

To be done if your distribution does not provide the updated package (minimum `5.6`), otherwise you can skip this step.

```shell
wget "https://github.com/CGAL/cgal/releases/download/v5.6/CGAL-5.6.tar.xz" -O CGAL-5.6.tar.xz
tar xJf CGAL-5.6.tar.xz
```
Remember your path to CGAL - we'll need it later.
Example, path to CDAL: `/home/foo/CGAL-5.6`

## SFCGAL

Clone and place in the [sfcgal](https://gitlab.com/sfcgal/SFCGAL) folder

```shell
git clone git@gitlab.com:sfcgal/SFCGAL.git && cd SFCGAL
```

Path to CGAL is useful here.

```shell
cmake -GNinja -S . -B build -DSFCGAL_BUILD_TESTS=ON -DCGAL_DIR=/home/foo/CGAL-5.6
cmake --build build
```

The build includes can be found here: `/home/foo/SFCGAL/build/src`

## PySFCGAL

Build the python module

To start you have to clone and place yourself in [pysfcgal](https://gitlab.com/sfcgal/pysfcgal).

```shell
git clone git@gitlab.com:sfcgal/pysfcgal.git && cd pysfcgal
```

LDFLAGS: path we find `libSFCGAL.so`
CFLAGS: path where the build includes are located

```shell
env CFLAGS=-I/home/foo/SFCGAL/build/include LDFLAGS=-L/home/foo/SFCGAL/build/src python3 setup.py build install --user
```

```shell
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/foo/SFCGAL/build/src
```

### Add the environment to the system (valid only on Debian/Ubuntu)

Create the following file

```shell
touch /etc/ld.so.conf.d/sfcgal.conf
```

Then add in this file the link to the sources of the SFCGAL build

```text
/home/foo/SFCGAL/build/src
```