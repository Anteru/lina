Miranda
=======

Miranda is a template engine in the spirit of Google's [CTemplate](http://code.google.com/p/ctemplate/?redir=1) written in Python 3. It can be used to generate any kind of text-based documents. Right now, it is mostly used for HTML and C/C++ code generation.

Requirements
------------

Python 3 is all that is needed. Tested with Python 3.1, 3.2 and 3.3. Python 3.0 is not recommended.

Getting started
---------------

The most trivial template is:

    Hello {{name}}!

It can be evaluated using

    import Miranda.Template
    template = Miranda.Template.Template ('Hello {{name}}!')
    print (template.RenderSimple (name = "Bob"))

This will print:

    Hello Bob!

The real power comes from blocks which can be repeated and nested. For instance:

    {{#Users}}Hello {{name}}!{{/Users}

rendered with

    Users = [{'name':'Alice'}, {'name':'Bob'}]

will print:

    Hello Alice!Hello Bob!

This can be further improved by using formatters. A formatter modifies a value just before it is written to the output stream. Miranda comes with a set of predefined formatters like upper-case transformation. Formatters can be defined for values or blocks. A good example for a block-level formatter is the `list-separator` formatter. If we change the template of the previous example to:

    {{#Users:list-separator=NEWLINE}}Hello {{name}}!{{/Users}

the result will be:

    Hello Alice!
    Hello Bob!

Value-level formatters are for example the upper-case formatter. `{{value:upper-case}}` with `value` set to `Test` will result in `TEST`.