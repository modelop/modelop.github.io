---
title: FastScore SDK for Python
---

Release 1.6.1

An example of an interaction with FastScore:

    >>> import fastscore
    >>> connect = fastscore.Connect("https://localhost:8000")
    >>> model = fastscore.Model('model-1')
    >>> model.source = '...'
    >>> mm = connect.lookup('model-manage')
    >>> model.update(mm)
    >>> mm.models.names()
    ['model-1']
    >>> del mm.models['model-1']

The User Guide
==============

-   [Introduction](user/intro.md)
-   [Installation](user/install.md)
-   [Advanced Usage](user/advanced.md)

The API documentation / Guide
=============================

-   [Developer interface](api.md)
    -   [Service instances](api.md#module-fastscore.suite)
    -   [Exceptions](api.md#exceptions)
    -   [Pneumo](api.md#pneumo)
    -   [Models](api.md#models)
    -   [Attachments](api.md#attachments)
    -   [Snapshots](api.md#snapshots)
    -   [Streams](api.md#streams)
    -   [Schemata](api.md#schemata)
    -   [Sensors](api.md#sensors)

The Developer Guide
===================

-   [Unfinished/incomplete](dev/todo.rst)
