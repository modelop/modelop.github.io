## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.5.14; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `titus.prettypfa`:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import titus.prettypfa as prettypfa

## Realistic example

The [simple example](PrettyPFA-Simple-Example) applies a mathematical formula to user-supplied parameters, but PFA was designed for data processing.  The example in this section is more realistic.

To begin, download the [Exoplanets dataset](/public/data/exoplanets.avro), which we use for examples.  It can be read with [Avro](https://pypi.python.org/pypi/avro) or [fastavro](https://pypi.python.org/pypi/avro).

    >>> from avro.datafile import DataFileReader
    >>> from avro.io import DatumReader
    >>> exoplanetsIter = DataFileReader(open("exoplanets.avro"), DatumReader())
    >>> exoplanets = list(exoplanetsIter)
    >>> print len(exoplanets)
    1103

or

    >>> import fastavro
    >>> exoplanetsIter = fastavro.reader(open("exoplanets.avro"))
    >>> exoplanets = list(exoplanetsIter)
    >>> print len(exoplanets)
    1103

Next, build a scoring engine directly from PrettyPFA.  This engine finds the coldest planet orbiting each     star in the exoplanets dataset, with contingencies for missing data.

    >>> engine, = prettypfa.engine('''
    types:
      Planet = record(
        name:          string,                // Name of the planet
        detection:                            // Discovery technique
          enum([astrometry, imaging, microlensing, pulsar,
                radial_velocity, transit, ttv, OTHER]),
        discovered:    string,                // Year of discovery
        updated:       string,                // Date of last update
        mass:          union(double, null),   // Mass over Jupiter's mass
        radius:        union(double, null),   // Radius over Jupiter's
        period:        union(double, null),   // Planet year (Earth days)
        max_distance:  union(double, null),   // Distance from star (AU)
        eccentricity:  union(double, null),   // (0 = circle, 1 = escapes)
        temperature:   union(double, null),   // Temperature (Kelvin)
        temp_measured: union(boolean, null),  // True if the measured
        molecules:     array(string)          // Molecules observed
      );

      Star = record(
        name:    string,                      // Name of the star
        ra:      union(double, null),         // Right ascension (degrees)
        dec:     union(double, null),         // Declination (degrees)
        mag:     union(double, null),         // Magnitude (unitless)
        dist:    union(double, null),         // Distance away (parsecs)
        mass:    union(double, null),         // Mass over Sun's mass
        radius:  union(double, null),         // Radius over Sun's radius
        age:     union(double, null),         // Age (billions of years)
        temp:    union(double, null),         // Temperature (Kelvin)
        type:    union(string, null),         // Spectral type
        planets: array(Planet)                // Orbiting planets
      );

      PlanetWithTemp = record(planet: Planet, temp: double)

    input: Star
    output: Planet

    method: emit
    action:
      var star = input;  // name the input for convenience

      // build up a list of planets with temperature estimates
      var pt = json(array(PlanetWithTemp), []);
      foreach (planet: star.planets, seq: true) {
        var temp =
          ifnotnull(t: planet.temperature)
            // if a planet's temperature is already defined, use it
            t
          else {
            // otherwise, estimate it from the star
            ifnotnull(t: star.temp,
                      r: star.radius,
                      d: planet.max_distance) {
              var r_in_km = r * 695800.0;
              var d_in_km = d * 149600000.0;
              t / (d/r)**2
            }
            else
              // third case: not enough data to make any estimate
              null
          };
        // if the above resulted in an estimate, add it to the list
        ifnotnull(t: temp) {
          pt = a.append(pt, new(PlanetWithTemp,
                                planet: planet,
                                temp: t))
        }
      };

      // if the list is not empty...
      if (a.len(pt) > 0) {
        // find the coldest planet
        var coldest =
          a.minLT(pt, fcn(x: PlanetWithTemp,
                          y: PlanetWithTemp -> boolean) {
            x.temp < y.temp
          });

        // and emit it as the result of this scoring engine
        emit(coldest.planet)
      }
    ''')

Now run the scoring engine on the exoplanets dataset.

    >>> def emit(x):
    ...     print x
    ...
    >>> engine.emit = emit
    >>>
    >>> for star in exoplanets:
    ...     engine.action(star)
    ...
    {u'discovered': '2014', u'updated': '2014-03-06', u'name': 'Kepler-207 d', u'temp_measured': True, u'period': 5.868075, u'detection': u'transit', u'eccentricity': None, u'radius': 0.295, u'molecules': [], u'max_distance': 0.068, u'mass': None, u'temperature': None}
    {u'discovered': '2004', u'updated': '2012-05-25', u'name': 'HD 89307 b', u'temp_measured': True, u'period': 2199.0, u'detection': u'radial_velocity', u'eccentricity': 0.25, u'radius': None, u'molecules': [], u'max_distance': 3.34, u'mass': 2.0, u'temperature': None}
    ...
