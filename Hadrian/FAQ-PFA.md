### Contents

   1. [What is PFA?](#what-is-pfa)
   2. [Why do we need it?](#why-do-we-need-it)

### What is PFA?

| PFA *is not:* | PFA *is:* |
|:--------------|:----------|
| A data pipeline framework, like Hadoop or Spark. | A specification for data analytics, the math that gets computed in Hadoop or Spark (or other frameworks). |
| A math library, like Apache Commons Math or Numpy. | A specification for expressing mathematical algorithms, which an implementation like Commons Math or Numpy can perform in response to a PFA-formatted request. |
| A graphical math formatting language, like LaTeX or MathML. | PFA is unconcerned with *presenting* math visually, only *computing* it. |
| A general-purpose programming language, like Java or Python. | A file format for expressing algorithms that might have been written in Java or Python and then converted to PFA.<br><br>Whereas human-oriented languages like Java or Python have a complex syntax and provide almost total control over a computer, including access to operating system calls, the file system, network ports, etc., PFA's syntax is a subset of JSON and it only provides the ability to do math.<br><br>The external system must feed data into PFA and interpret the results that come out. PFA provides separation between control system code (written in a general-purpose programming language) and mathematical algorithms, so that the mathematical algorithms can be tested and versioned more rapidly than the whole system. |
| Virtual bytecode, like LLVM or JVM executables. | While PFA is intended as an intermediate format for moving executable algorithms from one language or environment to another, it operates at a much higher level than bytecode. The names in JSON are human-readable and describe operations such as finding nearest clusters, walking through decision trees, and manipulating matrices. |
| A data mining/machine learning toolkit, like R, Scikit-Learn, MLlib, Mahout, Breeze... | Although PFA can be used to build models from training data ("fit" in R), its primary purpose is to apply fitted models ("predict" in R) in a formal or large-scale production.<br><br>Typically, one would use a data mining/machine learning toolkit to train a model, then convert it to PFA to get it into production. The production environment is usually more restricted than the development environment, since it is capable of performing business actions and must therefore be secure.<br><br>Some of these models might update internal state while performing their calculations, which is not completely distinct from training, so PFA has this ability and defines rules for distributed model updates. |
| PMML, the Predictive Model Markup Language | PFA's purpose is similar to PMML's, namely to provide an interchange format for data mining models (and other mathematical algorithms), but there are several structural differences.<ul><li>PMML is XML and PFA is JSON.<li>PMML defines [several high-level model types](http://dmg.org/pmml/v4-2-1/GeneralStructure.html), each with a suite of common options, whereas PFA defines [hundreds of data mining primitives](http://dmg.org/pfa/docs/library/) that can be combined in arbitrarily complex ways.<li>PFA has a [well-defined type system](http://dmg.org/pfa/docs/avro_types/), including arrays, maps, records, and tagged unions, whereas PMML operates on a flat table of numeric and string primitives.</ul> |

### Why do we need it?

**Suppose you're a data scientist,** working on a difficult analysis. You've been struggling with conventional data mining algorithms for weeks and suddenly have a breakthrough using Professor Hess's Gradient-Boosted Deep Learning Monte Carlo Adaptive Regularization Toolkit (GraBooDeLearnMicArt). Your amazingly accurate model could do a lot of good for your company, but its servers only run Java, and GraBooDeLearnMicArt is an R package.

You try to get your company to install an R-Java bridge, but they won't because they say it's a security hazard. They also say that GraBooDeLearnMicArt has seemingly unnecessary dependencies. The prospect of reimplementing it in Java is grim.

However, GraBooDeLearnMicArt's "predict" method isn't too complicated, only a mild variation on matrix multiplication and decision trees. You work with a Java developer to reimplement "predict," but after it's working, you realize you forgot a pre-processing step and have to change the code. A few weeks later, you decide to smooth the outputs. Of course, you'll be refreshing the models every month. The Java developer stops answering your calls.

**Suppose you're a data engineer,** trying to keep a thousand-node cluster healthy. Data scientists are constantly asking you why their jobs won't run, why they don't have permission to install random packages, when they can update their recommendation engines, etc. The code running on this cluster affects real things: monetary transactions, customer interactions, third-party corporate clients, perhaps even industrial machinery. It *has to* work.

Suddenly, somebody wants to install a hundred dependencies across the whole cluster to run some academic software with a long name. It side-steps Java's security model with compiled C code. Even trusting that the professor who wrote it is not deliberately malicious, it introduces the possibility of C array overflows that could be exploited through the web portal, potentially letting a hacker bring the whole system down, or worse. You say no.

In a hurried attempt to port the code, mistakes are made and the analyst is always wanting to change things. Even if you asked them to write it themselves, they would still have to pass code reviews and coordinate with the version schedule, like any other software developer.

**Here's how PFA helps.**

Suppose that the backend team installs a PFA implementation, such as Hadrian (Java). They wire this into the data pipeline as a black box: it makes predictions, recommendations, or actions based on some calculation in PFA.

The data science team installs PFA development kits, such as Titus (Python) or Aurelius (R). They produce models using whatever tools they want and use the PFA kit to convert these trained models into PFA. If they're lucky, the PFA kit knows about their tool and already has a conversion function. If not, they write the conversion themselves and add it to the library.

The PFA is a JSON file with a lot of model parameters and a little code. The code cannot break out of its sandbox because the necessary functions aren't even a part of the language. The data science team sends this to engineering in a formal way (e.g. database) and the PFA scoring engine can be plugged into the black box immediately. It won't cause any other system to fail to compile, run properly, or open security holes.

Before trusting the new model to perform actions, some review is necessary. However, that review can focus exclusively on its mathematical properties. Does it optimize sales? Does it improve manufacturing efficiency? These things could even be demonstrated with a champion-challenger system that applies the new PFA to live data in the real production system.

Control code and mathematical analyses are now decoupled. They can progress according to their own schedules.
