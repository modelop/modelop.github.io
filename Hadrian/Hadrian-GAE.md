Hadrian-GAE wraps the Hadrian software library as a servlet that can be used in any servlet container (Tomcat, JBoss, WildFly, etc.) or Google App Engine (GAE). Google App Engine has strictly tighter constraints than standard servlet containers, so this project demonstrates that Hadrian can be executed in restricted environments that do not allow disk or operating system access. This is the server that backs the interactive examples in the [online PFA tutorials](http://dmg.org/pfa/docs/tutorial1/).

You can insert the [pre-built WAR](Installation#case-2-you-want-to-use-pre-built-jar-files-for-one-of-the-hadrian-containers) into any servlet container to start using Hadrian via REST queries, or you can [compile the sources](Installation#case-3-you-want-to-recompile-hadrian) to make modifications (such as adding built-in datasets).

Without modification, Hadrian-GAE accepts HTTP POST requests as JSON with the following form:

    {"document": PFA_IN_JSON_OR_YAML,
     "format": "json" or "yaml",
     "data": JSON_ENCODED_DATA}

or

    {"document": PFA_IN_JSON_OR_YAML,
     "format": "json" or "yaml",
     "dataset": NAME_OF_DATASET}

where `NAME_OF_DATASET` must be `"exoplanets"`. PFA in JSON format is embedded, PFA in YAML format is quoted.

With each request, a new PFA scoring engine is created, compiled, and applied to the given data or dataset. (Note that the compilation does not require disk access, which is strictly forbidden in the Google App Engine environment.) The result is returned as a JSON object if successful or non-JSON text if an exception occurred.

The [DMG website source code](https://github.com/datamininggroup/pfa-docs/blob/master/public/js/engine.js) provides an example of a user interface on top of the servlet REST calls.
