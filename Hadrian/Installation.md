### Find what you're looking for:

   1. [You want to use Hadrian as a library in your JVM-based project](Installation#case-1-you-want-to-use-hadrian-as-a-library-in-your-jvm-based-project)
   2. [You want to use pre-built JAR files for one of the Hadrian containers](Installation#case-2-you-want-to-use-pre-built-jar-files-for-one-of-the-hadrian-containers)
   3. [You want to recompile Hadrian](Installation#case-3-you-want-to-recompile-hadrian)
   4. [You want to install Titus in Python](Installation#case-4-you-want-to-install-titus-in-python)
   5. [You want to use Aurelius in R](Installation#case-5-you-want-to-use-aurelius-in-r)

### Case 1: You want to use Hadrian as a library in your JVM-based project

Hadrian has these coordinates:

  * **Group id:** com.opendatagroup
  * **Artifact id:** hadrian
  * **Version:** 0.8.3

in this repository: http://repository.opendatagroup.com/maven

In Maven, you can add Hadrian by including the following in your pom.xml's `<dependencies>` section:

    <dependency>
      <groupId>com.opendatagroup</groupId>
      <artifactId>hadrian</artifactId>
      <version>0.8.3</version>
    </dependency>

and the following in its `<repositories>` section (create one if necessary):

    <repository>
      <id>opendatagroup</id>
      <url>http://repository.opendatagroup.com/maven</url>
    </repository>

Hadrian was built against Scala 2.10.4, so this is the version of `scala-library` that will be brought in as a dependency.

If you are using a different build system than Maven, use these coordinates in your build system.

### Case 2: You want to use pre-built JAR files for one of the Hadrian containers

The latest Hadrian version is 0.8.3. The latest JAR files and sources can be found [here](https://github.com/opendatagroup/hadrian/releases/tag/0.8.1). In particular, use

   * [hadrian-standalone-0.8.3-jar-with-dependencies.jar](https://github.com/opendatagroup/hadrian/releases/download/0.8.1/hadrian-standalone-0.8.1-jar-with-dependencies.jar) to run PFA and Jython (Antinous) scoring engines on a commandline through standard input and standard output.
   * [hadrian-standalone-0.8.3-exclude-antinous.jar](https://github.com/opendatagroup/hadrian/releases/download/0.8.1/hadrian-standalone-0.8.1-exclude-antinous.jar) to run PFA only on a commandline (35 MB smaller; no Jython libraries).
   * [hadrian-mr-0.8.3-jar-with-dependencies.jar](https://github.com/opendatagroup/hadrian/releases/download/0.8.1/hadrian-mr-0.8.1-jar-with-dependencies.jar) to run PFA and Jython in Hadoop map-reduce.
   * [hadrian-mr-0.8.3-exclude-antinous.jar](https://github.com/opendatagroup/hadrian/releases/download/0.8.1/hadrian-mr-0.8.1-exclude-antinous.jar) to run PFA only in Hadoop map-reduce.
   * [hadrian-actors-0.8.3.jar](https://github.com/opendatagroup/hadrian/releases/download/0.8.1/hadrian-actors-0.8.1.jar) to run PFA and Jython in an actor-based workflow.
   * [hadrian-gae-0.8.3.war](https://github.com/opendatagroup/hadrian/releases/download/0.8.1/hadrian-gae-0.8.1.war) to run PFA only in a Java servlet or Google App Engine.

### Case 3: You want to recompile Hadrian

Either [clone](https://github.com/opendatagroup/hadrian.git) or fork the [Hadrian repository](https://github.com/opendatagroup/hadrian). Make sure you have [Maven 3](https://maven.apache.org/download.cgi) installed (e.g. by `sudo apt-get install maven` on Ubuntu). The build order is

   1. Hadrian
   2. Antinous
   3. All Hadrian containers
      * Hadrian Standalone
      * Hadrian MR
      * Hadrian Actors
      * Hadrian GAE (Antinous is not required yet, but may be someday)

Navigate to the `hadrian` directory and run `mvn clean install`. Once that finishes (along with all unit tests), navigate to `antinous` and run `mvn clean install` there. Once that finishes, navigate to the desired container directory and run `mvn clean package`. The JARs will be in the `target` directory.

### Case 4: You want to install Titus in Python

Either [clone](https://github.com/opendatagroup/hadrian.git) or fork the [Hadrian repository](https://github.com/opendatagroup/hadrian). Make sure you have Python 2.6 or 2.7 installed (most operating systems and distributions do) as well as Python's Setuptools (e.g. by `sudo apt-get install python-setuptools` on Ubuntu). Navigate to the `titus` directory and run

    sudo python setup.py install

or

    python setup.py install --home=~

to install Titus in your local directory. In the latter case, you will have to set configure `PYTHONPATH` for Python to find your installation.

#### Debugging the Titus installation

Titus has a suite of unit tests, too. You can invoke them with

    python setup.py test

You can also verify that your installation completed properly by starting Python in a new terminal and typing

    import titus.version
    print titus.version.__version__

on the `>>>` prompt. If you get an `ImportError`, Python could not find your installation (check `PYTHONPATH` or `sys.path`).

If the installation failed with a complaint about `"python < 3.0"`, remove that requirement from the `setup.py`. Some versions of Python (particularly on Windows) have trouble with a less-than requirement, but as long as you're not using Python 3, it is automatically satisfied.

### Case 5: You want to use Aurelius in R

Download the latest package

   * [aurelius_0.8.3.tar.gz](https://github.com/opendatagroup/hadrian/releases/download/0.8.1/aurelius_0.8.1.tar.gz)

and install it in your R library with

    R CMD INSTALL aurelius_0.8.3.tar.gz

Now you should be able to

    library(aurelius)
    ?json

in an R session.

To validate or execute scoring engines, you will also have to install

   * [rPython](https://cran.r-project.org/web/packages/rPython/index.html) (depends on [RJSONIO](https://cran.r-project.org/web/packages/RJSONIO/index.html)) and
   * Titus (above).
