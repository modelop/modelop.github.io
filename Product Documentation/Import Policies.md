---
title: "Import Policies"
excerpt: "New in v1.4!"
---
Python and R models often make use of libraries, sometimes importing third-party libraries. For example, a Python model may contain the statement 
```
import scikit-learn
```
When deploying models in production, it can be valuable to control which libraries are installed and usable by a model. FastScore's Engine provides this functionality through **import policies**.

An import policy manifest describes what the engine should do when a model references certain libraries. The manifest is a YAML-encoded file with library names for keys. For example, the entry `socket: prohibit` instructs the engine not to load the model that references the `socket` library. 

The possible entries are:

[block:parameters]
{
  "data": {
    "h-0": "Entry",
    "h-1": "Description",
    "0-0": "```\n<my-lib>: prohibit\n```",
    "0-1": "Do not load the model and issue an error.",
    "1-0": "```\n<my-lib>: warn\n```",
    "1-1": "Allow the model to run, but issue a warning.",
    "2-0": "```\n<my-lib>: install\n```",
    "2-1": "Install the library using the default command.",
    "3-0": "```\n<my-lib>:\n    policy: install\n    command: <command>\n```",
    "3-1": "Install the library using a custom command."
  },
  "cols": 2,
  "rows": 4
}
[/block]
The engine knows the standard install commands for all runners. For example, for Python, the engine would use `pip install <my-lib>`. 

An example import policy manifest would for a Python runner is:
[block:code]
{
  "codes": [
    {
      "code": "os: prohibit\nsocket: warn\nscikit-learn:\n  policy: install\n  command: pip install scikit-learn=3.2.1\nnose: install",
      "language": "yaml"
    }
  ]
}
[/block]
A model runner's import policy manifest is loaded from the `import.policy` file located in the appropriate directory in the engine's filesystem:

* For Python2: `/root/engine/lib/engine-1.4/priv/runners/python`
* For Python3: `/root/engine/lib/engine-1.4/priv/runners/python3`
* For R: `/root/engine/lib/engine-1.4/priv/runners/R`

In FastScore 1.4, the import policy for a model runner is fixed as soon as a model is loaded into the engine, so any changes to import policies must be made _before_ running a model. To copy a new manifest into the container, use the [`docker cp`](https://docs.docker.com/engine/reference/commandline/cp/) command or an equivalent.

Adding import policies to an engine through the command `fastscore policy set my-policy.yml` is now available with v1.6. See [FastScore Command Line Interface](doc:fastscore-command-line-interface) for more information on subcommands.