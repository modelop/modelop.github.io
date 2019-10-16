---
title: "Model Deploy"
excerpt: "Deploying models from Jupyter Notebooks"
---
# Model Deploy

ModelOp Center Model Deploy is a containerized Jupyter notebook server with ModelOp Center's model deployment and Jupyter integration toolkit built in. It is built on top of the [Jupyter data science Docker image](https://hub.docker.com/r/jupyter/datascience-notebook/). Model Deploy provides model creation and deployment tools for R and Python (2 & 3) notebooks, as well as for PFA (through Python 2). 

## Starting Model Deploy

Start Model Deploy with the following command:
```
docker run -it --rm -p 8888:8888 fastscore/model-deploy:latest
```
If other services in the ModelOp Center fleet are also running on the same host, it may be advantageous to start Model Deploy with the `--net="host"` option, so that these services are accessible from `localhost`. 

Model Deploy may also be started with any of the additional configuration options available to the Jupyter base Docker image, [see the documentation for more details](https://github.com/jupyter/docker-stacks/tree/master/datascience-notebook). 

Once the container is created, it will be accessible from port 8888 (by default) on the host machine, using the token generated during the startup process.

## Install to Existing Jupyter Notebook

Model Deploy is also avaiable via the `fastscoredeploy` library and can be installed using `pip install fastscoredeploy` from within the Jupyter Notebook terminal.  

## Model Deploy functionality

Model Deploy provides a number of features to make it easy to migrate a model into ModelOp Center:

* Python and R supply a `Model` class that can be used for validation and testing of a model locally, before deploying to a ModelOp Center engine.
* The `Model.from_string` (Python) and `Model_from_string` (R) functions provide shortcuts for creating a Model object from a string of code. In Python notebooks, the `%%py2model`, `%%py3model`, `%%pfamodel`, and `%%ppfamodel` cell magic commands will automatically convert the contents of a cell into a Python or (P)PFA model object, respectively.
* The `Engine` class allows for direct interaction with a ModelOp Center Engine, including scoring data using a running Engine
* `Model` objects may be deployed directly to a ModelOp Center Engine from within the Jupyter notebook, as well as to Model Manage.
* A utility `codec` library is included to make it easy to serialize R and Python objects to JSON and other formats based on an Avro schema.

Example notebooks demonstrating this functionality are included with the Model Deploy container.

