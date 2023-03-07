""" Functions to assist editing zettels in an editor.
"""
import os
import tempfile
from subprocess import call

from superdate import parse_date

from libzet.Zettel import Zettel, str_to_zettels, zettels_to_str


def edit(s='', output_file='', editor='', file_extension='.md'):
    """ Open a string in a text editor.

    If output_file is supplied, then the string will be copied to that file.

    Args:
        s: The string to edit.
        output_file: Optional file to write to.
        editor: Specify path to editor. If not supplied the the EDITOR and VISUAL
            environment variables are searched.
        file_extension: File extension. eg. .txt, .md, .rst...

    Returns:
        The text from the edited file.

    Raises:
        ValueError if the editor wasn't set and neither were the VISUAL or
        EDITOR environment variables.

        PermissionError if the file could not be edited.
    """
    if not editor:
        if 'EDITOR' in os.environ:
            editor = os.environ['EDITOR']
        elif 'VISUAL' in os.environ:
            editor = os.environ['VISUAL']

    if not editor:
        raise ValueError('Neither the "VISUAL" or "EDITOR" environment variables had values.')

    _, path = tempfile.mkstemp(suffix=file_extension)

    try:
        with open(path, 'w') as f:
            f.write(s)

        call([editor, path])

        with open(path, 'r') as f:
            text = f.read()

    finally:
        os.remove(path)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(text)

    return text


def update_zettels(orig_zettels, new_zettels, exp_headings=None):
    """ Update a bunch of zettels at once.

    Called by edit_zettels. Accepts two dictionaries of zettels;
    old and new. The old zettels with the same keys as new zettels
    will be updated.

    Don't use this method to create new zettels unless you set the
    _loadpath parameter yourself. The point of a zettel is to be
    written back to disk and this parameter is necessary for that.

    Args:
        orig_zettels: Dict of original zettels to update.
        new_zettels: Dict of zettels with new content.

        exp_headings: A list of expected headings. If a heading
            is here but not in the new_zettel then the heading
            will be deleted from the original zettel.

            If this argument is not specified the it's just like
            modifying the whole zettel.
    """
    for k, z in new_zettels.items():
        if k in orig_zettels:
            orig_zettels[k].update(z, exp_headings)


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
    if type(zettels) is str:
        zettels = str_to_zettels(zettels, zettel_format)

    s = zettels_to_str(zettels, zettel_format, headings)
    s = edit(s)

    try:
        updated = str_to_zettels(s, zettel_format)
    except ValueError as e:
        if errlog:
            with open(errlog, 'w') as f:
                f.write(s)
        raise

    all_ = {z.attrs['_loadpath']: z for z in zettels}
    updated = {z.attrs['_loadpath']: z for z in updated}
    update_zettels(all_, updated, headings)

    return all_, {k: all_[k] for k in updated}


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
    z = None
    if text:
        z = str_to_zettels(text, zettel_format)[0]
    else:
        z = Zettel(title, headings, attrs)

    z.attrs['creation_date'] = parse_date('today')
    z.attrs['_loadpath'] = path
    fun(z)
    z.attrs['_loadpath'] = path

    if not no_edit:
        edit_zettels([z], zettel_format, headings, errlog)

    return [z]
