---
title: "FastScore Configuration Syntax"
---

# FastScore Configuration Syntax

The Connect service maintains the deployment-wide configuration. The
configuration describes all service instances, the Pneumo properties, etc.

The standard representation of FastScore configuration uses YAML format. The
semi-formal template for the configuration is given below:

```
fastscore:
  fleet:
    - api: model-manage
      host: ...
      port: ...
    - api: engine
    ...
  pneumo:
    type: REST (or kafka)
    ...
  db:
    type: mysql
    host: ...
    port: 3306
    username: ...
    password: ...
```

Use the following CLI command to set the FastScore configuration:

```
$ fastscore config set config.yaml
```

Note that the configuration can be set multiple time. The services are able to
detect the change in the version of the configuration and act accordingly, e.g.
use a different Kafka instance for Pneumo messages.

