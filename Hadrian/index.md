## Hadrian Wiki

This wiki provides documentation for the Hadrian ecosystem of tools.

   * [PFA: frequently asked questions](FAQ-PFA)
   * [Hadrian: frequently asked questions](FAQ-Hadrian)

### First steps

   * [How to install](Installation): start here!
   * [Tutorial 1](Tutorial-Small-Model-Titus): Building and testing a small model in Titus (Python)
   * [Tutorial 2](Tutorial-Small-Model-R): Building a small model in Aurelius (R)
   * [Tutorial 3](Tutorial-Inspecting-Model): Inspecting a model in PFA-Inspector (commandline)
   * [Tutorial 4](Tutorial-Executing-Model-in-JVM): Executing a model in hadrian-standalone (JVM)
   * Basic models: simple examples in Titus PrettyPFA
     * [Association rules](Basic-association-rules)
     * [Baseline models](Basic-baseline-models)
     * [Clustering models](Basic-clustering-models)
     * [Decision tree](Basic-decision-tree)
     * [Gaussian Process](Basic-gaussian-process)
     * [Naive bayes](Basic-naive-bayes)
     * [Nearest neighbors](Basic-nearest-neighbors)
     * [Neural network](Basic-neural-network)
     * [Random forest](Basic-random-forest)
     * [Regression](Basic-regression)
     * [Ruleset](Basic-ruleset)
     * [Scorecard](Basic-scorecard)
   * [Moving windows](Moving-windows): How to add moving windows to your preprocessing
   * [Segmentation](Segmentation): How to subdivide a model into segments
   * [Concurrency](Concurrency): Running multiple scoring engines simultaneously

### Hadrian (Java/Scala/JVM)

<!-- <img src="https://github.com/opendatagroup/hadrian/wiki/images/hadrian_small.jpg" align="right" hspace="10"> -->

**Hadrian** is a complete implementation of PFA in **Scala**, which can be accessed through any JVM language, principally **Java**. It focuses on model deployment, so it is flexible (can run in restricted environments) and fast.

   * [Complete API reference](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.jvmcompiler.PFAEngine) (Scaladoc)
   * [Performance table](http://modelop.github.io//hadrian/hadrian-0.8.1-performance/)
   * Using Hadrian directly
     * [Loading, validating, and executing PFA](Hadrian-Basic-Use) on the Scala command prompt
     * [Hadrian's internal data format and serialization](Hadrian-Data-Format)
     * [Analysis of a PFA engine](Hadrian-Analyzing-Engine), including call graphs, and mutability checks, and memory use
     * [Embedding Hadrian](Embedding-Hadrian) in your Java or Scala program
   * Ready-to-use Hadrian wrappers:
     * [Hadrian-Standalone](Hadrian-Standalone): command-line program that reads data from standard input and writes it to standard output: use this for testing or a simple shell-based workflow
     * [Hadrian-MR](Hadrian-MR): Hadoop executable that runs two PFA files as mapper and reducer. Has built-in secondary sort: use this for running fast Hadoop jobs with no compilation
       * [Usage as a model producer](Hadrian-MR-as-a-Producer): snapshot and Antinous
     * [Hadrian-GAE](Hadrian-GAE): Java servlet that runs PFA as a service in Google App Engine or any servlet container, such as Tomcat, JBoss, or WildFly: this is the backend for [scoringengine.org](http://scoringengine.org/)
     * [Hadrian-Actors](Hadrian-Actors): actor-based network of interacting PFA scoring engines: use this for building data pipelines in a JVM
       * [Workflow configuration language](Hadrian-Actors-Configuration)

<br clear="right">

### Titus (Python)

<!-- <img src="https://github.com/opendatagroup/hadrian/wiki/images/titus_small.jpg" align="right" hspace="10"> -->

**Titus** is a complete, independent implementation of PFA in pure **Python**. It focuses on model development, so it includes model producers and PFA manipulation tools in addition to runtime execution.

   * [Complete API reference](http://modelop.github.io//hadrian/titus-0.8.3/titus.genpy.PFAEngine.html) (Sphinx)
   * [Loading, validating, and executing PFA](Titus-Basic-Use) on the Python command prompt
   * PFA development tools
     * PrettyPFA is a more human-readable syntax that converts into PFA: use this to write PFA "code"
       * [Simple example](PrettyPFA-Simple-Example): the quadratic formula
       * [Realistic example](PrettyPFA-Realistic-Example): manipulating an exoplanets dataset
       * [Titus functions](PrettyPFA-Titus-Functions) that produce PFA from PrettyPFA
       * [PrettyPFA complete reference](PrettyPFA-Reference) that shows how to produce any PFA structure from a PrettyPFA document
     * [PFA navigation](Titus-PFA-navigation) (look function)
     * [JSON regular expressions](JSON-Regular-Expressions): find and change parts of a PFA document declaratively
     * [Convert PMML into PFA](PMML-into-PFA)
   * Model producers in Titus
     * [CUSUM tutorial](Producing-CUSUM-models-in-Titus): an example of building a model primarily with PrettyPFA
     * [K-means reference](Producing-k-means-models-in-Titus): building cluster models with Titus
     * [CART reference](Producing-tree-models-in-Titus): building decision trees with Titus
     * [Transformations producer](Preprocessing-in-Titus): coordinates operations on Numpy arrays in the producer stage with PFA code in the runtime scoring engine, for developing pre- and post-processors
   * Ready-to-use Titus scripts:
     * [pfainspector](Titus-pfainspector): command-line tool (with history and tab-complete) for inspecting PFA documents (or other JSON): use this to diagnose faulty PFA
     * [pfachain](Titus-pfachain): turns a linear sequence of PFA files into a combined PFA file, with schema-checking and renaming to avoid namespace collisions
     * [pfaexternalize](Titus-pfaexternalize): moves large data blocks from a PFA file into external JSON for faster loading (uses [ijson](https://pypi.python.org/pypi/ijson))
     * [pfarandom](Titus-pfarandom): given an input and output schema, creates a PFA file to fit these schama (the PFA file ignores input and generates random outputs)

<br clear="right">

### Aurelius (R)

<!-- <img src="https://github.com/opendatagroup/hadrian/wiki/images/aurelius_small.jpg" align="right" hspace="10"> -->

**Aurelius** is a toolkit for generating PFA in the **R programming language**. It focuses on porting models to PFA from their R equivalents. To validate or execute scoring engines, Aurelius sends them to Titus through [rPython](https://cran.r-project.org/web/packages/rPython/index.html) (so both must be installed).

   * [R-to-PFA code reference](Aurelius-Rcode-Transformation)
   * [Complete API reference](Aurelius-Reference)
   * Converting R models
     * [glm](Aurelius-glm)
     * [glmnet](Aurelius-glmnet)
     * [randomForest](Aurelius-randomForest)
     * [gbm](Aurelius-gbm)

<br clear="right">

### Antinous (Model development in Jython)

<!-- <img src="https://github.com/opendatagroup/hadrian/wiki/images/antinous_small.jpg" align="right" hspace="10"> -->

**Antinous** is a model-producer plugin for Hadrian that allows **Jython** code to be executed anywhere a PFA scoring engine would go. It also has a library of model producing algorithms.

   * [Interaction between PFA, Jython, and Scala/Java code](Antinous-basics)
   * [Producer interface](Antinous-producers)
