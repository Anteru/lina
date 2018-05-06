Release notes
=============

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