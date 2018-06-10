import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name='rlbot',
    packages=setuptools.find_packages(),
    install_requires=['psutil', 'inputs', 'PyQt5'],
    version='0.0.11',
    description='A framework for writing custom Rocket League bots that run offline.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Tyler Arehart',
    author_email='rlbotofficial@gmail.com',
    url='https://github.com/RLBot/RLBot',
    keywords=['rocket-league'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    package_data={
        'rlbot': ['**/*.dll', '**/*.exe', '**/*.json', 'gui/design/*.ui', '**/*.png']
    },
)
