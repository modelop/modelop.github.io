---
title: "Release Notes for FastScore v1.6.1"
excerpt: ""
---
## Highlights
Version 1.6 of FastScore introduces multiple input and output streams connected to an engine, Octave and MATLAB runner, and access to the R SDK.

## 1.6.1 

* REST Transport and Python3 fixes
* Stream Sampling for inline and REST transports
* Model Schema is used when missing from Stream Descriptor
* Loop is set to false by default in Stream Descriptors
* Stream profiling sensors
* S3 Authenticated Stream Transport

## 1.6.1 Model Deploy

* Multiple I/O Streams

## 1.6 Features

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


## Additional Notes
JSON-format PFA models are not supported in the new version of the FastScore CLI and must be added through the dashboard. YAML-format PFA models are unaffected.