---
title: "Gradient Boosting Regressor"
excerpt: "Difficulty: Intermediate"
---
Gradient Boosting Regressors (GBR) are ensemble decision tree regressor models. In this example, we will show how to prepare a GBR model for use in FastScore. We'll be constructing a model to estimate the insurance risk of various automobiles. The data for this example is freely available from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Automobile).

The model will be constructed in Python using [SciKit Learn](http://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting), and both input and output data streams will use Kafka. This example demonstrates several features of FastScore:

1. Running a trained Python model in FastScore
2. Installing additional Python libraries in a FastScore engine
3. Using custom classes with model attachments
4. Scoring records over Kafka streams

All of the files needed to run this example are included [at the bottom of this post](#source-code-for-this-example). To run this locally, you'll need to have installed the following Python libraries:

* NumPy (`numpy`)
* Pandas (`pandas`)
* SciKit Learn (`sklearn`)
* Kafka (`kafka`, if you're using the included Python Kafka client)

Each of these libraries can be installed using `pip`. 
[block:api-header]
{
  "type": "basic",
  "title": "A Brief Review of Gradient Boosting Regressors"
}
[/block]
Gradient boosting regressors are a type of inductively generated tree ensemble model. At each step, a new tree is trained against the negative gradient of the loss function, which is analogous to (or identical to, in the case of least-squares error) the residual error.

More information on gradient boosting can be found below:

* [Wikipedia](https://en.wikipedia.org/wiki/Gradient_boosting)
* [SciKit Learn Gradient Boosting documentation](http://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting)
[block:api-header]
{
  "type": "basic",
  "title": "Training and Running a GBR Model in SciKit Learn"
}
[/block]
This section reviews how to train a GBR model using SciKit Learn in Python.

## The Dataset and the Model

In this example, we're using a GBR model to estimate insurance risk for various types of automobiles from various features of the vehicle. The scores produced are numbers between -3 and +3, where lower scores indicate safer vehicles.

## Transforming Features

To get the best results from our GBR model, we need to do some preprocessing of the input data. To keep the model itself as simple as possible, we will separate the feature preprocessing from the actual scoring, and encapsulate it in its own module:
[block:code]
{
  "codes": [
    {
      "code": "from itertools import chain\nimport numpy as np\nimport pandas as pd\nfrom sklearn.base import BaseEstimator, TransformerMixin\nfrom sklearn.preprocessing import Imputer, StandardScaler\nfrom sklearn.pipeline import Pipeline\n\n# define transformer to scale numeric variables \n# and one-hot encode categorical ones\nclass FeatureTransformer(BaseEstimator, TransformerMixin):\n    def __init__(self, transforms = [(\"impute\", Imputer()), (\"scale\", StandardScaler())]):\n        self.transforms = transforms\n    def fit(self, X, y = None):\n        self.columns_ = X.columns\n        self.cat_columns_ = X.select_dtypes(include = [\"object\"]).columns\n        self.non_cat_columns_ = X.columns.drop(self.cat_columns_)\n        self.pipe = Pipeline(self.transforms).fit(X.ix[:, self.non_cat_columns_])\n        self.cat_map_ = {col: X[col].astype(\"category\").cat.categories\n                         for col in self.cat_columns_}\n        self.ordered_ = {col: X[col].astype(\"category\").cat.ordered\n                         for col in self.cat_columns_}\n        self.dummy_columns_ = {col: [\"_\".join([col, v])\n                                     for v in self.cat_map_[col]]\n                               for col in self.cat_columns_}\n        self.transformed_columns_ = pd.Index(\n            self.non_cat_columns_.tolist() +\n            list(chain.from_iterable(self.dummy_columns_[k]\n                                     for k in self.cat_columns_))\n        )\n        return self\n    def transform(self, X, y = None):\n        scaled_cols = pd.DataFrame(self.pipe.transform(X.ix[:, self.non_cat_columns_]),\n                                   columns = self.non_cat_columns_).reset_index(drop = True)\n        cat_cols = X.drop(self.non_cat_columns_.values, 1).reset_index(drop = True)\n        scaled_df = pd.concat([scaled_cols, cat_cols], axis = 1)\n        final_matrix = (pd.get_dummies(scaled_df)\n                        .reindex(columns = self.transformed_columns_)\n                        .fillna(0).as_matrix())\n        return final_matrix\n",
      "language": "python",
      "name": "FeatureTransformer.py"
    }
  ]
}
[/block]
This is a utility class for imputing raw input records. A typical input record will look something like this:
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"engineLocation\": \"front\", \n  \"numDoors\": \"four\", \n  \"height\": 54.3, \n  \"stroke\": 3.4, \n  \"peakRPM\": 5500, \n  \"horsepower\": 102, \n  \"bore\": 3.19, \n  \"fuelType\": \"gas\", \n  \"cityMPG\": 24, \n  \"make\": \"audi\", \n  \"highwayMPG\": 30, \n  \"driveWheels\": \"fwd\", \n  \"width\": 66.2, \n  \"curbWeight\": 2337, \n  \"fuelSystem\": \"mpfi\", \n  \"price\": 13950, \n  \"wheelBase\": 99.8, \n  \"numCylinders\": \"four\", \n  \"bodyStyle\": \"sedan\", \n  \"engineSize\": 109, \n  \"aspiration\": \"std\", \n  \"length\": 176.6, \n  \"compressionRatio\": 10.0, \n  \"engineType\": \"ohc\"\n}",
      "language": "json"
    }
  ]
}
[/block]
Many of the features of this record (such as the manufacturer or body style of the car) are categorical, and the numerical variables have not been normalized. Gradient boosting models work best when all of the input features have been normalized to have zero mean and unit variance.

The `FeatureTransformer` class performs these imputations using two functions. First, `fit` trains the `FeatureTransformer` using the training data. This determines the mean and standard deviation of the training data and rescales the numerical inputs accordingly, as well as converts the categorical entries into collections of dummy variables with one-hot encoding. Fitting the FeatureTransformer is done as part of model training, as discussed below. 

The `transform` function is used during model scoring to perform streaming imputations of input records. The imputing is done using the information about the mean, variance, and categorical variables determined from the `fit` function. 

## Training the Model

We will use SciKit Learn to build and train our GBR model. First, import the following libraries:
[block:code]
{
  "codes": [
    {
      "code": "import cPickle\nimport numpy as np\nimport pandas as pd\nfrom sklearn.ensemble import GradientBoostingRegressor\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.model_selection import GridSearchCV\nfrom sklearn.metrics import mean_squared_error, make_scorer\nfrom FeatureTransformer import FeatureTransformer",
      "language": "python",
      "name": " "
    }
  ]
}
[/block]
`cPickle` will be used to store our fitted `FeatureTransformer`, and we'll use `numpy` and `pandas` to do some manipulations of the input data. Finally, the `sklearn` libraries are what we'll use to actually train the model. 

Building and training the model is fairly standard:
[block:code]
{
  "codes": [
    {
      "code": "# read in training data\nin_data = pd.read_json(\"train_data.json\", orient = \"records\")\nX = in_data.drop(\"risk\", 1)\ny = np.array(in_data[\"risk\"])\n\n# create feature transformation and training pipeline\npreprocess = FeatureTransformer()\ngbm = GradientBoostingRegressor(learning_rate = 0.1,\n                                random_state = 1234)\npipe = Pipeline([(\"preprocess\", preprocess), (\"gbm\", gbm)])\n\n# fit model\ngbm_cv = GridSearchCV(pipe,\n                      dict(gbm__n_estimators = [50, 100, 150, 200],\n                           gbm__max_depth = [5, 6, 7, 8, 9, 10]),\n                      cv = 5,\n                      scoring = make_scorer(mean_squared_error),\n                      verbose = 100)\ngbm_cv.fit(X, y)\n\n# pickle model\nwith open(\"gbmFit.pkl\", \"wb\") as pickle_file:\n    cPickle.dump(gbm_cv.best_estimator_, pickle_file)\n",
      "language": "python",
      "name": " "
    }
  ]
}
[/block]
Note that, because we're including our custom class `FeatureTransformer` as part of our data pipeline, we'll need to include the custom class file `FeatureTransformer.py` along with the actual pickled object `gbmFit.pkl` in our attachment.

## Scoring new records

Once the GBR model is trained, scoring new data is easy:
[block:code]
{
  "codes": [
    {
      "code": "import cPickle\nimport json\nimport numpy as np\nimport pandas as pd\nfrom sklearn.ensemble import GradientBoostingRegressor\nfrom sklearn.pipeline import Pipeline\nfrom FeatureTransformer import FeatureTransformer\n\n# load our trained model\nwith open('gbmFit.pkl', 'rb') as pickle_file:\n  gbmFit = cPickle.load(pickle_file)\n\n# each input record is delivered as a string\ndef score(record):\n  datum = json.loads(record)\n  score = list(gbmFit.predict(pd.DataFrame([datum]).replace(\"NA\", np.nan)))[0]\n  return json.dumps(score)\n",
      "language": "python",
      "name": null
    }
  ]
}
[/block]
In fact, as we'll see below, this model can be adapted essentially without modification for running in FastScore.
[block:api-header]
{
  "type": "basic",
  "title": "Loading the Model in FastScore"
}
[/block]
Loading our GBR model to FastScore can be broken into two steps: preparing the model code and creating the input and output streams. 

## Preparing the model for FastScore

In the previous section, we created a small Python script to score our incoming auto records using the trained gradient boosting regressor and our custom feature transformer. In this example, the training of the model has already been done, so we'll only need to adapt the trained model to produce scores.

As discussed in the [Getting Started Guide](doc:getting-started-with-fastscore), Python models in FastScore must deliver scores using an `action` method. Note that the `action` method operates as a generator, so scores are obtained from `yield` statements, rather than `return` statements. Additionally, because we don't want to re-load our trained model with every score, we'll define a `begin` method to do all of the model initialization. If a model defines a `begin` method, this method will be called at the start of the job.

After these alterations, our model looks like this:
[block:code]
{
  "codes": [
    {
      "code": "# fastscore.input gbm_input\n# fastscore.output gbm_output\n\nimport cPickle # unpickle a file\nimport imp # Load a custom class from the attachment\nimport numpy as np\nimport pandas as pd\nfrom sklearn.ensemble import GradientBoostingRegressor\nfrom sklearn.pipeline import Pipeline\n\n# GBM model\ndef begin():\n    FeatureTransformer = imp.load_source('FeatureTransformer', 'FeatureTransformer.py')\n    global gbmFit\n    with open(\"gbmFit.pkl\", \"rb\") as pickle_file:\n        gbmFit = cPickle.load(pickle_file)\n\ndef action(datum):\n    score = list(gbmFit.predict(pd.DataFrame([datum]).replace(\"NA\", np.nan)))[0]\n    yield score\n",
      "language": "python",
      "name": "score_auto_gbm.py"
    }
  ]
}
[/block]
Let's briefly review what changes were made between this script (which is ready for scoring in FastScore) and our original one.
* The input and output schemas have been specified in smart comments at the beginning of the model.
* The `score` method has been renamed to `action`, and all JSON deserialization and serialization of the input and output records is taken care of automatically by FastScore.
* The logic to load our pickled `gbmFit` object and any other initialization code is now put in a well-defined `begin` method, to be executed when the job starts. 
* Finally, because our custom class is contained in the attachment, we have to load it using Python's `imp` module (as opposed to `from FeatureTransformer import FeatureTransformer`).

## Input and Output Schemas

FastScore uses AVRO schemas to enforce type validation on model inputs and outputs. Both input/output streams, as well as the models themselves, must specify schemas.

The input schema for our data is somewhat complicated because the input records contain many fields.
[block:code]
{
  "codes": [
    {
      "code": "{\n    \"type\": \"record\",\n    \"name\": \"CarRecord\",\n    \"fields\": [\n      {\"name\": \"make\", \"type\": \"string\"},\n      {\"name\": \"fuelType\", \"type\": \"string\"},\n      {\"name\": \"aspiration\", \"type\": \"string\"},\n      {\"name\": \"numDoors\", \"type\": \"string\"},\n      {\"name\": \"bodyStyle\", \"type\": \"string\"},\n      {\"name\": \"driveWheels\", \"type\": \"string\"},\n      {\"name\": \"engineLocation\", \"type\": \"string\"},\n      {\"name\": \"wheelBase\", \"type\": \"double\"},\n      {\"name\": \"length\", \"type\": \"double\"},\n      {\"name\": \"width\", \"type\": \"double\"},\n      {\"name\": \"height\", \"type\": \"double\"},\n      {\"name\": \"curbWeight\", \"type\": \"int\"},\n      {\"name\": \"engineType\", \"type\": \"string\"},\n      {\"name\": \"numCylinders\", \"type\": \"string\"},\n      {\"name\": \"engineSize\", \"type\": \"int\"},\n      {\"name\": \"fuelSystem\", \"type\": \"string\"},\n      {\"name\": \"bore\", \"type\": \"double\"},\n      {\"name\": \"stroke\", \"type\": \"double\"},\n      {\"name\": \"compressionRatio\", \"type\": \"double\"},\n      {\"name\": \"horsepower\", \"type\": \"int\"},\n      {\"name\": \"peakRPM\", \"type\": \"int\"},\n      {\"name\": \"cityMPG\", \"type\": \"int\"},\n      {\"name\": \"highwayMPG\", \"type\": \"int\"},\n      {\"name\": \"price\", \"type\": \"int\"}\n    ]\n  }",
      "language": "json",
      "name": "gbm_input.avsc"
    }
  ]
}
[/block]
The output schema is much simpler---the output of the model will just be a double between -3 and 3.
[block:code]
{
  "codes": [
    {
      "code": "{ \"type\":\"double\" }",
      "language": "json",
      "name": "gbm_output.avsc"
    }
  ]
}
[/block]
## Input and Output Stream Descriptors

One of the key features of FastScore is that it enforces strong type contracts on model inputs and outputs: a model's inputs are guaranteed to match the specified input format, as are its outputs. The input and output streams are described using stream descriptors. In this example, we'll be using Kafka to both send and receive scores. 

For the output stream, the stream descriptor is simple:
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Transport\": {\n    \"Type\": \"kafka\",\n    \"BootstrapServers\": [\"127.0.0.1:9092\"],\n    \"Topic\": \"output\"\n  },\n  \"Envelope\": null,\n  \"Encoding\": \"json\",\n  \"Schema\": {\"$ref\":\"gbm_output\"}\n}",
      "language": "json",
      "name": "gbm-out.json"
    }
  ]
}
[/block]
This stream descriptor specifies that scores will be delivered on the "output" Kafka topic using the Kafka bootstrap server located at `127.0.0.01:9092`, and that the scores delivered will be of AVRO type `double`, as specified in the output schema (`gbm_output.avsc`)

