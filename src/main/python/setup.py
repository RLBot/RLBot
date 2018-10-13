import setuptools

__version__ = None  # This will get replaced when reading version.py

exec(open('rlbot/version.py').read())

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name='rlbot',
    packages=setuptools.find_packages(),
    install_requires=['psutil', 'inputs', 'PyQt5', 'py4j'],
    version=__version__,
    description='A framework for writing custom Rocket League bots that run offline.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='RLBot Community',
    author_email='rlbotofficial@gmail.com',
    url='https://github.com/RLBot/RLBot',
    keywords=['rocket-league'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    package_data={
        'rlbot': [
            '**/*.dll',
            '**/*.exe',
            '**/*.json',
            'gui/design/*.ui',
            '**/*.png',
            '**/*.md',
            'utils/prediction/*.dat'
        ]
    },
)
