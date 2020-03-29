
Installing from source
-----------------------

This code is developed on `GitHub <https://github.com/arjunsavel/covid-hacks-2020>`_. If you received the code as a tarball or zip, skip to below the :code:`git clone` line. I would recommending performing the below steps in a fresh conda environment.

.. code-block:: bash

    python3 -m pip install -U pip
    python3 -m pip install -U setuptools setuptools_scm pep517
    git clone https://github.com/arjunsavel/covid-hacks-2020.git
    cd covid-hacks-2020
    pip install -r requirements.txt