---
title: "FastScore Configuration Syntax"
---

# FastScore Configuration Syntax

The Connect service maintains the deployment-wide configuration. The
configuration describes all service instances, the Pneumo properties, etc.

The standard representation of FastScore configuration uses YAML format. The
semi-formal template for the configuration is given below:

```yaml
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

# Specifying custom instance names

Fleet elements all have a name, which, by default, is the host name specified.  However, custom names can be given:

```yaml
fastscore:
  fleet:
    - api: model-manage
      name: Mr. Manager
      host: model-manage
      port: 8002
    - api: engine
      host: engine-1
      port: 8003
    - api: engine
      name: an explicitly named engine
      host: engine-2
      port: 8003
```

```
$ fastscore fleet
Name                        API           Health
--------------------------  ------------  --------
engine-1                    engine        ok
an explicitly named engine  engine        ok
Mr. Manager                 model-manage  ok
```

# Using Docker Secrets to configure database username/password

It is possible to configure credentials in FastScore via Docker Secrets.  To do so you must:
* [Grant access](https://docs.docker.com/compose/compose-file/#secrets) to the secret to the relevant microservice.
* Reference the secret with "secret://..." syntax inside the YAML config file.

#### In config.yaml
Where 'foo' is the name of the Docker Secret that contains the username, and 'bar' is the name of the Docker Secret that contains the password:

MySQL secrets:
```yaml
db:
  type: mysql
  username: secret://foo
  password: secret://bar
```

Git secrets:
```yaml
db:
  type: git
  username: secret://foo
  password: secret://bar
```

#### In Stream Descriptors
Kafka stream:
```json
{
  "Transport": {
    "Type": "kafka",
    "Keytab": "secret://foo",
    "Principal": "secret://bar"
  }
}
```
Note: Authenticated Kafka streams requires that the krb5.conf be copied into the engine container at /etc/.

S3 stream:
```json
{
  "Transport": {
    "Type": "S3",
    "AccessKeyID": "secret://foo",
    "SecretAccessKey": "secret://bar"
  }
}
```
