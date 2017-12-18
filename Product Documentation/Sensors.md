---
title: "Sensors"
excerpt: ""
---
[block:api-header]
{
  "type": "basic",
  "title": "Overview"
}
[/block]
A sensor is a configurable function that:
* Can be turned on and off (installed/uninstalled)
* Is associated with a particular spot on the code path (a tapping point)
* Activates according to a schedule
* Can filter/aggregate measurements
* Publishes results separately from the output stream
* Has a language-agnostic descriptor
* May output cost-related information
Examples of potential uses for sensors include record/byte counters at the edge of an input stream, CPU utilization measurements for the main process, or a memory usage gauge for model runners. Some sensors are added to a FastScore microservice by default, e.g., the memory usage monitor present in Dashboard. 
[block:api-header]
{
  "type": "basic",
  "title": "Sensor Descriptors"
}
[/block]
A sensor descriptor is conceptually similar to a stream descriptor: it has a name, and is stored in Model Manage. A template for a sensor descriptor is:
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Tap\": \"sys.memory\",\n  \"Activate\": {\n    \"Type\": \"regular\",\n    \"Interval\": 0.5\n  },\n  \"Report\": {\n    \"Interval\": 3.0\n  },\n  \"Filter\": {\n    \"Type\":\">=\",\n    \"Threshold\":1G\n  }\n}",
      "language": "json"
    }
  ]
}
[/block]
This particular sensor reports system memory usage, but only if it exceeds 1 gigabyte.
[block:parameters]
{
  "data": {
    "h-0": "Field",
    "h-1": "Explanation",
    "h-2": "Type",
    "0-0": "`Tap`",
    "0-1": "The tapping point for the sensor. Currently, this can be either `\"sys.memory\"`, or `\"sys.cpu.utilization\"`.",
    "0-2": "`string`",
    "1-0": "`Activate`",
    "1-1": "A field to describe when to collect sensor readings. In the example, the sensor activates every 0.5 seconds.",
    "7-0": "`Report`",
    "7-1": "A field to describe when to report sensor readings. In the example, the sensor reports every 3 seconds.",
    "9-0": "`Filter`",
    "9-1": "The filtering function of the sensor. Defaults to null.",
    "10-0": "`Filter.Type`",
    "10-1": "Allowed values: `\">\"`, `\">=\"`, `\"<\"`, \"`<=`\", `\"within-range\"`, `\"outside-range\"`",
    "11-0": "`Filter.Threshold`",
    "11-1": "The threshold value for less-than or greater-than comparisons.",
    "12-0": "`Filter.MinValue`",
    "12-1": "The minimum value for range filters.",
    "13-0": "`Filter.MaxValue`",
    "13-1": "The maximum value for range filters.",
    "2-0": "`Activate.Type`",
    "2-1": "Allowed values: `\"permanent\"`, `\"regular\"`, `\"random\"`.",
    "3-0": "`Activate.Intensity`",
    "3-1": "The number of activation events per second. (The `Interval` element must be omitted.)",
    "4-0": "`Activate.Interval`",
    "4-1": "The time between activation events. (The `Intensity` element must be omitted.)",
    "5-0": "`Activate.Duration`",
    "5-1": "The time to keep the tapping point active.",
    "6-0": "`Activate.MaxReads`",
    "6-1": "Deactivate after receiving this many reads.",
    "1-2": "`object`",
    "2-2": "`string`",
    "3-2": "`float`",
    "4-2": "`float`",
    "5-2": "`float`",
    "6-2": "`int`",
    "7-2": "`object`",
    "8-0": "`Report.Interval`",
    "8-1": "How often to report sensor readings.",
    "8-2": "`float`",
    "9-2": "`object`",
    "10-2": "`string`",
    "11-2": "`float`",
    "12-2": "`float`",
    "13-2": "`float`",
    "14-0": "`Aggregate`",
    "14-1": "The aggregation function of the sensor. Accepts `\"accumulate\"`, `\"sum\"`, and `\"count\"` as shortcuts. Defaults to `\"accumulate\"`.",
    "14-2": "`object`",
    "15-0": "`Aggregate.Type`",
    "15-1": "One of `\"accumulate\"`, `\"sum\"`, or `\"count\"`.",
    "15-2": "`string`",
    "16-0": "`Aggregate.SampleSize`",
    "16-1": "The maximum number of values to accumulate.",
    "16-2": "`int`"
  },
  "cols": 3,
  "rows": 17
}
[/block]
Note that the filter values `Threshold`, `MinValue`, and `MaxValue` accept human-friendly values, e.g., "1G" instead of 1073741824. 
[block:api-header]
{
  "type": "basic",
  "title": "An Example"
}
[/block]
Let's add the sensor example above to FastScore. We can do this using the CLI:
```
fastscore sensor add s1 <<EOF
{
  "Tap": "sys.memory",
  "Activate": {
    "Type": "regular",
    "Interval": 0.5
  },
  "Report": {
    "Interval": 3.0
  }
}
EOF
```
After entering this command, the CLI will return `Sensor 's1' added` if the command was successful. 

Currently, all sensors have to be installed on Model Manage. Install the sensor:
```
$ fastscore tap install model-manage-1 s1
Sensor 's1' installed [2]
```
The number in the square brackets is the identifier of the sensor deployment. The identifier will be needed to stop the sensor later. It can also be found from the `fastscore tap list` command:
```
$ fastscore tap list model-manage-1
  Id  Tap         Active
----  ----------  --------
   2  sys.memory  No
```

The sensor activates periodically (2 times a second), and collects the memory consumed by the service. The collected data is reported as Pneumo messages (Kafka messages on the topic "notify") every 3 seconds. These can be viewed in the CLI with the `fastscore pneumo` command:
```
$ fastscore pneumo
[model-manage-1] 16:10:44 sys.memory [2] [2123345920, 2123345920, 2123345920, 2123345920, 2123345920, 2123345920]
[model-manage-1] 16:10:47 sys.memory [2] [2123345920, 2123345920, 2123345920, 2123345920, 2123345920, 2123345920]
[model-manage-1] 16:10:50 sys.memory [2] [2123345920, 2123345920, 2123345920, 2123345920, 2123345920, 2123345920]
```

The sensor can be uninstalled using the `fastscore tap uninstall` command:
```
$ fastscore tap uninstall model-manage-1 2
Sensor [2] uninstalled
```

Once uninstalled, these reports will no longer be send through Pneumo.
[block:api-header]
{
  "title": "Default Sensors"
}
[/block]
Eight sensors are installed in each engine by default:
```
  Id  Tap
----  ---------------------------------------
   1  manifold.1.records.size
   2  manifold.0.records.size
   3  manifold.1.records.rejected.by.encoding
   4  manifold.0.records.rejected.by.encoding
   5  manifold.1.records.count
   6  manifold.0.records.count
   7  manifold.1.records.rejected.by.schema
   8  manifold.0.records.rejected.by.schema
```

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/cf9e7de-Sensor1.png",
        "Sensor1.png",
        1920,
        1029,
        "#dee0e0"
      ],
      "caption": "This graph shows the Memory usage metrics that the sensor is capturing."
    }
  ]
}
[/block]

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/62ed12a-Sensor2.png",
        "Sensor2.png",
        1920,
        1027,
        "#e6e4e1"
      ],
      "caption": "These graphs show the throughput and count of records with that are rejected due to some specific issue and records that are accepted."
    }
  ]
}
[/block]