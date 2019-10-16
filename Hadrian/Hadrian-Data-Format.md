## Hadrian's internal data representation

PFA by itself does not define a data representation, only a type system (Avro's type system). Hadrian, as a software library rather than an application, does not require data to be serialized in a particular format. Three input formats are defined so far (Avro, JSON, and CSV), but applications using the library are encouraged to use their own input formats: anything that is appropriate for the workflow that Hadrian is to be embedded in.

However, data has to be represented in some form for processing by PFA functions. This is the data format used internally by Hadrian.

| Avro type | Hadrian's internal format |
|:----------|:--------------------------|
| null | `null` Java [Object](http://docs.oracle.com/javase/7/docs/api/java/lang/Object.html) ([`AnyRef`](http://www.scala-lang.org/api/current/#scala.AnyRef)) |
| boolean | [`java.lang.Boolean`](http://docs.oracle.com/javase/7/docs/api/java/lang/Boolean.html) |
| int | [`java.lang.Integer`](http://docs.oracle.com/javase/7/docs/api/java/lang/Integer.html) |
| long | [`java.lang.Long`](http://docs.oracle.com/javase/7/docs/api/java/lang/Long.html) |
| float | [`java.lang.Float`](http://docs.oracle.com/javase/7/docs/api/java/lang/Float.html) |
| double | [`java.lang.Double`](http://docs.oracle.com/javase/7/docs/api/java/lang/Double.html) |
| string | Java [`String`](http://docs.oracle.com/javase/7/docs/api/java/lang/String.html) |
| bytes | Java array of bytes |
| array | [`com.opendatagroup.hadrian.data.PFAArray[T]`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.data.PFAArray) |
| map | [`com.opendatagroup.hadrian.data.PFAMap[T]`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.data.PFAMap) |
| record | subclass of [`com.opendatagroup.hadrian.data.PFARecord`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.data.PFAMap) |
| fixed | subclass of [`com.opendatagroup.hadrian.data.PFAFixed`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.data.PFAFixed) |
| enum | subclass of [`com.opendatagroup.hadrian.data.PFAEnumSymbols`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.data.PFAEnumSymbols) |
| union | Java Object (`AnyRef`) |

Input to a scoring engine's `action` method must be of this form, and output from that method will be of this form. This is not the format that the Avro library produces when you deserialize an Avro file (Hadrian uses a custom [`org.apache.avro.specific.SpecificData`](https://avro.apache.org/docs/1.7.7/api/java/org/apache/avro/specific/SpecificData.html) called [`com.opendatagroup.hadrian.data.PFASpecificData`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.data.PFASpecificData)). However, it is a format that can be passed directly to the Avro library to serialize an Avro file.

### Specialized subclasses

Three of the above, `PFARecord`, `PFAFixed`, and `PFAEnumSymbols` are compiled specifically for each PFA engine class. (If you run the `fromJson` method of [`com.opendatagroup.hadrian.jvmcompiler.PFAEngine`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.jvmcompiler.PFAEngine$) with `multiplicity > 1`, all of the scoring engines returned share the same class; if you run it multiple times, the scoring engines belong to different classes.) You must use the right subclass. Since these subclasses are compiled at runtime, they must be accessed through a special [`java.lang.ClassLoader`](http://docs.oracle.com/javase/7/docs/api/java/lang/ClassLoader.html).

Here is an example of creating a `PFARecord` for a given `engine` (of class [`com.opendatagroup.hadrian.jvmcompiler.PFAEngine`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.jvmcompiler.PFAEngine)) and a `recordType` (of class [`com.opendatagroup.hadrian.datatype.AvroRecord`](http://modelop.github.io//hadrian/hadrian-0.8.1/index.html#com.opendatagroup.hadrian.datatype.AvroRecord)). Assume that the fields of this record have already been converted into the appropriate types and are stored, in field order, in an array of Objects called `fieldData`.

```scala
val recordTypeName = recordType.fullName
val classLoader = engine.classLoader
val subclass = classLoader.loadClass(recordTypeName)
val constructor = subclass.getConstructor(classOf[Array[AnyRef]])
constructor.newInstance(fieldData)
```

Only the last line needs to be executed at runtime; the rest can be saved from an initialization phase. In fact, calling `constructor.setAccessible(true)` can speed up `constructor.newInstance(fieldData)` by skipping access checks at runtime.

Here is an example of creating a `PFAFixed` from a given `engine` (of class `PFAEngine`) and a `fixedType` (of class [`com.opendatagroup.hadrian.datatype.AvroFixed`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.datatype.AvroFixed)). Assume that the data is stored as an array of byte primitives called `bytesData`.

```scala
val fixedTypeName = fixedType.fullName
val classLoader = engine.classLoader
val subclass = classLoader.loadClass(fixedTypeName)
val constructor = subclass.getConstructor(classOf[Array[Byte]])
constructor.newInstance(bytesData)
```

Here is an example of creating a `PFAEnumSymbol` from a given `engine` (of class `PFAEngine`) and an `enumType` (of class [`com.opendatagroup.hadrian.datatype.AvroEnum`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.datatype.AvroEnum)). Assume that the data is given as a string called `symbolName`.

```scala
val enumTypeName = enumType.fullName
val classLoader = engine.classLoader
val subclass = classLoader.loadClass(enumTypeName)
val constructor = subclass.getConstructor(classOf[org.apache.avro.Schema],
                                          classOf[String])
constructor.newInstance(enumType.schema, symbolName)
```

### Container types: array and map

`PFAArray[T]` and `PFAMap[T]` are templated classes that satisfy Java's `java.util.List[T]` and `java.util.Map[String, T]` interfaces, though most methods raise [`UnsupportedOperationException`](http://docs.oracle.com/javase/7/docs/api/java/lang/UnsupportedOperationException.html). They are backed by Scala collections, [`Vector[T]`](http://www.scala-lang.org/api/current/#scala.collection.immutable.Vector) and [`Map[String, T]`](http://www.scala-lang.org/api/current/#scala.collection.immutable.Map). The normal way to create a `PFAArray[T]` or `PFAMap[T]` is with a given vector `v` or map `m`:

```scala
PFAArray.fromVector(v)
PFAMap.fromMap(m)
```

However, they can also be constructed using in-place operations using the Java interfaces (`sizeHint` is an integer hint for preallocation and `arrayType`, `mapType` are instances of [`com.opendatagroup.hadrian.datatype.AvroArray`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.datatype.AvroArray) and [`com.opendatagroup.hadrian.datatype.AvroMap`](http://modelop.github.io//hadrian/hadrian-0.8.1/index.html#com.opendatagroup.hadrian.datatype.AvroMap)):

```scala
val array = PFAArray.empty(sizeHint, arrayType.schema)
array.add(value1)
array.add(value2)

val map = PFAMap.empty(sizeHint, mapType.schema)
map.put(key1, value1)
map.put(key2, value2)
```

To get a usable collection, call the `array.toVector` or `map.toMap` methods. In the building phase, `PFAArray[T]` and `PFAMap[T]` are backed by [`scala.collection.mutable.Builder[T, Vector[T]]`](http://www.scala-lang.org/api/current/#scala.collection.mutable.Builder) and [`scala.collection.mutable.Builder[(String, T), Map[String, T]]`](http://www.scala-lang.org/api/current/#scala.collection.mutable.Builder) for performance when progressively accumulating data. Once `array.toVector` or `map.toMap` has been called, they are backed by collections. The `array.toVector` and `map.toMap` operations should be considered rapid because they're already lazy-cached.

Note that `PFAArray[T]` takes primitive types `T` for booleans (`Boolean`), integers (`Int`), longs (`Long`), floats (`Float`), and doubles (`Double`), but `PFAMap[T]` takes boxed primitive types `T` for booleans (`java.lang.Boolean`), integers (`java.lang.Integer`), longs (`java.lang.Long`), floats (`java.lang.Float`), and doubles (`java.lang.Double`). These quirks were forced by the way that the Avro library loads data.

Additionally, `PFAArray[T]` has a mutable `metadata` field (of type `Map[String, Any]`) for optimizations. Some data mining models run faster if their input data are organized differently from a flat list. For instance, [`model.neighbor.nearestK`](http://dmg.org/pfa/docs/library/#fcn:model.neighbor.nearestK) can be optimized by storing the training dataset as a KD-tree, rather than a list. With the `lib.model.neighbor.nearestK.kdtree` option set to `true`, Hadrian will build the KD-tree and attach it to the `PFAArray[T]` as `metadata`. On subsequent calls, `model.neighbor.nearestK` will search the tree, rather than the array, replacing an O(n) algorithm with an O(log(n)) one. This is safe from inconsistencies because arrays are immutable in PFA.

### Example translators

Hadrian has a few built-in translator routines, which translate data from a form appropriate for one engine class to another engine class ([`com.opendatagroup.hadrian.data.PFADataTranslator`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.data.PFADataTranslator)), from data deserialized by the Avro library to data appropriate for an engine class ([`com.opendatagroup.hadrian.data.AvroDataTranslator`](http://modelop.github.io//hadrian/hadrian-0.8.1/index.html#com.opendatagroup.hadrian.data.AvroDataTranslator)), and to and from Scala code ([`com.opendatagroup.hadrian.data.ScalaDataTranslator`](http://modelop.github.io//hadrian/hadrian-0.8.1/index.html#com.opendatagroup.hadrian.data.ScalaDataTranslator)). All three minimize the effort needed to translate at runtime by saving constructors and skipping unnecessary translations (for example, from `java.lang.Integer` to `java.lang.Integer` or arrays of these, etc.).

Antinous also has translator routines, which translate from PFA to Jython ([`com.opendatagroup.antinous.translate.PFAToJythonDataTranslator`](https://github.com/opendatagroup/hadrian/blob/0.8.3/antinous/src/main/scala/com/opendatagroup/antinous/translate.scala#L74)), the reverse ([`com.opendatagroup.antinous.translate.JythonToPFADataTranslator`](https://github.com/opendatagroup/hadrian/blob/0.8.1/antinous/src/main/scala/com/opendatagroup/antinous/translate.scala#L407)), and data deserialized by the Avro library to Jython ([`com.opendatagroup.antinous.translate.AvroToJythonDataTranslator`](https://github.com/opendatagroup/hadrian/blob/0.8.1/antinous/src/main/scala/com/opendatagroup/antinous/translate.scala#L244)). They follow the same pattern as Hadrian's translators, but additionally have to deal with the problem of grafting the Avro type system onto Python's built-in type system.

## Built-in serialization methods

The Hadrian library provides a few data serialization/deserialization methods out-of-the-box. Some are specific to a given `PFAEngine` class, others are generic, deserializing data that could be translated with `PFADataTranslator` and then used as input to `action` or for serializing any data directly.

The specific methods are all member functions of the `PFAEngine` class. The results of each input method can be directly passed to `PFAEngine.action` and the output of `PFAEngine.action` (or `emit`) can be directly passed to each output method.

   * `avroInputIterator` reads a raw Avro file as a [`java.io.InputStream`](http://docs.oracle.com/javase/7/docs/api/java/io/InputStream.html) and yields data as a [`java.util.Iterator`](http://docs.oracle.com/javase/7/docs/api/java/util/Iterator.html).
   * `jsonInputIterator` reads a file in which each line is a complete JSON document representing one input datum, again as a `java.io.InputStream`, producing a `java.util.Iterator`. If the input is a [`scala.collection.Iterator[String]`](http://www.scala-lang.org/api/current/#scala.collection.Iterator), then the output is a `scala.collection.Iterator[X]`.
   * `csvInputIterator` uses [Apache Commons CSV](https://commons.apache.org/proper/commons-csv/) to read a CSV file as record data. The engine's input type must be a record containing only primitives, to conform with CSV's limitations.
   * `jsonInput` loads one complete JSON document representing one datum. This function must be called repeatedly, since it does not operate on streams or iterators, and it is less efficient than the iterator version.
   * `avroOutputDataStream` creates an Avro data sink on a given [`java.io.OutputStream`](http://docs.oracle.com/javase/7/docs/api/java/io/OutputStream.html) that has `append` and `close` methods for writing data.
   * `jsonOutputDataStream` does the same for JSON, printing one complete JSON document per line.
   * `csvOutputDataStream` does the same for CSV, assuming that the engine's output type is a record containing only primitives.
   * `fromPFAData` is a specialized `PFADataTranslator` attached to the `PFAEngine`. Use this to convert data from one scoring engine's output to another's input (i.e. chaining models).
   * `fromGenericAvroData` is a specialized `AvroDataTranslator` attached to the `PFAEngine`. Use this to convert data deserialized by the Avro library into data that can be sent to `action`.

The following functions are generic, not associated with any PFA engine class. To use them for input, be sure to run the data through the specific PFA engine's `PFAEngine.fromPFAData` first. Any can be used for output. They are all in the [`com.opendatagroup.hadrian.data`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.data.package) package.

   * `fromJson` converts one datum from a complete JSON document.
   * `fromAvro` converts one datum from Avro (as part of a stream or an RPC call, not an Avro file with header).
   * `toJson` converts one datum to a complete JSON document.
   * `toAvro` converts one datum to Avro (again, as part of a stream or an RPC call, not an Avro file with header).
   * `avroInputIterator` streams an Avro file like the `PFAEngine` method with the same name, but produces generic data that must be translated with `PFAEngine.fromPFAData`.
   * `jsonInputIterator` streams a file of one-JSON-per-line like the `PFAEngine` method with the same name, but produces generic data that must be translated with `PFAEngine.fromPFAData`.
   * `csvInputIterator` streams a CSV file like the `PFAEngine` method with the same name, but produces generic data that must be translated with `PFAEngine.fromPFAData`.
   * `avroOutputDataStream` streams an Avro file exactly like the `PFAEngine` method with the same name.
   * `jsonOutputDataStream` streams a one-JSON-per-line file exactly like the `PFAEngine` method with the same name.
   * `csvOutputDataStream` streams a CSV file exactly like the `PFAEngine` method with the same name.
