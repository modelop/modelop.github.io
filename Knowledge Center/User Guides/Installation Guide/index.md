---
title: "ModelOp Center Installation Guide"
description: "How to install ModelOp Center with Docker or Kubernetes"
---


## Contents

1. [Overview](#the-preprocessor)
2. [The Postprocessor](#the-postprocessor)
3. [Setting up Composer](#setting-up-composer)
4. [Creating the Workflow in Designer](#creating-the-workflow-in-designer)
5. [Deploy and execute the Workflow](#deploy-and-execute-the-workflow)

## The Preprocessor

The preprocessor model accepts data from two different sources (S&P 500 closing
prices, and CPI), and uses that data to produce the transformed inputs that the
TensorFlow LSTM model needs to make its predictions. Recall that this transformation
consists of two steps: