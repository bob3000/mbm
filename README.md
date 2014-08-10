# Micro Bog Magic

[![Build Status](https://travis-ci.org/bob3000/mbm.svg?branch=master)](https://travis-ci.org/bob3000/mbm)
[![Coverage Status](https://img.shields.io/coveralls/bob3000/mbm.svg)](https://coveralls.io/r/bob3000/mbm)

Micro Bog Magic is a multi micro blog client written in *Python3* which is able
to manage several accounts on various micro blogging platforms. The project is
currently still under heavy development.

## Table of contents

- [Features](#features)
    - [Current](#current)
    - [Future](#future)
- [Getting started](#getting-started)
    - [Requirements](#requirements)
    - [Bootstrap](#bootstrap)
- [Documentation](#documtation)
    - [Command line help](#command-line-help)
    - [Manpage](#manpage)
    - [Doctest](#doctest)
- [Hacking](#hacking)
    - [Makefile](#makefile)
    - [Running tests](#running-test)
    - [Cleaning up](#cleaning-up)
- [Bugs](#bugs)

## Features

### Current

    - post updates to twitter
    - post photos to twitter

### Future

    - tumblr support
    - read timelines and actively listen for updates
    - follower/friends management
    - facebook timeline updates support
    - other micro blogs

## Getting started

*Note:* This software is still in an early alpha status. Therefor I only
describe an installation in a sandboxed environment for development purpose.

### Requirements

- [VirtualBox](https://www.virtualbox.org)
- [Vagrant](http://www.vagrantup.com/)

### Bootstrap

After cloning the project enter the project directory and type `vagrant up`.
Wait until everything is setup and enter the sandbox with `vagrant ssh`.

## Documentation

### Command line help

Inside the vagrant box type `mbm --help` to get an overview of the command line
interface.

### Manpage

Inside the vagrant box type `man mbm` to open the manpage. At the moment the
manpage is still work in progress.

### Doctest

The projects integration test is supposed to serve a documentation purpose as
well as blackbox testing. The file can be found here:
[integration\_test.md](mbm/tests/integration_test.md)

## Hacking

Contributions are welcome! Please have a look at
[CONTRIBUTING.md](CONTRIBUTING.md) before you start hacking. Thanks!

### Makefile

There is a Makefile inside the project root directory which server as a central
entry point for developing tasks like running tests or package building. All
tasks described inside the Makefile are *supposed to be run from inside the
sandbox* in order to to run properly and to keep your host system clean.

### Running the tests

The following command will run the unittests as well as the integration test.

    make tests

Code coverage can be figured out with

    make coverage

This will create a `htmlcov` directory in the project root. Open the
`index.html` inside this folder to see the coverage report.

### Cleaning up

Run the following command to safely delete all temporary files which are
are created while running test and building packages.

    make clean

## Bugs

I encourage you to report bugs in github issues.
