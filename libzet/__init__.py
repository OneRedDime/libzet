import sys

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

__version__ = metadata.version('libzet')

from libzet.Zettel import (
    load_zettels, save_zettels, SkipZettel, str_to_zettels, Zettel, zettels_to_str)

from libzet.edit import create_zettel, edit_zettels
