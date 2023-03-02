===========
 Changelog
===========
All notable changes will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[0.1.0-alpha] - 2023-03-01
==========================
Initial release of libzet.

I made this library because 2 of my other applications were doing basically
identical things with zettels so I abstracted out those classes and logic here.

Still needs docs and more robust unit testing, but the interface is solid
because I imported the main functions from a program I've been daily driving
for 2 years (pun intended).

Added
-----
- The main Zettel class. It can load a zettel from markdown or RST documents.
  Each must have a title, and then headings below that followed by a section
  for attributes.
- A function for filtering lists of zettels based on metaprogramming filter
  strings that adhere to python3 syntax.
- It should also be safe to compare against asymmetrical zettels; that is to
  say zettels with mismatched attributes. Attributes not present in particular
  zettels will be ignored (still need to figure out competing types though).
- Attributes class to help with loading and string dumping the attributes back
  to the files. It also automatically parses datetimes out of any field with
  a "date" in it.
