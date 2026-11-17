import setuptools


def test_find_packages_excludes_tests():
    packages = setuptools.find_packages(exclude=["tests", "tests.*"])
    assert "tests" not in packages
    assert not any(package.startswith("tests") for package in packages)
