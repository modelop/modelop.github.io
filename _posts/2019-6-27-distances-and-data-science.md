---
layout: post
title: "Distances and Data Science"
categories: [data science]
tags: [python, metric learning]
author: Sam Shideler
mathjax: true
---

We're all aware of what 'distance' means in real-life scenarios, and how our notion
of what 'distance' means can change with context. If we're talking about the distance
from the ODG office to one of our favorite lunch spots, we probably mean the distance
we walk when traversing Chicago's grid of city blocks from the office to the restaurant,
not the 'direct line' distance on the Earth's surface. Similarly, if we're talking
about the distance from Chicago to St. Louis, the distance we're talking about probably
depends on whether we're driving (taking the shortest path via available roads) or flying
(which is usually much closer to the 'straight line' path on the Earth's surface
than driving is). In this post, we explore a more rigorous construction of distance
and its applications to data science.


## What is a metric?

Most people have also encountered distances in their math classes - things like
computing the distance between two points in the Cartesian plane with the familiar
formula $\sqrt{(x_1-x_2)^2 + (y_1-y_2)^2}$.

As mathematicians love to do, we can attempt to broadly generalize what we mean
by 'distance' while still retaining the key properties that make such a measurement
useful. Really, what 'distances' are doing in most scenarios is giving some
quantitative indication of how 'close' two things are, where what we mean by
'close' depends on the situation. For a slightly less obvious example of distances,
we can talk about distances between people in a social network. We can define a
distance as follows: everyone I have personally met has distance 1 from me,
everyone that one of my acquaintances has met that I haven't has distance 2 from
me, and so on. Then the 'distance' between two people in this scenario - the
shortest path of acquaintances connecting them - can be thought of as a measurement
of how similar their social networks are. This is a special case of something
called a 'graph distance', and people study distances like this on sites like
Facebook all the time.

As mentioned above, mathematicians have singled out a few properties that give a
useful and meaningful notion of distance. Given a function $d(x,y)$, what
properties would we like it to satisfy in order to be called a distance?

First, we want the distance from something to itself to be $0$, and the distance
from something to a different something to be strictly larger than $0$. Said
differently, we want our distance function to be able to detect equality:
$d(x,y)=0$ should imply that $x=y$.

Secondly, we want the distance between $x$ and $y$ to not depend on the order:
$d(x,y)$ should equal $d(y,x)$. Note that this can actually fail in some real
life examples (for instance, one way streets might mean this is false for the
driving distance between two places), but it is desirable for theoretical
applications.

Finally, we don't want there to be 'shortcuts': the distance from $x$ to $y$
should truly be the shortest distance from $x$ to $y$ - I can't get a shorter
distance by first going to some intermediate $z$. Mathematically, we can write
this as $d(x,y) \leq d(x,z)+d(z,y)$ for all $z$. This is known as the triangle
inequality.

Any function satisfying these 3 properties is called a *metric* and can be used
as a meaningful notion of distance.


### Metrics and Data Science

This is all well and good, but why should a data scientist care about metrics?
The answer is that distance computations are at the heart of a number of common
important algorithms from machine learning, and understanding what's going on
behind the scenes can lead to better insights and increased accuracy.

Broadly speaking, when we're attacking (for instance) a classification problem,
the heart of what we're actually trying to do is to find a way to compare a new,
unclassified data point to previously seen data points. We then use that
additional information to try and classify our new point in a way that attempts
to be as consistent as possible with the known data. In order to do this, we
need some sort of additional numerical information about comparisons between
data points. Metrics are exactly the tool that allow us to translate notions of
'similarity' into a useable mathematical form.

Let's quickly run through some specific examples.

- K-Nearest Neighbors: This is probably the simplest and most well-known of all metric-based ML algorithms. The idea is clear - given a new data point, we want to classify it based on the closest nearby known data points. What we mean by 'closest' obviously depends on the choice of a metric. There is a lot of work that has been done on choosing the best metric for a given problem - more on that later.

- Support Vector Machines - This algorithm attempts to find a maximally separating hyperplane between classes. Again, 'maximally separating' here depends on the choice of a metric. With techniques like kernelization, you are implicitly working with the points in some higher dimensional space (along with its Euclidean metric!).

- Clustering - Many clustering objective functions come from trying to minimize the sum of distances between cluster centers and points in the cluster in various metrics. The clusters you get will depend on the choice of metric. Common choices are the standard Euclidean distance and the 'taxicab' or $\ell_1$ distance - named because it works like distances in a city with a grid layout like Chicago (it's also commonly called the Manhattan distance for the same reason).


### Choosing the Right Metric for the Job

So now we've established that metrics appear quite often and that the choice of
metric can affect the efficacy of a model. The obvious question is then: how do
I choose the right metric for the job?

One potential direction this question might lead is dimensionality reduction. If
my data lies in some very high dimensional space, doing computations like finding
the nearest neighbor to a given data point can be quite computationally expensive.
The idea of dimensionality reduction is to (hopefully!) drastically lower the
number of necessary dimensions in order to speed this process up. But this is
useless unless there's some guarantee that pairwise distances don't become too
distorted - otherwise I'm no longer able to compute the correct nearest neighbor.
The Johnson-Lindenstrauss lemma is an example of the kind of theorem that one
might hope to prove in the direction of showing that such a process is possible.
At a high level, it says that if I take random projections of my data to roughly
(log of the number of data points) dimensions, distances are preserved (modulo
some factors) with high probability. So most of the time, just taking random
projections allows me to severely reduce the dimensionality of my data without
losing too much information about the pairwise distances!

But perhaps I want to leave my data unchanged and just change the metric on the
ambient space to better serve my classification task. This is broadly the subject
of a field called 'metric learning'. The general goal is often to learn a special
kind of metric called a Mahalanobis distance - one of the form
$d(x,y) = \sqrt{(x-y)^\top M (x-y)}$ where $M$ is a positive semidefinite matrix -
that improves the classification results of algorithms like K-Nearest Neighbors.
The idea is often to translate the condition 'points of the same class are close,
whereas points of different classes are far apart' into an optimization problem,
and then optimize!

This is just scratching the surface of the ways metrics are studied and applied
to machine learning and data science problems. I learned a lot about
Johnson-Lindenstrauss and high dimensional geometry in data science from Blum,
Hopcroft and Kannan's book [Foundations of Data Science](http://www.cs.cornell.edu/jeh/book%20no%20so;utions%20March%202019.pdf)
(which is free online!). For metric learning, Kulis' [Metric Learning: A Survey](http://people.bu.edu/bkulis/pubs/ftml_metric_learning.pdf) is a nice introduction.
