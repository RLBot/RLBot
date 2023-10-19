import setuptools

__version__ = None  # This will get replaced when reading version.py

exec(open('rlbot/version.py').read())

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name='rlbot',
    packages=setuptools.find_packages(),
    install_requires=[
        'flatbuffers==1.12',
        'psutil==5.*',
        'inputs',
        'websockets',
        'dataclasses',  # Python 3.6 compatibility
        'webdriver_manager',  # For scratch bots
        'selenium==4.*',  # For scratch bots
        'requirements-parser',
        'docopt',  # Used by standalone agents
    ],
    version=__version__,
    description='A framework for writing custom Rocket League bots that run offline.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='RLBot Community',
    author_email='rlbotofficial@gmail.com',
    url='https://github.com/RLBot/RLBot',
    keywords=['rocket-league'],
    license='MIT License',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    package_data={
        'rlbot': [
            "**/*.csv",
            '**/*.json',
            '**/*.png',
            '**/*.md',
            'dll/**/*',
            'dll/*',
            'utils/structures/*.pyi',
            'py.typed',
            'matchconfig/psyonix_presets/*.cfg'
        ]
    },
)
