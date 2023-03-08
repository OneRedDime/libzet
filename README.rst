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

Testing
=======
Use the following command to run unit tests.

::

    python3 -m unittest

Maintenance and versioning
==========================
Update the CHANGELOG and version in pyproject.toml when cutting a release.

Build with ``python3 -m build`` and use ``twine upload -r pypi dist/*`` to
upload to pypi.

Usage
=====
The libzet library provides functions to parse content and metadata from
zettel notes. These notes may be in rst or markdown format.

Each note must have a title, followed by the content, and then the metadata
in yaml format.

It is still in alpha. Many libraries store their metadata at the top of a note
but I wanted mine at the bottom. I would like to be compatible with each.

Zettel File Format
------------------
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

Zettel Class
------------
Files formatted as above are loaded into Zettel objects.

- `zettel.title`: Title of the zettel.
- `zettel.headings`: Dictionary of level-2 headings within the zettel.
- `zettel.attrs`: Attributes of the Zettel.

The `attrs` is a special dictionary that will automatically parse date fields
read in by the Attributes. Any key with the word 'date' in it will be parsed.
Dates read in this matter may be very free-form. Plain English phrases such as
"tomorrow" or "next Wednesday" should work fine.

You shouldn't have to worry too much about the methods within the Zettel class;
Zettels are primarily manipulated by the functions detailed in the next section.

General flow - life of a zettel
-------------------------------
So how does one go about loading and modifying zettels from the disk? The
general flow an application should perform is...

- `create_zettel` to create a new zettel on disk.
- `load_zettels` to load a list of zettels from the disk.
- Filter this list based on the needs of your application.
- Send this list to `edit_zettels` to edit them in a text editor.
- Use `save_zettels` to save the edited zettels back to disk.

And you can use the `zettels_to_str` function to print zettels to stdout,
or the `str_to_zettels` to turn a string into a list of zettels. These
functions play well together.

Here are the specific docstrings for those methods.

::
    
    def create_zettel(
            path,
            text='', title='', headings=None, attrs=None, zettel_format='md',
            no_edit=False, errlog='', fun=lambda z: None):
        """ Create and edit a new zettel.

        All params other than path are optional.

        Args:
            path: Path to create new zettel.
            text: Provide a body of text from which to parse the whole zettel.
            headings: Headings to create the new zettel with.
            attrs: Default attributes to create the zettel.
            zettel_format: 'md' or 'rst'
            errlog: See edit_zettels
            no_edit: Set to True to skip editing.
            fun: Function which accepts a zettel reference. This function may
                be used to modify the zettel before editing.
        
        Returns:
            A list containing the newly created zettel. Pass it to save_zettels
            to write to disk.
        """


    def load_zettels(paths, zettel_format, recurse=False, fun=lambda z: None):
        """ Load Zettels from the filesystem.
    
        Zettels will be updated with a _loadpath value in their attrs.
        This value is useful while zettels are being manipulated in a
        program because it is guaranteed to be unique (at least within
        that program).
    
        If this list is sent to save_zettels then the _loadpath will
        not be written.
    
        Args:
            paths: List of directories and exact paths to zettels.
            zettel_format: md or rst
            recurse: True to recurse into subdirs, False otherwise.
            fun: Call this function on each zettel as it's loaded from disk.
                Raise SkipZettel from fun to avoid loading a zettel.
    
        Returns:
            A list of zettels.
    
            This list may be passed to save_zettels to write
            them to the filesystem.
        """


    def edit_zettels(zettels, zettel_format, headings=None, errlog=''):
        """ Bulk edit existing zettels.
    
        Assumes the zettels were loaded with Zettel.load_zettels . This
        function cannot create new zettels.
    
        If the editing resulted in incorrect zettels and errlog is specified,
        then this function will write the text to errorlog and print the error.
        Modify this file and pass it back to this function to retry parsing.
    
        Delete the text while editing to avoid updating a zettel.
    
        Args:
            zettels: List of zettels to edit.
            zettel_format: md or rst.
            headings: Only edit specific headings.
            errlog: Write zettels to this location if parsing failed.
    
        Returns:
            A tuple of dictionaries. In each, the key is the _loadpath
            and the value is the zettel reference.
    
                all_, updated
    
            all_ references all zettels.
            updated maps just the zettels which were updated.
    
            The caller may optionally compare these dicts. For example,
            perhaps to delete zettels from disk which were deleted in edit.
    
        Raises:
            ValueError if any zettels were edited in an invalid way.
        """


    def save_zettels(zettels, zettel_format, fun=lambda z: None):
        """ Save zettels back to disk.
    
        The zettels are expected to have a _loadpath key in their attrs.
        Probably best to send the output from load_zettels to this function.
    
        Args:
            zettels: List of zettels.
            zettel_format: md or rst.
            fun: A callable that accepts a zettel reference. This will be called
                on each zettel before it's written back to disk.

                Raise SkipZettel to skip saving a zettel.
        """


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
            headings: Provide a list of select headings to write.

        Returns:
            A str representing the zettels
        """
