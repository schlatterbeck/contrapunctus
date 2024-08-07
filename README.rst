Contrapunctus
=============

This project is an experiment to generate music via AI techniques.
We start with Contrapunct because it has many rules and promises to get
us some results quickly.

The following are notes (mostly in german)

Also interesting are the wikipedia articles on Counterpoint:
https://en.wikipedia.org/wiki/Counterpoint
The german version is not as good for our purposes because it doesn't
contain all the rules:
https://de.wikipedia.org/wiki/Kontrapunkt

Some more articles on musical theory:
https://de.wikipedia.org/wiki/Kirchentonart
https://de.wikipedia.org/wiki/Quintenzirkel

Testing
-------

For testing we're using pytest. You can run the tests with::

    python3 -m pytest test

Coverage
++++++++

The test coverage can be computed with::

    python3 -m pytest -cov contrapunctus test

or more verbose (including a report about untested lines) with::

    python3 -m pytest --cov-report term-missing --cov contrapunctus test

By default this skips long-running tests. You can enable these tests
with the --longrun option::

    python3 -m pytest --cov-report term-missing --cov \
        contrapunctus test --longrun

When running things with MPI it is a good idea to run the ``coverage``
program explicitly (it may be named differently on your installation, on
Debian Linux it is called ``python3-coverage``) and tell it via
``setup.cfg`` to produce separate coverage reports for each CPU::

    mpirun --machinefile ~/.mpi-openmpi-bee+cat --np 8 \
        coverage run --rcfile setup.cfg -m pytest --longrun
    coverage combine --keep
    coverage report -m --include "contrapunctus/*"

Regeln für Cantus Firmus
------------------------

- Sanglich eher stufenweise nicht zu viele Sprünge
  Intervalle: 3, 4, 5, 8 (6)
  Terz, Quart erlaubt, Quint, Octave selten, Sext sehr selten
  Quart gilt als Dissonanz, im Cantus Firmus erlaubt, bei zweiter Stimme
  nicht
- Aufbau Spannung, Höhepunkt, Entspannung
  Fängt an und endet mit Grundton
- Keine Anklänge an Dur und Moll:
  Einfacher: Keine zwei Sprünge hintereinander
- Nach Sprung Schritt in Gegenrichtung

- Anfang und Ende immer Grundton
- Vorletzter Ton zweite Stufe (einen Ton über Grundton)

Grundton: Finalis
Leitton: 7. Stufe einen Halbton unter Grundton
