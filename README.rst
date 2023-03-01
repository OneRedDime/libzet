========
 libzet
========
Hello and welcome to libzet, a library for reading data from zettels.

Building and installation
=========================
Available from PyPi; Just ``pip3 install superdate``

Alternatively, clone this repo and then pip3 install.

::

    pip3 install --user .

Usage
=====
The libzet library provides functions to parse content and metadata from
zettel notes. These notes may be in rst or markdown format.

Each note must have a title, followed by the content, and then the metadata
in yaml format.

It is still in alpha. Many libraries store their metadata at the top of a note
but I wanted mine at the bottom. I would like to be compatible with each.

Zettel Format
-------------
Zettels may be stored in markdown or RST format. Here's an example in markdown.

::

    # Markdown Zettel Title

    Some content

    ## Heading 1
    Notes under Heading 1

    <!--- attributes --->
        ---
        key1: value1
        key2: value2

And an example in RST.

::
    
    ==================
     RST Zettel Title
    ==================
    Some content

    Heading 1
    =========
    Notes under Heading 1

    .. attributes
    ::

        ---
        key1: value1
        key2: value2

Loading Zettels
---------------
The 2 main methods to create zettels are.

- str_to_zettels
- zettels_to_str

::

    def str_to_zettels(text, zettel_format):
        """ Convert a str to a list of zettels.
    
        The return from this function can be passed to zettels_to_str.
    
        Args:
            text: Text to convert to zettels.
            zettel_format: 'rst' or 'md'.
    
        Returns:
            A list of Zettel references.
        """

    def zettels_to_str(zettels, zettel_format, headings=None):
        """ Return many zettels as a str.

        The output from this function can be passed to str_to_zettels.

        Args:
            zettels: List of zettels to print.
            zettel_format: 'rst' or 'md'.

        Returns:
            A str representing the zettels
        """

Testing
=======
Use the following command to run unit tests.

::

    python3 -m unittest

Maintenance and versioning
==========================
Update the CHANGELOG when and version in pyproject.toml when cutting a release.

Build with ``python3 -m build`` and use ``twine upload -r pypi dist/*`` to
upload to pypi.
