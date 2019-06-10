---
title: "Release Notes for FastScore"
excerpt: ""
---
## Highlights v1.10
Version 1.10 of FastScore includes an enhanced logging system through Kibana, and advanced approach to conforming a model, and full support for the Go CLI and SDK.

## What's New

### Advanced Conformance Approach

Additional “model conformance" approaches to support a larger variety of data scientist workflows and programming paradigms. For particular models, this approach streamlines the process for adding a new model into FastScore by allowing data scientists to simply change their model’s input and output data structures to read from the FastScore engine “slots.” A typical paradigm that data scientists use to structure their code includes: (1) reading in data (2) processing and scoring the data (3) writing the inference out to a consuming application or data feed. Through this feature, data scientists need only make minor modifications to steps 1 and 3, using the intuitive FastScore libraries. Note that FastScore will continue to support the prior “conformance” approaches, which are still well suited for certain classes of models (e.g. explicit RESTful models). This capability includes support for:

* Languages: R, Python (others to follow in subsequent dot releases)
* Jupyter Notebook Runner: allows data scientists to upload full Jupyter notebooks to be executed within the FastScore Engine. FastScore parses, prepares, and enables execution of the model in its Docker-based FastScore Engine. 

### Go CLI/SDK

Added full support for a Go SDK for core FastScore interactions, allowing data scientists, data engineers, model ops engineers, and others to leverage the rapidly-growing GO language for standard interactions and management of FastScore. We have also used the new Go SDK to improve our CLI so it no longer depends on python implementations, allowing for more portability.

### Enhanced Logging

Enhanced the core logging framework to leverage the ELK (Elasticsearch, Logstash, Kibana) stack, providing system architects and support engineers more flexibility to integrate FastScore’s logging and monitoring capabilities into existing enterprise systems and standards. 

### Additional Documentation/Training

Additional training curricula and documentation to enable data scientists, data engineers, and ModelOps/support engineers to be more self-sufficient in integrating models into the overall Model Lifecycle (MLC), powered by FastScore.

## Release v1.9

* [HDFS Native Stream](https://opendatagroup.github.io/Product%Manuals/Stream%Descriptors/#section-hdfs)
* [Ubuntu and Alpine based Engines](https://opendatagroup.github.io/Product%Manuals/Engine)
* [Kubernetes Support for Conductor](https://opendatagroup.github.io/Product%Manuals/FastScore%Composer)
* General improvements to performance and stability

## Release v1.8

* Enhanced CSV Encoding Support
* GitHub Integration - Secrets Support
* Enhanced Avro OCF Format Support
* Relaxed Avro Schema Matching
* S3 Transport Enhancements
* Enhanced C/C++ Model Support - Multiple Stream Capability
* Docker Secret Support for MySQL Backend and S3 Streams
* Msgpack Encoding
* General improvements to performance and stability

## Release v1.7

* FastScore Composer and Designer BETA 
* FastScore Compare BETA
* GitHub Integration
* Scala FastScore SDK
* Import Policy Enhancements
* General improvements to performance and stability

## Release v1.6.1

* REST Transport and Python3 fixes
* Stream Sampling for inline and REST transports
* Model Schema is used when missing from Stream Descriptor
* Loop is set to false by default in Stream Descriptors
* Stream profiling sensors
* S3 Authenticated Stream Transport
* Model Deploy - multiple I/O streams

## Release v1.6

* Multiple input and output streams
* Octave and MATLAB model language support
* R SDK
* 8 default sensors installed
* Executable stream type
* LDAP configuration through the dashboard
* Ability to download assets from the dashboard
* Authenticated Kafka stream type
* Additional sub-commands in the CLI
* General improvements to performance and stability