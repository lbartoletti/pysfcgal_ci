from subprocess import PIPE, CalledProcessError, run

import pytest

from pysfcgal.sfcgal import Triangle


def test_wrap_geom_segfault():
    segfault_code = """
from pysfcgal.sfcgal import Triangle
triangle = Triangle([(0, 0, 0), (1, 0, 0), (0, 1, 0)])
for t in [triangle, triangle]:
    triangle = Triangle.from_sfcgal_geometry(triangle._geom)
    """
    proc = run(f"python3 -c '{segfault_code}'", shell=True, stdout=PIPE, stderr=PIPE)
    assert proc.stderr == b"Segmentation fault (core dumped)\n"
    with pytest.raises(CalledProcessError):
        proc.check_returncode()


def test_wrap_geom():
    triangle = Triangle([(0, 0, 0), (1, 0, 0), (0, 1, 0)])
    for t in [triangle, triangle]:
        triangle = triangle.wrap()
    assert True  # Just to confirm that the code works fine and no segfault arises
