---
title: "FastStart with FastScore - Quick Setup Instructions"
excerpt: "Currently running with v1.6.1"
---
Get started with FastScore quickly by importing the FastScore Virtual Appliance into the Oracle VirtualBox Manager. We have made it easy by providing you with a pre-configured FastScore fleet and two demos that will walk you through deploying a model with FastScore:
* hello-world example
* Gradient Boosting Machine example
Models, streams, schemas, and data are provided. 

Watch our instructional video [here](http://docs.opendatagroup.com/docs/product-videos#faststart-with-fastscore-instructional-video) for more help on getting started!
[block:api-header]
{
  "type": "basic",
  "title": "Prerequisites"
}
[/block]
You must have Oracle VirtualBox installed on your machine.
[block:api-header]
{
  "title": "1. Download FastScore Virtual Appliance (OVA)"
}
[/block]
If you have not already, [click here to download!](http://www.opendatagroup.com/evaluate-fastscore "FastScore OVA")
[block:api-header]
{
  "title": "2. Open Oracle VirtualBox Manager and Import the OVA"
}
[/block]
Navigate to the "File" menu and select "Import Appliance"
[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/5344967-OVA1.png",
        "OVA1.png",
        329,
        301,
        "#f1f2f1"
      ]
    }
  ]
}
[/block]

[block:api-header]
{
  "title": "3. Review Default Settings"
}
[/block]
* Rename your Virtual System: Defaults to "FastScore Demo 1.6.1"
* Modify CPU / RAM: We don't recommend going below the default of 3072 MB

When you are finished modifying your settings, click Import.
[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/8aad9a9-OVA2.png",
        "OVA2.png",
        522,
        537,
        "#2d4173"
      ]
    }
  ]
}
[/block]
* The import process will start: This might take several minutes
* When the importing process is complete, the newly created machine will show up in the VirtualBox Manager list
[block:api-header]
{
  "title": "4. Power On the FastScore Machine"
}
[/block]
1. Click the FastScore Demo 1.6.1 machine in the list of virtual machines
2. Click Start from the toolbar - the boot process might take a few minutes and the console screen will be blank (or show Ubuntu start-up animation) during that time
[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/dbb3b59-OVA3.png",
        "OVA3.png",
        773,
        588,
        "#e5e5e4"
      ]
    }
  ]
}
[/block]
3. When the boot is complete, you will be presented with a prompt to login
[block:api-header]
{
  "title": "5. Login to the Box"
}
[/block]
When prompted, login to the box:
User: fastscore
Password: fastscore
Upon first login, the "hello-world" demo will launch automatically. Follow along by pressing Enter or press ctrl+c to escape the demo.

FastScore is now up and running. 
The FastScore Dashboard is accessible from your host: https://127.0.0.1:15080
You may also SSH into the box with the following command:
[block:code]
{
  "codes": [
    {
      "code": "$ ssh -p 15022 fastscore@127.0.0.1",
      "language": "shell"
    }
  ]
}
[/block]
You are now ready to start scoring!
[block:api-header]
{
  "title": "Additional Information"
}
[/block]
In addition to “hello-world”, FastScore OVA comes with pre-installed Gradient Boosting Machine (GBM) model example. In order to run it: 
[block:code]
{
  "codes": [
    {
      "code": "$ cd GBM\n$ ./prep.sh\n$ ./run.sh",
      "language": "text",
      "name": "Shell"
    }
  ]
}
[/block]
Note that first run might take time since required model packages are being installed into container. To view the output of the example (gbm_output.json):
[block:code]
{
  "codes": [
    {
      "code": "$ cd /opt/data\n$ less gbm_output.json",
      "language": "text",
      "name": "Shell"
    }
  ]
}
[/block]
Press `q` to escape.

You can start / stop / get status from / restart FastScore service using the following set of commands (make sure to use “sudo”): 
[block:code]
{
  "codes": [
    {
      "code": "$ sudo service fastscore start \n$ sudo service fastscore stop \n$ sudo service fastscore status \n$ sudo service fastscore restart",
      "language": "text",
      "name": "Shell"
    }
  ]
}
[/block]
Optionally, you can install FastScore CLI on your host running Virtual Box. This is how you connect CLI to FastScore on VM:
[block:code]
{
  "codes": [
    {
      "code": "$ fastscore connect https://127.0.0.1:15080",
      "language": "text",
      "name": "Shell"
    }
  ]
}
[/block]
You can also look at these scripts:
* prep.sh 
* run.sh 
* cleanup. sh 

under the GBM folder for self-explanatory CLI command examples.