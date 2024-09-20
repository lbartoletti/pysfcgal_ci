import pytest


@pytest.fixture
def c0():
    yield (0., 0., 0.)


@pytest.fixture
def c1():
    yield (1., 0., 0.)


@pytest.fixture
def c2():
    yield (0., 1., 0.)


@pytest.fixture
def c3():
    yield (0., 0., 1.)
