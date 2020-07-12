import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name='rlbot_legacy_gui',
    packages=setuptools.find_packages(),
    install_requires=[
        'rlbot',
        'PyQt5==5.15.0',
    ],
    version='1.0.0',
    description='An old UI for RLBot built on PyQt5. Currently deprecated in favor of RLBotGUI.',
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
        'rlbot_legacy_gui': [
            '**/*.json',
            'design/*.ui',
            '**/*.png',
            '**/*.md',
        ]
    },
)