The input stream descriptor includes the more complicated schema, encapsulating the various features of the automobile input records. We specify this schema by reference, so that both the model and the stream descriptor point to the same schema. This way, if there are any changes to the schema, the model and stream descriptor will both use the new schema. 
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Transport\": {\n    \"Type\": \"kafka\",\n    \"BootstrapServers\": [\"127.0.0.1:9092\"],\n    \"Topic\": \"input\"\n  },\n  \"Envelope\": null,\n  \"Encoding\": \"json\",\n  \"Schema\": { \"$ref\":\"gbm_input\"}\n}",
      "language": "json",
      "name": "gbm-in.json"
    }
  ]
}
[/block]
## Starting and Configuring FastScore

This step may differ if you're using a custom FastScore deployment. If you're just using the  [standard deployment from the Getting Started Guide](doc:getting-started-with-fastscore#section-using-fastscore-with-docker-compose-recommended-), starting up FastScore is as easy as executing the following command:

```
docker-compose up -d
```
[block:callout]
{
  "type": "warning",
  "body": "The instructions above assume that you already have configured and are currently running a Kafka server set up with topics for the input and output streams, as well as the `notify` topic used by FastScore for asynchronous notifications. \n\nIn the attached example code, we provide an additional docker-compose file (`kafka-compose.yml`) which will automatically start up Kafka docker containers configured for this example. Start the Kafka services from this docker-compose file with\n```\ndocker-compose -f kafka-compose.yml up -d\n```\n(You'll need to do this before starting FastScore).",
  "title": "A note on Kafka"
}
[/block]
Once the FastScore containers are up and running, configure them via the CLI:
```
fastscore connect https://dashboard-host:8000
fastscore config set config.yml
```
where `dashboard-host` is the IP address of the Dashboard container (if you're running the Dashboard container in `host` networking mode on your local machine as in the Getting Started Guide, this will just be `localhost`). 

After configuration, you should see that all of the containers are healthy, e.g., in the CLI, 
```
fastscore fleet
Name            API           Health
--------------  ------------  --------
engine-x-1      engine-x      ok
model-manage-1  model-manage  ok
```

## Adding Packages to FastScore

The model code we've written uses the `pandas` and `sklearn` Python packages, which we'll need to add to the FastScore Engine container. (It also uses the `numpy` package, but this is installed in FastScore by default.)

To add new packages to the engine container, there are two steps:
1. Install the package (for example, with pip).
2. Add the package to the list of installed modules.

To install the packages we need, execute the commands `pip install pandas` and `pip install sklearn` in the engine container. For example, using docker-compose:
```
docker-compose exec engine-1 pip install pandas
docker-compose exec engine-1 pip install sklearn
```

Next, add the novel packages our model uses to FastScore's `python.modules` list. (This list is used to check whether or not the current engine possesses the required dependencies for a model before attempting to run the model). The `python.modules` file is located inside of the engine container's file system at
```
/root/engine/lib/engine-1.3/priv/runners/python/python.modules
```
To add the needed modules to the container via docker-compose, execute the commands:
```
docker-compose exec engine-1 bash -c 'echo pandas >> /root/engine/lib/engine-1.3/priv/runners/python/python.modules'
docker-compose exec engine-1 bash -c 'echo sklearn.ensemble >> /root/engine/lib/engine-1.3/priv/runners/python/python.modules'
docker-compose exec engine-1 bash -c 'echo sklearn.pipeline >> /root/engine/lib/engine-1.3/priv/runners/python/python.modules'
```

If you'll be re-using this container later, you can save these changes (so that the packages don't need to be installed again in the future) with the `docker commit` command:
```
docker commit [name of engine container] [name for new engine image]
```
(After committing the new image, you'll have to update your docker-compose file to use the new image you created). 

## Creating the Attachment

In this section, it is assumed that you have created the model file `score_auto_gbm.py` as well as the input and output stream descriptors `gbm-in.json` and `gbm-out.json`, and  the pickled FeatureTransformer `gbmFit.pkl` and FeatureTransformer module `FeatureTransformer.py`. 

Once you've created these files, package these along with the FeatureTransformer class and pickled object into a .zip or .tar.gz archive. This archive should contain:
* `FeatureTransformer.py`
* `gbmFit.pkl`

You can call the attachment whatever you like---in the code sample, we've named it `gbm.tar.gz`

## Adding the model and stream descriptors

Now that we've created the model, stream descriptors, schemas, and attachment, it's time to add them to FastScore. This can be done through the command line, or using Dashboard.

From the command line, add the schemas and stream descriptors with
```
fastscore schema add gbm_input gbm_input.avsc
fastscore schema add gbm_output gbm_output.avsc
fastscore stream add GBM-in gbm-in.json
fastscore stream add GBM-out gbm-out.json
```
Add the model and attachment with
```
fastscore model add GBM score_auto_gbm.py
fastscore attachment upload GBM gbm.tar.gz
```

Steps for setting configuration through the Dashboard are covered in the [Getting Started Guide](doc:getting-started-with-fastscore#section-using-the-fastscore-dashboard). 

After adding the model, attachment, and streams to FastScore, you can inspect them from the FastScore Dashboard:
[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/d526fa7-dashboard-gbm-1.png",
        "dashboard-gbm-1.png",
        1409,
        630,
        "#e3e3e3"
      ],
      "caption": "The GBR model in FastScore's Dashboard."
    }
  ]
}
[/block]

