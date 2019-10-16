---
title: "ModelOp Center Engine"
---
# ModelOp Center Engine

The ModelOp Center Engine lives inside a Docker container and contains the various runners for the various languages and model types that ModelOp Center supports.

As of 1.9, there are now two official flavors of the Engine: one based on Alpine linux, and the other based on Ubuntu.

### Alpine

Alpine is the default Engine base (when looking at Docker tags, if no base is mentioned, assume Alpine is the base).  The Alpine engine contains the full complement of all the available runners - i.e. all languages and model types are supported on the Alpine Engine.

### Unbuntu

The Ubuntu engine exists because certain 3rd party libraries are difficult to install on Alpine.  An Engine based on Ubuntu can, therefore, be easier to work with.

The Ubuntu engine only supports runners for the following languages:
* R
* Python 3
