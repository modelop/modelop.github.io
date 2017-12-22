---
title: "Import Policies"
excerpt: "New in v1.4!"
---
# Import Policies

Python and R models often make use of libraries, sometimes importing third-party libraries. For example, a Python model may contain the statement 
```
import scikit-learn
```

When deploying models in production, it can be valuable to control which libraries are installed and usable by a model. FastScore's Engine provides this functionality through **import policies**.

An import policy manifest describes what the engine should do when a model references certain libraries. The manifest is a YAML-encoded file with library names for keys. For example, the entry `socket: prohibit` instructs the engine not to load the model that references the `socket` library. 

The possible entries are:

| Entry | Description |
| --- | --- |
| <my-lib>: prohibit | Do not load the model and issue an error. |
| <my-lib>: warn | Allow the model to run, but issue a warning. |
| <my-lib>: install | Install the library using the default command. |
| <my-lib>:<br>    policy: install<br>    command: <command> | Install the library using a custom command. |


The engine knows the standard install commands for all runners. For example, for Python, the engine would use `pip install <my-lib>`. 

An example import policy manifest would for a Python runner is:

``` yaml
os: prohibit
socket: warn
scikit-learn:
  policy: install
  command: pip install scikit-learn=3.2.1
nose: install
```

A model runner's import policy manifest is loaded from the `import.policy` file located in the appropriate directory in the engine's filesystem:

* For Python2: `/root/engine/lib/engine-1.4/priv/runners/python`
* For Python3: `/root/engine/lib/engine-1.4/priv/runners/python3`
* For R: `/root/engine/lib/engine-1.4/priv/runners/R`

In FastScore 1.4, the import policy for a model runner is fixed as soon as a model is loaded into the engine, so any changes to import policies must be made _before_ running a model. To copy a new manifest into the container, use the [`docker cp`](https://docs.docker.com/engine/reference/commandline/cp/) command or an equivalent.

Adding import policies to an engine through the command `fastscore policy set my-policy.yml` is now available with v1.6. See [FastScore Command Line Interface](https://opendatagroup.github.io/Product%20Documentation/FastScore%20Command%20Line%20Interface.html) for more information on subcommands.