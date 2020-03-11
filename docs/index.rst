Welcome to Lina
===============

Lina is a minimal template system for Python, modelled after Google's `CTemplate <https://code.google.com/p/ctemplate>`_ library. It is designed to provide fast, safe template evaluation to generate code or other text documents. ::

    enum DataTypes {
    {{#types:list-separator=,NEWLINE}}  {{name}}={{value:hex}}{{/types}}
    }

evaluated with::

    types = [{'name':'Vector3i', 'value': 0x301}, {'name':'Vector3f', 'value': 0x302}]

will produce::

    enum DataTypes {
        Vector3i = 0x301,
        Vector3f = 0x302
    }

Overview
--------

The base class in Lina is :py:class:`lina.Template` which must be initialized with the template contents. It can be then evaluated to a string using :py:meth:`lina.Template.Render` and :py:meth:`lina.Template.RenderSimple`.

Lina has two main directives, *values* and *blocks*. A value is something which is replaced directly by the provided value, while a block is used to iterate over collections. Both blocks and values can be optionally formatted using a ``formatter``, which allows for example to turn a string into uppercase inside the template.

Values are escaped using double curly braces::

    Hello {{name}}!

Blocks have an additional prefix before the variable, ``#`` for the block start and ``/`` for the block end::

    {{#users}}Hello {{name}}!{{/users}}

This requires to pass an array of named objects::

    template.Render ({'users':[{'name':'Alice'}, {'name':'Bob'}]})

Element access
--------------

In some cases, accessing members by names is unnecessary complicated. Lina provides a special syntax to access the *current* element, using a single dot. Using a self-reference, the template above can be simplified to::

    {{#users}}Hello {{.}}!{{/users}}

and rendered with::

    template.Render ({'users': ['Alice', 'Bob']})

or even simpler using :py:meth:`lina.Template.RenderSimple`::

    template.RenderSimple (users = ['Alice', 'Bob'])

Both self-references as well as values can also access fields of an object. Assuming the ``User`` class has fields ``name``, ``age``, the following template will print the user name and age::

    {{#users}}Hello {{.name}}, you are {{.age}} years old!{{/users}}

For an object, use ``{{item.field}}``. The field accessor syntax works for both fields as well as associative containers, that is, for Lina, the following two objects are equivalent::

    u = {'name':'Alice'}

and::

    class User:
        def __init__(self, name):
            self.name = name

    u = User ('Alice')

It is also possible to directly reference indexed items using ``[0]``, ``[1]``, etc. For instance, the following template::

    {{#vectors}}X: {{.[0]}}, Y: {{.[1]}}, Z: {{.[2]}}\n{{/vectors}}

rendered with::

    template.RenderSimple (vectors = [[0, 1, 2], [3, 4, 5]])

will produce::

    X: 0, Y: 1, Z: 2
    X: 3, Y: 4, Z: 5

Blocks
------

For blocks, Lina provides additional modifiers to check whether the current block execution is the first, an intermediate or the last one::

    {{#block}}{{variable}}{{#block#Separator}},{{/block#Separator}}{{/block}}

``#First`` will be only expanded for the first iteration, ``#Separator`` will be expanded for every expansion which is neither first nor last and ``#Last`` will be expanded for the last iteration only. If there is only one element, it will considered both first and last item of the sequence.

If a block variable is not found, or the block is ``None``, the block will be not expanded. It is possible to capture this case using ``!`` blocks, which are only expanded if the variable is not present::

    {{!users}}No users :({{/users}}

Rendered with ``template.Render ()``, this will yield ``No users :(``. This can be used to emulate conditional statements.

Formatters
----------

Lina comes with a few formatters which can be used to modify values or block elements. The value formatters are:

* ``width``, ``w``: This aligns a value to a specific width. Negative values align to the left. For example: ``{{name:w=-8}}`` using ``name='Ton'`` will yield ``     Ton``.
* ``prefix`` adds a prefix to a value. For example: ``{{method:prefix=api_}}`` with ``method='Copy'`` yields ``api_Copy``
* ``suffix`` adds a suffix to a value. For example: ``{{method:suffix=_internal}}`` with ``method='Copy'`` yields ``Copy_internal``
* ``default`` provides a default value in case the provided value is ``None``. ``{{name:default=Unknown}}`` with ``name=None`` yields ``Unknown``.
* ``upper-case``, ``uc`` converts the provided value to upper case. ``{{func:upper-case}}`` with ``func=Copy`` yields ``COPY``.
* ``escape-newlines`` escapes embedded newlines. ``{{s:escape-newlines}}`` with ``s='foo\nbar'`` yields ``foo\\nbar``.
* ``escape-string`` escapes newlines, tabs, and quotes. ``{{s:escape-string}}`` with ``s=a "string"`` yields ``a \"string\"``.
* ``wrap-string`` wraps the provided string with quotes. ``{{s:wrap-string}}`` with ``s=string`` yields ``"string"``. If the value is not a string, it will not be wrapped.
* ``cbool`` converts booleans to ``true`` or ``false``. ``{{enabled:cbool}}`` with ``enabled=True`` yields ``true``. If the value is not a boolean, it will be returned as-is.
* ``hex`` prints numbers in hexadecimal notation. ``{{i:hex}}`` with ``i=127`` yields ``0x7F``.

Lina provides the following block formatters:

* ``indent`` indents every line with a specified number of tabs. ``{{#block:indent=2}}{{.}}{{/block}}`` with ``block=[1,2]`` yields ``\t\t1\t\t2``
* ``list-separator``, ``l-s`` separates block repetitions using the provided value. ``{{#block:l-s=,}}{{.}}{{/block}}`` with ``block=[1,2]`` yields ``1,2``. ``NEWLINE`` is replaced with a new line, and ``SPACE`` with a space.

Whitespace & special characters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Whitespace in Lina is preserved. If you want to explicitly insert whitespace, you can use ``{{_NEWLINE}}`` to get a new line character inserted into the stream, and ``{{_SPACE}}`` to get a blank space. To produce a left brace or right brace, use ``{{_LEFT_BRACE}}`` and ``{{_RIGHT_BRACE}}``.

Contents
========

.. toctree::
   :maxdepth: 4

   lina
   release-notes


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