[block:api-header]
{
  "type": "basic",
  "title": "Delivering Scores using Kafka"
}
[/block]
The final step is to run the model, and deliver input records and output scores with Kafka. Kafka producers and consumers can be implemented in many languages. In the example code attached to this tutorial, we include a simple Scala Kafka client (`kafkaesq`), which streams the contents of a file line-by-line over a specified input topic, and then prints any responses received on a specified output topic. However, FastScore is compatible with any implementation of Kafka producer/consumer. 

After FastScore is configured, we're ready to start scoring. Start the job from the CLI with
```
fastscore job run GBM GBM-in GBM-out
```
If you're using the included Kafka client script, score a file with
```
python kafkaesq --input-file /path/to/input/file.json input output
```
And that's it! Once you're done, stop the job with `fastscore job stop`. 
[block:api-header]
{
  "type": "basic",
  "title": "Source code for this Example"
}
[/block]
[Download the source files for this example (GBM_example.tar.gz).](https://github.com/opendatagroup/fastscore-tutorials/raw/master/GBM_example.tar.gz)

This archive contains all of the code used in this example.
[block:api-header]
{
  "type": "basic",
  "title": "Related Articles"
}
[/block]
1. [SciKit-Learn: Gradient Tree Boosting](http://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting)
2. [Wikipedia: Gradient Boosting](https://en.wikipedia.org/wiki/Gradient_boosting)
3. [J. Friedman: "Greedy Function Approximation: A Gradient Boosting Machine"](https://statweb.stanford.edu/~jhf/ftp/trebst.pdf)
4. [FastScore DockerHub repository](http://hub.docker.com/u/fastscore/)
5. [Automotive Sample Dataset](https://archive.ics.uci.edu/ml/datasets/Automobile)