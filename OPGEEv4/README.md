[![Build Status](https://travis-ci.com/Stanford-EAO/OPGEEv4.svg?token=qVku1FaPpCm5v3f1zYpw&branch=master)](https://travis-ci.com/Stanford-EAO/OPGEEv4)
[![codecov](https://codecov.io/gh/Stanford-EAO/OPGEEv4/branch/master/graph/badge.svg?token=NVziMt7tdD)](https://codecov.io/gh/Stanford-EAO/OPGEEv4)
[![Coverage Status](https://coveralls.io/repos/github/Stanford-EAO/OPGEEv4/badge.svg?branch=master&t=xSjoF0)](https://coveralls.io/github/Stanford-EAO/OPGEEv4?branch=master)

# OPGEE v4

OPGEEv4 is implemented as the `opgee` Python package, which provides classes, functions, 
scripts, and data that implement the OPGEE model.

## Core functionality

OPGEEv4 is a tool for translating a physical description of a set of oil and gas fields and their 
constituent conversion and transport processes into a runnable LCA model. OPGEE reads a model 
description file, written in XML format, which drives the instantiation of classes representing 
each LCA component, connecting these as required to implement the corresponding model.

OPGEEv4 is a Python implementation of the Excel-based OPGEEv3. Version 4, however, is implemented
as a more general platform supporting the creation of connected processes and streams that define
an ordered system of processing steps and flows among processes. The functionality of the processes
is defined by subclasses of a generic `Process` class, instances of which are created as defined
in the input XML file.

The main features of OPGEEv4 are:

* Ability to define oil and gas fields and all their attendant processes and streams

* Ordered execution of processes, allowing for cyclic processes

* Tracking of energy use, including imports and exports to/from the field

* Tracking of greenhouse gas emissions

* Calculation of carbon intensity (CI) for oil or gas

* Browser-based graphical user interface (GUI) to view the process and stream network, run the model, modify parameters, and view results

* Graphical display of energy use and emissions by process or aggregation of processes

* Ability to customize many aspects of the system to add new flows to streams, new processes and aggregates, and more.

* Support for Monte Carlo simulation

## How do I get set up?

* Documentation is available at http://opgee.readthedocs.io/.

## Who do I talk to?

* TBD

# Release Notes

## Version 4.0.0-alpha.0 (2022-03-01)

First alpha version made public. Still testing against Excel version and adding essential features.
