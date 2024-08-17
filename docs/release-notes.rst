Release notes
=============

1.0.11
------

* Packaging changes only.

1.0.10
------

* Added ``{{_LEFT_BRACE}}`` and ``{{_RIGHT_BRACE}}`` tokens.

1.0.9
-----

* Applying block formatters to non-blocks and value formatters to non-values
  raises an error now. Previously, those were silently ignored.

1.0.8
-----

* Packaging changes only.

1.0.7
-----

* The formatter registration has been improved. Instead of a long ``if-elif``
  cascade, it now jumps directly to the right formatter through a dictionary.

1.0.6
-----

* Various build improvements.

1.0.5
-----

* Handling of ``None`` blocks changed (i.e. set using ``block_name = None``.) Instead of treating them as empty, they are now completely ignored. Only blocks initialized to an empty container (``{}``) are now treated as empty.

1.0.4
-----

* Added a new ``escape-string`` formatter.

1.0.3
-----

* Add support for negated blocks: ``{{!block}}``

1.0.2
-----

* Add support for self references via ``{{.[0]}}``.

1.0.1
-----

* Allow block formatters to write a suffix
* Add support for field access via ``{{item.member}}``.

1.0
---

Initial public release.