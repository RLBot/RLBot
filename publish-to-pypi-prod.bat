call prepare-python-distribution.bat
cd build/python-dist
py setup.py sdist upload
