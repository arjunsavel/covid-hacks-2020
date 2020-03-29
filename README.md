# covid-hacks-2020
[![Build Status](https://travis-ci.com/arjunsavel/covid-hacks-2020?branch=master)](https://travis-ci.com/arjunsavel/covid-hacks-2020) [![codecov](https://codecov.io/gh/arjunsavel/covid-hacks-2020/branch/master/graph/badge.svg?)](https://codecov.io/gh/arjunsavel/covid-hacks-2020)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Documentation Status](https://readthedocs.org/projects/covid-19-simulations/badge/?version=latest)](https://covid-19-simulations.readthedocs.io/en/latest/?badge=latest)


Simulating and working with COVID-19 data. Our simulation implements an arguably naive agent-based approach, storing data in pandas DataFrames.

![2D animation](https://github.com/arjunsavel/covid-hacks-2020/blob/master/img/2D.gif)

![1D simulation](img/1D.png)


The *.py files contain the scripts necessary to run the simulations in the dimension of your choosing. "Simulation_notebook.ipynb" produces the relevant plots; "Data exploration.ipynb" and "covid_country_data.ipynb" relate to the COVID-19 case data included in this repository; and "performance_testing.ipynb" includes a variety of benchmarks used in the debugging and optimization of the simulation.

Make sure you have the correct dependencies installed — run

     pip install -r requirements.txt
I would recommend doing so in a fresh conda environment.
