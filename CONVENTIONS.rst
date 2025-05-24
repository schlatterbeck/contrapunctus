Contrapunctus Coding Conventions
================================

This document outlines the coding conventions used in the Contrapunctus
project.

All documents (including documentation like this one) use a maximum line
length of 80 characters.

Python Style
------------

Indentation and Spacing
~~~~~~~~~~~~~~~~~~~~~~~

- 4 spaces for indentation
- No tabs
- Never produce trailing spaces on a line (unless we have a very special
  case like a doctest where the command produces trailing spaces)
- Spaces around operators
- A space between function name and opening parenthesis
- Space after commas in argument lists
- We generally have a space before a parenthesis or bracket, except for
  a *second* bracket (in multi-dimensional dereferences) e.g.::

    my_function ()
    my_list [0][5]


Comments
~~~~~~~~

- Comments use ``#`` followed by a space
- Inline comments have at least one space before the ``#``
- Block comments describe complex logic or design decisions but
  typically those should use docstrings

Class and Method Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Class names use uppercases with underscores (e.g., ``Contrapunctus``,
  ``Check_Melody_Interval``).
- Method names use snake_case with underscores (e.g., ``compute_interval``,
  ``as_tune``).
- Class methods are separated by a comment line: ``# end def method_name``
- Classes are terminated with a comment line: ``# end class ClassName``.
  When closing a class this way we typically leave an empty line before
  the closing comment.
- After the method or class name we always have a space before the
  opening parenthesis, same when calling a function.
- Contrary to the standard python PEP style defaults in arguments lists
  uses spaces before and after the ``=``, same when calling functions.
- Argument lists in function or method definitions that become too long
  are first tried to shorten by only moving the argument list (including
  parenthesis) to the next line, we need a backslash on the previous
  line. If the argument list is still too long we try to find a
  meaningful layout, typically the arguments without defaults come first
  (when they fit on a single line, otherwise one line per argument), the
  the arguments with defaults follow, one per line.
- Multi-line lists or argument lists or similar structures have the
  comma in front and end in a closing parenthesis (or other bracketing
  construct as applicable).
- In Multi-line structures we try to keep assignments aligned.

Example::

    class Check_Melody_Interval (Check_Melody):
        def __init__ \
            ( self, desc, interval
            , badness  = 0
            , ugliness = 0
            , signed   = False
            , octave   = True
            ):
            super ().__init__ (desc, badness, ugliness)
            self.interval = set (interval)
            self.signed   = signed
            self.octave   = octave
        # end def __init__

        def _check (self, current):
            # Method implementation
            return result
        # end def _check

    # end class Check_Melody_Interval

Docstrings
~~~~~~~~~~

- Triple double-quotes for docstrings
- Docstrings include examples where appropriate
- Examples use the doctest format
- Doctests are tested in the regression test
- The first line of a docstring starts immediately after the triple
  quote. Continuation lines are indented by 4 spaces.

Example::

    def method(self):
        """ This is a docstring with an example.
            This is the second line of the example. It is indented by
            four spaces.
        
        >>> obj.method()
        Expected output
        """
        # Method implementation

Variable Naming
~~~~~~~~~~~~~~~

- Variable names use snake_case
- Boolean variables often use ``is_`` prefix
- Private methods and variables use a single leading underscore
- Constants are in ALL_CAPS

Data Structures
~~~~~~~~~~~~~~~

- Lists and dictionaries are defined with trailing backslashes for
  multi-line definitions, this format is used if a definition becomes
  too long to fit on a line, see above for function definitions with long
  signatures
- Dictionary keys and values are aligned for readability

Example::

    my_dict = dict \
        ( key1 = value1
        , key2 = value2
        , key3 = value3
        )

Error Handling
~~~~~~~~~~~~~~

- Assertions are used to validate internal logic
- Specific exceptions are raised with descriptive messages

Module Structure
~~~~~~~~~~~~~~~~

- License header at the top of each source-code file
- Year in the license header should be updated with each edit (if the
  year changed, that is) but we keep the creation date. So we have, e.g.::

  # Copyright (C) 2024-25

- Imports grouped by standard library, third-party, and local modules
- ``__all__`` list at the end of modules to specify public API

Testing
-------

- Tests use doctest format in docstrings where appropriate
- Assertions validate expected behavior
- There are tests under the ``test`` directory, they use the pytest
  framework
- There is a ``Test_Doctest`` class in ``test/test_contrapunctus.py``
  which explicitly tests all the doc tests, the ``num_tests`` dictionary
  in that file needs occasional updates when the number of doctests
  changes.

Version Control
---------------

- Commit messages start with a capitalized (50 chars or less) summary
  line, avoid ending the summary line with a period
- Then a longer description may follow after a blank line
- No line should be longer than 72 characters
- Commit messages do not use a type like "feat" or "docs" as mandated in
  other git conventions
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")

Example::

 Fix a peculiar bug involving something weird

This document is a living reference and may be updated as the project evolves.
