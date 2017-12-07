---
title: Developer interface
---

Service instances
=================

**class fastscore.suite.Connect(proxy\_prefix, auth\_secret=None)**

> An instance of a Connect service.
>
> Typically, an interaction with FastScore starts with:
>
> &gt;&gt;&gt; from fastscore.suite import Connect &gt;&gt;&gt; connect
> = Connect("<https://localhost:8000>")
>
> Afterwards, you can use 'connect' to access other FastScore instances.
> For example:
>
> &gt;&gt;&gt; engine = connect.lookup('engine')
>
> `active_sensors`
>
> > A collection of currently installed sensors indexed by id.
> >
> > &gt;&gt;&gt; engine = connect.lookup('engine') &gt;&gt;&gt;
> > engine.active\_sensors.keys() \[8\] &gt;&gt;&gt; x =
> > engine.active\_sensors\[8\] &gt;&gt;&gt; x.id 8 &gt;&gt;&gt; x.tap
> > manifold.input.records.count &gt;&gt;&gt; x.uninstall() &gt;&gt;&gt;
> > engine.active\_sensors.ids() \[\]
>
> **check\_health()**
>
> > Retrieves version information from the instance. A successful reply
> > indicates that the instance is healthy.
> >
> > &gt;&gt;&gt; connect.check\_health() { 'id':
> > '366e5030-d773-49cb-8b28-9b1b9d173c79', 'built\_on': 'Thu May 11
> > 12:53:39 UTC 2017', 'release': '1.5' }
>
> **configure(config)**
>
> > Sets the FastScore configuration.
> >
> > &gt;&gt;&gt; with open('config.yaml') as f: &gt;&gt;&gt;
> > connect.configure(yaml.load(f)) False
> >
> > Parameters
> >
> > :   **config** -- a dict describing a FastScore configuration.
> >
> > Returns
> >
> > :   True, if an existing configuration has been replaced and False,
> >     otherwise.
> >
> **dump(savefile)**
>
> > Saves the Connect parameters to a file.
> >
> > &gt;&gt;&gt; connect.dump(".fastscore")
>
> **fleet()**
>
> > Retrieves metadata for all running instances.
> >
> > Returns
> >
> > :   an array of dicts describing running FastScore instances. Each
> >     dict contains the following fields:
> >
> >     -   **id**: the internal instance id (do not use)
> >     -   **api**: the service name, e.g. 'model-manage'
> >     -   **release**: the instance release, e.g '1.5'
> >     -   **built\_on**: the human-readable build date and time
> >     -   **host**: the host name of the instance REST API
> >     -   **port**: the port of the instance REST API
> >     -   **health**: the current health status of the instance.
> >
> **get(name)**
>
> > Retrieves a (cached) reference to the named instance.
> >
> > &gt;&gt;&gt; mm = connect.get('model-manage-1') &gt;&gt;&gt; mm.name
> > 'model-manage-1'
> >
> > Parameters
> >
> > :   **name** -- a FastScore instance name.
> >
> > Returns
> >
> > :   a FastScore instance object.
> >
> **get\_config(section=None)**
>
> > Retrieves the current FastScore configuration.
> >
> > &gt;&gt;&gt; connect.config('db') { 'username': 'root', 'host':
> > 'database', 'password': 'root', 'type': 'mysql', 'port': 3306 }
> >
> > Parameters
> >
> > :   **section** -- gets only the named section of the configuration
> >
> > Returns
> >
> > :   a dict with the FastScore configuration.
> >
> **get\_swagger()**
>
> > Retrieves the Swagger specification of the API supported by the
> > instance.
> >
> > &gt;&gt;&gt; connect.get\_swagger() {u'info':...}
>
> `static load(savefile)`
>
> > Recreates a Connect instance from a file.
> >
> > &gt;&gt;&gt; connect = Connect.load(".fastscore")
>
> **login(username, password)**
>
> > Login to FastScore.
> >
> > Parameters
> >
> > :   -   **username** -- a user name.
> >     -   **password** -- a password.
> >
> **lookup(sname)**
>
> > Retrieves an preferred/default instance of a named service.
> >
> > &gt;&gt;&gt; engine = connect.lookup('engine') &gt;&gt;&gt;
> > engine.name 'engine-1'
> >
> > Parameters
> >
> > :   **sname** -- a FastScore service name, e.g. 'model-manage'.
> >
> > Returns
> >
> > :   a FastScore instance object.
> >
> `pneumo`
>
> > Access Pneumo messages.
> >
> > &gt;&gt;&gt; pneumo = connect.pneumo.socket() &gt;&gt;&gt;
> > pneumo.recv() &gt;&gt;&gt; pneumo.close()
> >
> > &gt;&gt;&gt; connect.pneumo.history()
>
> **prefer(sname, name)**
>
> > Marks the named instance as preferred for a given service.
> >
> > &gt;&gt;&gt; connect.prefer('engine', 'engine-3') &gt;&gt;&gt;
> > engine = connect.lookup('engine') &gt;&gt;&gt; engine.name
> > 'engine-3'
> >
> > Parameters
> >
> > :   -   **sname** -- a FastScore service name, e.g. 'model-manage'.
> >     -   **name** -- the name of preferred instance of the given
> >         service.
> >
> `tapping_points`
>
> > A list of tapping points supported by the instance.
> >
> > &gt;&gt;&gt; mm.tapping\_points \['sys.memory',... \]
>
> `target`
>
> > Gets/Sets the target instance. When set, the target instance also
> > becomes the preferred instance of the service it represents.
> >
> > &gt;&gt;&gt; engine = connect.get('engine-3') &gt;&gt;&gt;
> > connect.target = engine

**class fastscore.suite.ModelManage(name)**

> An instance of a Model Manage service. Use `Connect` to create a
> ModelManage instance:
>
> &gt;&gt;&gt; mm = connect.lookup('model-manage')
>
> `active_sensors`
>
> > A collection of currently installed sensors indexed by id.
> >
> > &gt;&gt;&gt; engine = connect.lookup('engine') &gt;&gt;&gt;
> > engine.active\_sensors.keys() \[8\] &gt;&gt;&gt; x =
> > engine.active\_sensors\[8\] &gt;&gt;&gt; x.id 8 &gt;&gt;&gt; x.tap
> > manifold.input.records.count &gt;&gt;&gt; x.uninstall() &gt;&gt;&gt;
> > engine.active\_sensors.ids() \[\]
>
> **check\_health()**
>
> > Retrieves version information from the instance. A successful reply
> > indicates that the instance is healthy.
> >
> > &gt;&gt;&gt; connect.check\_health() { 'id':
> > '366e5030-d773-49cb-8b28-9b1b9d173c79', 'built\_on': 'Thu May 11
> > 12:53:39 UTC 2017', 'release': '1.5' }
>
> **get\_swagger()**
>
> > Retrieves the Swagger specification of the API supported by the
> > instance.
> >
> > &gt;&gt;&gt; connect.get\_swagger() {u'info':...}
>
> `models`
>
> > A collection of `Model` objects indexed by model name.
> >
> > &gt;&gt;&gt; mm.models.names() \[u'model-1'\] &gt;&gt;&gt; model =
> > mm.models\['model-1'\] &gt;&gt;&gt; model.mtype 'python'
> > &gt;&gt;&gt; del mm.models\['model-1'\] &gt;&gt;&gt;
> > mm.models.names() \[\]
>
> `schemata`
>
> > A collection of `Schema` objects indexed schema name. The
> > alternative name for the property is 'schemas'.
> >
> > &gt;&gt;&gt; from fastscore import Schema &gt;&gt;&gt; s =
> > Schema('schema-1') &gt;&gt;&gt; s.source = '{"type": "string"}'
> > &gt;&gt;&gt; s.update(mm) False \# Success; schema created, not
> > updated &gt;&gt;&gt; mm.schemata.names() \['schema-1'\] &gt;&gt;&gt;
> > del mm.schemata\['schema-1'\] &gt;&gt;&gt; mm.schemata.names() \[\]
>
> `sensors`
>
> > A collection of `Sensor` objects indexed by sensor name.
> >
> > &gt;&gt;&gt; from fastscore import Sensor &gt;&gt;&gt; s =
> > Sensor('sensor-1') &gt;&gt;&gt; s.desc = {'tap':
> > 'manifold.input.records.size',... } &gt;&gt;&gt; s.update(mm) False
> > \# Success; sensor created, not updated &gt;&gt;&gt;
> > mm.sensors.names() \['sensor-1'\] &gt;&gt;&gt; del
> > mm.sensors\['sensor-1'\] &gt;&gt;&gt; mm.sensors.names() \[\]
>
> `streams`
>
> > A collection of `Stream` objects indexed by stream name.
> >
> > &gt;&gt;&gt; mm.streams.names() \['demo-1','demo-2\] &gt;&gt;&gt;
> > mm.streams\['demo-1'\].desc {u'Description': u'A demo stream... }
> > &gt;&gt;&gt; del.strems\['demo-2'\] &gt;&gt; mm.streams.names()
> > \['demo-1'\]
>
> `tapping_points`
>
> > A list of tapping points supported by the instance.
> >
> > &gt;&gt;&gt; mm.tapping\_points \['sys.memory',... \]

**class fastscore.suite.Engine(name)**

> An Engine instance.
>
> `active_model`
>
> > The currently loaded model information.
> >
> > &gt;&gt;&gt; mm = connect.lookup('model-manage') &gt;&gt;&gt; engine
> > = connect.lookup('engine') &gt;&gt;&gt; print
> > stream.active\_model.name &gt;&gt;&gt; print
> > stream.active\_model.jets
> >
> > Returns
> >
> > :   An ActiveModelInfo object.
> >
> `active_sensors`
>
> > A collection of currently installed sensors indexed by id.
> >
> > &gt;&gt;&gt; engine = connect.lookup('engine') &gt;&gt;&gt;
> > engine.active\_sensors.keys() \[8\] &gt;&gt;&gt; x =
> > engine.active\_sensors\[8\] &gt;&gt;&gt; x.id 8 &gt;&gt;&gt; x.tap
> > manifold.input.records.count &gt;&gt;&gt; x.uninstall() &gt;&gt;&gt;
> > engine.active\_sensors.ids() \[\]
>
> `active_streams`
>
> > A collection of active streams indexed by a slot.
> >
> > &gt;&gt;&gt; mm = connect.lookup('model-manage') &gt;&gt;&gt; engine
> > = connect.lookup('engine') &gt;&gt;&gt; print
> > stream.active\_streams\[1\]
>
> **check\_health()**
>
> > Retrieves version information from the instance. A successful reply
> > indicates that the instance is healthy.
> >
> > &gt;&gt;&gt; connect.check\_health() { 'id':
> > '366e5030-d773-49cb-8b28-9b1b9d173c79', 'built\_on': 'Thu May 11
> > 12:53:39 UTC 2017', 'release': '1.5' }
>
> **get\_swagger()**
>
> > Retrieves the Swagger specification of the API supported by the
> > instance.
> >
> > &gt;&gt;&gt; connect.get\_swagger() {u'info':...}
>
> **input(data, slot)**
>
> > Write data to a REST stream attached to the slot.
> >
> > Parameters
> >
> > :   -   **data** -- The data to write to the stream.
> >     -   **slot** -- The stream slot.
> >
> **load\_model(model, force\_inline=False, embedded\_schemas={},
> dry\_run=False)**
>
> > Load a model into this engine.
> >
> > Parameters
> >
> > :   -   **model** -- A Model object.
> >     -   **force\_inline** -- If True, force all attachments to load
> >         inline. If False, attachments may be loaded by reference.
> >     -   **embedded\_schemas** -- A dict of schemas to send with the
> >         request to stop the Engine from contacting Model Manage when
> >         resolving schemas.
> >     -   **dry\_run** -- If True, do not actually load the model,
> >         check for errors only.
> >
> **output(slot)**
>
> > Reads data from the REST stream attached to the slot.
> >
> > Parameters
> >
> > :   **slot** -- The stream slot.
> >
> **pause()**
>
> > Pauses the engine. The result depends on the current state of the
> > engine. A running engine changes its state to PAUSED. An
> > initializing engine will pause upon startup. In all other states the
> > operation is ignored.
>
> `policy`
>
> > Set/get the import policy.
> >
> > &gt;&gt;&gt; engine = connect.lookup('engine-1') &gt;&gt;&gt;
> > engine.policy.set('import', 'python', text) &gt;&gt;&gt; print
> > engine.policy.get('import', 'python')
>
> **reset()**
>
> > Resets the engine. A loaded model is unloaded. All open streams are
> > closed. The engine changes its state to INIT.
>
> **scale(factor)**
>
> > Changes the number of running model instances.
>
> `state`
>
> > The current state of the engine.
> >
> > Returns
> >
> > :   'INIT', 'RUNNING', 'PAUSED', 'FINISHING', or 'FINISHED'.
> >
> `tapping_points`
>
> > A list of tapping points supported by the instance.
> >
> > &gt;&gt;&gt; mm.tapping\_points \['sys.memory',... \]
>
> **unpause()**
>
> > Unpauses the engine.
>
> **verify\_data(sid, rec)**
>
> > Verify schema against a prepared schema.
> >
> > Parameters
> >
> > :   -   **sid**
> >         ([int](https://docs.python.org/2/library/functions.html#int))
> >         -- The schema id.
> >     -   **rec**
> >         ([str](https://docs.python.org/2/library/functions.html#str))
> >         -- The data record to verify.
> >
Exceptions
==========

**class fastscore.FastScoreError(message, caused\_by=None)**

> A FastScore exception.
>
> SDK functions throw only FastScoreError exceptions. An SDK function
> either succeeds or throws an exception. The return value of a SDK
> function is always valid.

Pneumo
======

**class fastscore.PneumoSock(proxy\_prefix, timeout=None, src=None,
type=None,**kwargs)\*\*

> The Pneumo websocket.
>
> &gt;&gt;&gt; pneumo = connect.pneumo() &gt;&gt;&gt; pneumo.recv()
> LogMsg(src=..., timestamp=..., ...)
>
> **close()**
>
> > Close the Pneumo socket.
>
> **recv()**
>
> > Receives the next Pneumo message.

Models
======

**class fastscore.Model(name, mtype='python', source=None,
model\_manage=None)**

> Represents an analytic model. A model can be created directly:
>
> &gt;&gt;&gt; model = fastscore.Model('model-1') &gt;&gt;&gt;
> model.mtype = 'python' &gt;&gt;&gt; model.source = '...'
>
> Or, retrieved from a Model Manage instance:
>
> &gt;&gt;&gt; mm = connect.lookup('model-manage') &gt;&gt;&gt; model =
> mm.models\['model-1'\]
>
> A directly-created model must be saved to make attachment and snapshot
> manipulation functions available:
>
> &gt;&gt;&gt; mm = connect.lookup('model-manage') &gt;&gt;&gt;
> model.update(mm) &gt;&gt;&gt; model.attachments.names() \[\]
>
> `attachments`
>
> > A collection of model attachments. See `Attachment`.
>
> **deploy(engine)**
>
> > Deploy this model to an engine.
> >
> > Parameters
> >
> > :   **engine** -- The Engine instance to use.
> >
> `mtype`
>
> > A model type:
> >
> > -   **pfa-json**: a PFA model in JSON format.
> > -   **pfa-yaml**: a PFA model in YAML format.
> > -   **pfa-pretty**: a PrettyPFA model.
> > -   **h2o-java**: an H20 model.
> > -   **python**: a Python model.
> > -   **python3**: a Python 3 model.
> > -   **R**: an R model.
> > -   **java**: a Java model.
> > -   **c**: a C model.
> > -   **octave**: an Octave model.
> > -   **sas**: a SAS model.
>
> `name`
>
> > A model name, e.g. 'model-1'.
>
> `source`
>
> > The source code of the model.

Attachments
===========

**class fastscore.model.Attachment(name, atype=None, datafile=None,
datasize=None, model=None)**

> Represents a model attachment. An attachment can be created directly
> but it must (ultimately) associated with the model:
>
> &gt;&gt;&gt; att = fastscore.Attachment('att-1',
> datafile='/tmp/att1.zip') &gt;&gt;&gt; model = mm.models\['model-1'\]
> &gt;&gt;&gt; att.upload(model)
>
> Parameters
>
> :   -   **atype** -- An attachment type. Guessed from the data file
>         name if omitted.
>     -   **datafile** -- The data file.
>     -   **model** -- The model instance.
>
> `atype`
>
> > An attachment type.
> >
> > -   **zip** A ZIP archive.
> > -   **tgz** A gzipped tarball.
>
> `datafile`
>
> > A name of the file that contains the attachment data. The attachment
> > is downloaded when this property is first accessed.
>
> `datasize`
>
> > The size of the attachment. Checking the attachment size does NOT
> > trigger the download.
>
> `name`
>
> > An attachment name.
>
> **upload(model=None)**
>
> > Adds the attachment to the model.
> >
> > Parameters
> >
> > :   **model** -- The model instance. Can be None if the model
> >     instance has been provided when the attachemnet was created.
> >
Snapshots
=========

**class fastscore.model.Snapshot(snapid, created\_on, stype, size,
model)**

> Represents a snapshot of a model state. Do not create directly. Use
> the model's snapshots collection:
>
> &gt;&gt;&gt; model = mm.models\['model-1'\] &gt;&gt;&gt;
> model.snapshots.browse(count=1) \[{'id': 'yu647a',...}\] &gt;&gt;&gt;
> snap = model.snapshots\['yu'\] \# prefix is enough
>
> `created_on`
>
> > A date the snapshot has been taken.
>
> `id`
>
> > A snapshot id.
>
> **restore(engine)**
>
> > Restore the model state using the snapshot.
> >
> > &gt;&gt;&gt; snap = model.snapshots\['yu'\] \# prefix is enough
> > &gt;&gt;&gt; snap.restore(engine)
>
> `size`
>
> > A size of the snapshot in bytes.

Streams
=======

**class fastscore.Stream(name, desc=None, model\_manage=None)**

> A FastScore stream. A stream can be created directly:
>
> &gt;&gt;&gt; stream = Stream('stream-1') &gt;&gt;&gt; stream.desc =
> {'Transport':...}
>
> Or, retrieved from a Model Manage instance:
>
> &gt;&gt;&gt; mm = connect.lookup('model-manage') &gt;&gt;&gt; stream =
> mm.streams\['stream-1'\]
>
> **attach(engine, slot, dry\_run=False)**
>
> > Attach the stream to the engine.
> >
> > Parameters
> >
> > :   **slot** -- The stream slot.
> >
> `desc`
>
> > A stream descriptor (a dict).
> >
> > &gt;&gt;&gt; stream = mm.streams\['stream-1'\] &gt;&gt;&gt;
> > stream.desc {'Transport': {'Type': 'discard'}, 'Encoding': 'json'}
>
> `name`
>
> > A stream name.
>
> **rate(engine)**
>
> > Measures the stream throughput outside of a data pipeline.
> >
> > Parameters
> >
> > :   **engine** -- An Engine instance to use.
> >
> **sample(engine, n=None)**
>
> > Retrieves a few sample records from the stream.
> >
> > Parameters
> >
> > :   -   **engine** -- An Engine instance to use.
> >     -   **n** -- A number of records to retrieve (default: 10).
> >
> > Returns
> >
> > :   An array of base64-encoded records.
> >
> **update(model\_manage=None)**
>
> > Saves the stream to Model Manage.
> >
> > Parameters
> >
> > :   **model\_manage** -- The Model Manage instance to use. If None,
> >     the Model Manage instance must have been provided when then
> >     stream was created.
> >
Schemata
========

**class fastscore.Schema(name, source=None, model\_manage=None)**

> An Avro schema. It can be created direct
>
> `name`
>
> > A schema name.
>
> `source`
>
> > A schema source, e.g. {'type': 'array', 'items': 'int'}.
>
> **update(model\_manage=None)**
>
> > Saves the schema to Model Manage.
> >
> > Parameters
> >
> > :   **model\_manage** -- The Model Manage instance to use. If None,
> >     the Model Manage instance must have been provided when then
> >     schema was created.
> >
> **verify(engine)**
>
> > Asks the engine the check the schema.
> >
> > Returns
> >
> > :   id of the loaded schema. The identifier can be used to validate
> >
> > data records:
> >
> > &gt;&gt;&gt; engine = connect.lookup('engine') &gt;&gt;&gt; sid =
> > schema.verify(engine) &gt;&gt;&gt; engine.validate\_data(sid, rec)

Sensors
=======

**class fastscore.Sensor(name, desc=None, model\_manage=None)**

> Represents a FastScore sensor. A sensor can be created directly:
>
> &gt;&gt;&gt; sensor = fastscore.Sensor('sensor-1') &gt;&gt;&gt;
> sensor.desc = {'tap': 'manifold.input.records.size',...}
>
> Or, retreieved from Model Manage:
>
> &gt;&gt;&gt; mm = connect.lookup('model-manage') &gt;&gt;&gt;
> mm.sensors\['sensor-1'\] &gt;&gt;&gt; mm.desc {...}
>
> `desc`
>
> > A sensor descriptor (a dict).
>
> **install(target)**
>
> > Install/attach the sensor.
> >
> > Parameters
> >
> > :   **target** -- The instance to attach the sensor to.
> >
> `name`
>
> > A sensor name.
>
> **update(model\_manage=None)**
>
> > Saves the sensor to Model Manage.
> >
> > Parameters
> >
> > :   **model\_manage** -- The Model Manage instance to use. If None,
> >     the Model Manage instance must have been provided when then
> >     sensor was created.
> >
