# A Simple Microservice

In this example, we'll build a simple microservice dashboard using
[Swagger Codegen](https://swagger.io/swagger-codegen/)
and the ModelOp Center SDK. Our microservice will perform two functions: it will
provide an at-a-glance summary of the current state of all running engines, and
it will retrieve the source code of the models running on each engine.

[Download the code for this example.](https://s3-us-west-1.amazonaws.com/ModelOp Center-examples/Microservice-Example.zip)

Let's start by defining the REST API for this microservice, using Swagger. Our
microservice will serve an index page and retrieve information about deployed
models. Here's the specification:

**Swagger Specification: api.yaml**
```yaml
swagger: "2.0"
info:
    description: "An example ModelOp Center microservice."
    version: "0.1"
    title: "My ModelOp Center Microservice"

paths:
    /:
        get:
            produces:
                - text/html
            operationId: get_index
            responses:
                200:
                    description: Returns the Dashboard homepage.
                    schema: { type: string }
    /{engine}/model:
        get:
            parameters:
                - name: engine
                  description: The name of the engine instance
                  type: string
                  in: path
                  required: true
            produces:
                - application/json
            operationId: get_model
            responses:
                200:
                    description: Returns a description of the currently running model.
                    schema: { type: object }
```

Using Swagger-Codegen, we can auto-generate a server stub that matches this API
specification. The Swagger-Codegen command line tool is a small Java application
that can be found here: [github.com/swagger-api/swagger-codegen](https://github.com/swagger-api/swagger-codegen#prerequisites)
For Mac users, Swagger-Codegen can also be installed using Homebrew with
```
brew install swagger-codegen
```

After downloading a recent stable version of Swagger-Codegen to the current working
directory containing the API specification (`api.yaml`), generate a server
stub with
```
java -jar swagger-codegen-cli.jar generate -i api.yaml -l python-flask -o myserver
```
This will generate a new directory ("`myserver`"), containing the auto-generated
server stub and some further instructions.

In the generated code, there are two Python files to pay particular attention to.
The first is `__main__.py` (in `myserver/swagger_server/`), which defines the
entrypoint for the server. Changing this script will control the behavior of the
server---for example, by setting HTTPS/SSL options or changing the default port.

**`__main__.py`**
```python
#!/usr/bin/env python3

import connexion
from .encoder import JSONEncoder


if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'An example ModelOp Center microservice.'})
    app.run(port=8080)
```

The most important generated Python code is `default_controller.py`, located in
`myserver/swagger_server/controllers/`. This script is responsible for defining
the server operations corresponding to the REST API. Each function name maps to
the `operationId` in the API specification---for example, `get_model` is the
`operationId` associated to `/{engine}/model`'s GET operation.

The generated code is below:

**`default_controller.py`**
```python
import connexion
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def get_index():
    """
    get_index


    :rtype: str
    """
    return 'do some magic!'


def get_model(engine):
    """
    get_model

    :param engine: The name of the engine instance
    :type engine: str

    :rtype: object
    """
    return 'do some magic!'
```

Defining additional operations in the API specification will add other functions
to this controller. For more complicated microservers, custom controllers
can also be defined, but for this example we'll just modify the default one.

For this example, we've modified a CSS template from [Templated](https://templated.co/)
to use as our Dashboard. (Download it from [here](https://s3-us-west-1.amazonaws.com/ModelOp Center-examples/Microservice-Example.zip)).

Add two new directories to the `swagger_server` module (`myserver/swager_server`),
one called `templates` and the other `static`. The `static` directory will hold
static assets (such as CSS stylesheets), and the `templates` directory will hold
the templates for the the webpages served by our microservice (in this case, just
a simple dashboard).

Next, let's edit the `get_index` method to point to our template file. Add
```python
from flask import render_template
```
to the top of the script, and change the return statement to:
```python
return render_template('index.html', engines = [])
```

If you try running the server (e.g. with `python3 -m swagger_server`), and
navigate to `http://localhost:8123`, you should now see an empty page listing
no engines.

Using the ModelOp Center SDK, it's easy to retrieve a list of engine objects:
```python
from ModelOp Center.suite import Connect
c = Connect(proxy_prefix="https://localhost:8000")
engines = [c.get(x.name) for x in c.fleet() if 'engine' in x.name]
```
This produces a list of `ModelOp Center.suite.Engine` objects. This example's dashboard
requires three pieces of information: the engine's name, the current model
running (if any), and the current engine state. We can retrieve this information
with the following function:
```python
def engine_map(engine):
    engine.clear() # reset any locally cached engine data
    model_name = "none"
    if engine.active_model is not None:
        model_name = engine.active_model.name
    return { 'name': engine.name, 'model': model_name, 'state': engine.state }
```

Update the `get_index()` function in `default_controller.py` to include this
new function:
```python
def get_index():
    """
    get_index

    :rtype: str
    """
    c = Connect(proxy_prefix="https://localhost:8000")
    engines = [c.get(x.name) for x in c.fleet() if 'engine' in x.name]
    engine_data = map(engine_map, engines)
    return render_template('index.html', engines = engine_data)
```

So far, we've assumed that the ModelOp Center fleet proxy is accessible at `https://localhost:8000`.
This may not always be the case, so for convenience, we can retrieve this information
from an environment variable. Add `import os` to this script's import statements.
Then, define a function to retrieve the proxy prefix with:
```python
def proxy_prefix():
    if 'PROXY_PREFIX' in os.environ:
        return os.environ['PROXY_PREFIX']
    return "https://localhost:8000"
```
Update `get_index()` to use this function:
```python
def get_index():
    """
    get_index

    :rtype: str
    """
    c = Connect(proxy_prefix=proxy_prefix())
    engines = [c.get(x.name) for x in c.fleet() if 'engine' in x.name]
    engine_data = map(engine_map, engines)
    return render_template('index.html', engines = engine_data)
```
The user may then set the proxy prefix by setting the `PROXY_PREFIX` environment
variable. If `PROXY_PREFIX` is not defined, then it falls back to `https://localhost:8000`.

Our microservice also has a REST API which defines a single command (`GET /{engine}/model`).
This command will retrieve the source code of the currently running model. This
command is mapped to the `get_model` function in `default_controller.py`. Let's
edit it to retrieve the source:
```python
def get_model(engine):
    """
    get_model

    :param engine: The name of the engine instance
    :type engine: str

    :rtype: object
    """
    c = Connect(proxy_prefix=proxy_prefix())
    e = c.get(engine)
    if e.active_model is not None:
        return e.active_model.source
    return ''
```

Start the server with `python3 -m swagger_server`, and then, in another window,
a particular engine's running model (for example, the model running on `engine-2`)
can be retrieved with:
```
curl http://localhost:8123/engine-2/model
```

To complete this example, let's package up our microservice as a Docker container.
Conveniently, there's already a Dockerfile generated for us by Swagger-Codegen,
located in the `myserver` directory. We'll need to add the following lines to it
to install the ModelOp Center SDK:
```bash
WORKDIR /usr/src/app
RUN apk add --update openssl
RUN wget https://s3-us-west-1.amazonaws.com/ModelOp Center-sdk/ModelOp Center-dev.tar.gz
RUN pip3 install /usr/src/app/ModelOp Center-dev.tar.gz
```

In total, the Dockerfile should look like this:

**Dockerfile**
```bash
FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

WORKDIR /usr/src/app
RUN apk add --update openssl
RUN wget https://s3-us-west-1.amazonaws.com/ModelOp Center-sdk/ModelOp Center-dev.tar.gz
RUN pip3 install /usr/src/app/ModelOp Center-dev.tar.gz

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
```

Finally, build the Dockerfile with the following command from inside the `myserver`
directory:
```
docker build -t ModelOp Center-examples/microservice .
```

and run it with, for example,
```
docker run --net=host ModelOp Center-examples/microservice
```

You can download the entire project file for this example using the following
link:

* [Microservice Example Project](https://s3-us-west-1.amazonaws.com/ModelOp Center-examples/Microservice-Example.zip)
