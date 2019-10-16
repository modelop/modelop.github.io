---
title: "Release Notes for ModelOp Center"
excerpt: ""
---
## Highlights v1.10
New capabilities in Release 1.10 further accelerates the deployment process by streamlining model on-boarding into ModelOp Center. Through ModelOp Center’s powerful but lightweight abstractions, data scientists can encapsulate their models for easy deployment through the ModelOp Center System without any re-coding or refactoring.  Release 1.10 streamlines conformance to ModelOp Center’s abstractions for a large number of additional classes of models. Additionally, Release 1.10 adds automated schema inference to allow data scientists to quickly generate the externalized schemas to ensure compatibility of data streams with the model.  

## What's New

### Advanced Conformance Approach

Additional “model conformance" approaches to support a larger variety of data scientist workflows and programming paradigms. For particular models, this approach streamlines the process for adding a new model into ModelOp Center by allowing data scientists to simply change their model’s input and output data structures to read from the ModelOp Center engine “slots.” A typical paradigm that data scientists use to structure their code includes: (1) reading in data (2) processing and scoring the data (3) writing the inference out to a consuming application or data feed. Through this feature, data scientists need only make minor modifications to steps 1 and 3, using the intuitive ModelOp Center libraries. Note that ModelOp Center will continue to support the prior “conformance” approaches, which are still well suited for certain classes of models (e.g. explicit RESTful models). This capability includes support for:

* Languages: Python (others to follow in subsequent dot releases)
* Local-mode support: support for testing the model in one’s local environment before uploading into a ModelOp Center fleet.

### Auto Schema Creation
Added a schema inference utility to generate the ModelOp Center-compliant data schema automatically from a sample data file. 


### Go CLI/SDK

Added full support for a Go SDK for core ModelOp Center interactions, allowing data scientists, data engineers, model ops engineers, and others to leverage the rapidly-growing GO language for standard interactions and management of ModelOp Center. We have also used the new Go SDK to improve our CLI so it no longer depends on python implementations, allowing for more portability.

### Enhanced Logging

Enhanced the core logging framework to leverage the ELK (Elasticsearch, Logstash, Kibana) stack, providing system architects and support engineers more flexibility to integrate ModelOp Center’s logging and monitoring capabilities into existing enterprise systems and standards. 



## Release v1.9

* [HDFS Native Stream](https://opendatagroup.github.io/Product%Manuals/Stream%Descriptors/#section-hdfs)
* [Ubuntu and Alpine based Engines](https://opendatagroup.github.io/Product%Manuals/Engine)
* [Kubernetes Support for Conductor](https://opendatagroup.github.io/Product%Manuals/ModelOp%20Center%Composer)
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

* ModelOp Center Composer and Designer BETA 
* ModelOp Center Compare BETA
* GitHub Integration
* Scala ModelOp Center SDK
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
