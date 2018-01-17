---
description: How to Quickly Get Started with the FastScore OVA
title: Quick Start with the FastScore OVA
---

Get started with FastScore quickly by importing the FastScore Virtual Appliance into the Oracle VirtualBox Manager. We have made it easy by providing you with a pre-configured FastScore fleet and two demos that will walk you through deploying a model with FastScore:

* hello-world example
* Gradient Boosting Machine example
Models, streams, schemas, and data are provided. 

Watch our instructional video [here](http://docs.opendatagroup.com/docs/product-videos#faststart-with-fastscore-instructional-video) for more help on getting started!

## Prerequisites

You must have Oracle VirtualBox installed on your machine.

## 1. Download FastScore Virtual Appliance (OVA)
  
If you have not already, [click here to download!](http://www.opendatagroup.com/evaluate-fastscore "FastScore OVA")

## 2. Open Oracle VirtualBox Manager and Import the OVA
  
Navigate to the "File" menu and select "Import Appliance"

![OVA Image](images/OVA1.png)

## 3. Review Default Settings

* Rename your Virtual System: Defaults to "FastScore Demo 1.6.1"
* Modify CPU / RAM: We don't recommend going below the default of 3072 MB

When you are finished modifying your settings, click Import.

![OVA Image](images/OVA2.png)

* The import process will start: This might take several minutes
* When the importing process is complete, the newly created machine will show up in the VirtualBox Manager list

## 4. Power On the FastScore Machine

1. Click the FastScore Demo 1.6.1 machine in the list of virtual machines
2. Click Start from the toolbar - the boot process might take a few minutes and the console screen will be blank (or show Ubuntu start-up animation) during that time

![OVA Image](images/OVA3.png)

3. When the boot is complete, you will be presented with a prompt to login

## 5. Login to the Box

When prompted, login to the box:
User: fastscore
Password: fastscore
Upon first login, the "hello-world" demo will launch automatically. Follow along by pressing Enter or press ctrl+c to escape the demo.

FastScore is now up and running. 
The FastScore Dashboard is accessible from your host: https://127.0.0.1:15080
You may also SSH into the box with the following command:

``` bash
$ ssh -p 15022 fastscore@127.0.0.1
```

You are now ready to start scoring!

## Additional Information

In addition to “hello-world”, FastScore OVA comes with pre-installed Gradient Boosting Machine (GBM) model example. In order to run it: 

``` bash
$ cd GBM
$ ./prep.sh
$ ./run.sh
```

Note that first run might take time since required model packages are being installed into container. To view the output of the example (gbm_output.json):

``` bash
$ cd /opt/data
$ less gbm_output.json
```

Press `q` to escape.

You can start / stop / get status from / restart FastScore service using the following set of commands (make sure to use “sudo”): 

``` bash
$ sudo service fastscore start 
$ sudo service fastscore stop 
$ sudo service fastscore status 
$ sudo service fastscore restart
```

Optionally, you can install FastScore CLI on your host running Virtual Box. This is how you connect CLI to FastScore on VM:

``` bash
$ fastscore connect https://127.0.0.1:15080
```

You can also look at these scripts:

* prep.sh 
* run.sh 
* cleanup. sh 

under the GBM folder for self-explanatory CLI command examples.
