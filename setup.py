from setuptools import setup

setup(
    name="mbm",
    version="0.0.0",
    license="GNU GPL v3",
    packages=[
        "mbm",
        "mbm.lib",
        "mbm.provider",
    ],
    test_suite="mbm",
    install_requires={
    },
    entry_points={
        "console_scripts": [
            "mbm = mbm.__main__:main",
        ],
    },
    data_files=[
        ('/usr/share/man/man1', ['man/mbm.1.gz']),
        ('/usr/share/bash-completion/completions', ['completion/mbm']),
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Topic :: System :: Archiving :: Packaging",
        "Intended Audience :: End Users/Desktop",
    ],
)
