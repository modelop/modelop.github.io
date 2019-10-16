---
title: "ModelOp Center Configuration Syntax"
---

# ModelOp Center Configuration Syntax

The Connect service maintains the deployment-wide configuration. The
configuration describes all service instances, the Pneumo properties, etc.

The standard representation of ModelOp Center configuration uses YAML format. The
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

Use the following CLI command to set the ModelOp Center configuration:

```
$ ModelOp Center config set config.yaml
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

It is possible to configure credentials in ModelOp Center via Docker Secrets.  To do so you must:
* [Grant access](https://docs.docker.com/compose/compose-file/#secrets) to the secret to the relevant microservice.
* Reference the secret with "secret://..." syntax inside the YAML config file.

### Three options for secret:// syntax

#### Relative path

```
secret://secret1
```

ModelOp Center will look for `secret1` in the default /run/secrets directory

#### Relative path OVERRIDE

set the env variable `SECRET_PATH_ROOT` to /some/other/directory

```
secret://secret2
```

ModelOp Center will expect to find /some/other/directory/secret2

#### Absolute path

```
secret:///absolute/path/to/secret3
```

ModelOp Center will look in /absolute/path/to for `secret3`

Note the three '/', instead of the usual two.

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

# Configuration Persistence

Upon startup, the Connect service checks for a `FASTSCORE_CONFIG` environment variable.  If present, it uses the contents of this variable to set ModelOp Center's initial configuration.

FASTSCORE_CONFIG can be set right in a docker-compose file:
```
...
  connect: 
    image: local/connect
    ports: 
        - "8001:8001"
    stdin_open: true
    environment: 
       FASTSCORE_CONFIG: |
        fastscore: 
          fleet: 
            - api: model-manage
              host: model-manage
              port: 8002
            - api: engine
              host: engine-1
              port: 8003
            - api: engine
              host: engine-2
              port: 8003

          db: 
            type: mysql
            host: database
            port: 3306
            username: root
            password: root

          pneumo: 
            type: kafka
            bootstrap: 
              - kafka:9092
            topic: notify
    tty: true
    networks: 
      - fsnet
...
```
