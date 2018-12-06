---
layout: post
title: "Making Unstructured Text Data Usable with Semantic Parsing"
categories: [data science]
tags: [NLP, AI, robots,]
author: Alex Schumacher
---

If you’ve seen any technology publication in the last few years, you’d
know this one incontrovertible truth: the robots are coming, and there’s
no stopping them. Even if they’re not literal robots, AI is everywhere,
and it’s probably sitting in your living room already, taking the form
of a Google Assistant or Amazon Echo.

If you are one of the 50 million people who has such a device, you might
consider running the following experiment. Ask it the following
questions, posed by Steven Pinker in his 1994 book *The Language
Instinct*:

> The main lesson of thirty-five years of AI research is that the hard
> problems are easy and the easy problems are hard...if you want to
> stump an artificial intelligence system, ask it questions like: ’Which
> is bigger, Chicago or a breadbox? Do zebras wear underwear? Is the
> floor likely to rise up and bite you? If Susan goes to the store, does
> her head go with her?’

My Alexa told me she didn’t know for three of them, and read me the
summary portion of the Wikipedia page on underwear for the other. Pinker
lays out the heart of the problem:

> Understanding a sentence is one of these hard easy problems. To
> interact with computers we still have to learn their languages; they
> are not smart enough to learn ours. In fact, it is all too easy to
> give computers more credit at understanding than they deserve.

Although Alexa can’t yet tell us whether zebras wear underwear, natural
language understanding techniques have actually come quite a long way
since 1994. Computational linguists and data scientists can make large
amounts of unstructured text data into machine-readable information,
which can then be used to answer questions about the apparel commonly
worn by equines.

Turning text data into usable information requires a technique called
*semantic parsing*. In semantic parsing, a sentence is analyzed and
broken into its component parts which are then labelled with the
relations between them. Then, those relations are interpreted and fed
into a database. For example, take a sentence like \`\`John gave a duck
to Mary", which has been labelled with the parts of speech for each
word.
```
John gave a duck to Mary.\
NOUN VERB ART NOUN PREP NOUN\
```
At this point, there are two possibilities. One is to settle for a
**shallow semantic parse**, and the other is to strive for a **logical
semantic parse** (also called a **deep** semantic parse). A shallow
semantic parse consists of using the words and labels to infer the
**semantic roles** of the nouns in a sentence. You can think of a
semantic role as what \`\`job“ a noun is doing in the meaning described
by the sentence. In the example, *John* is the \`\`giver”, *Mary* is the
\`\`recipient“ and the *duck* is the \`\`givee”. What semantic roles
belong with what kinds of verbs is highly idiosyncractic, so shallow
semantic parsing based on semantic role labelling often require looking
up the roles for the verb in a resource like FrameNet. Linguists have
come up with annotation schemes which capturing the best generalizations
across verbs, so the labelling would look like below.
```
John gave a duck to Mary.\
Donor Theme Recipient\
```
The semantic parse for this sentence could then be recorded in a
database as the following attribute-value pairs:

    {
    "Donor":"John"
    "Theme":"duck"
    "Recipient":"Mary"
    "event":"give"
    }

In this format, the formerly unstructured text gains structure which can
be readily used in a wide variety of uses; from question-answering
systems, to dialog systems, to automated construction of ontologies.

For certain applications, like turning natural language into
instructions for robots, a logical semantic parse is often necessary.
The goal of a logical semantic parse is to convert a natural language
sentence into its equivalent in a logical formalism such as first-order
predicate logic or an ontology format like RDF.

-   **First-order logic:** give(John, duck, Mary)

-   **RDF:**

<!-- -->

    <rdf:Description rdf:about="arg:John">
    <ns1:give rdf:resource="arg:duck"/>
    <ns1:give_to rdf:resource="arg:Mary"/>      
    </rdf:Description>

The advantage that logical semantic parsing has over shallow semantic
parsing is that it is a more complete and explicit representation of the
text, but it comes at the cost of much greater complexity and the need
for (possibly lots and lots of) labelled data. There are several ways of
creating such a parse; one way is to begin with a syntactic parse of the
sentence, and then identifying its principle parts - the subject,
predicate, and objects. Below is a dependency graph of the example
sentence created using the open-source Python library spaCy:

![image](/assets/posts/images/dgraph.png)

The dependency graph identifies the principle parts of a logical or RDF
representation by the dependency labels (*ROOT*, *nsubj*, *dobj*,
*dative*). The relations can then straightforwardly be translated into
an RDF or first-order logical representation.

If a shallow semantic parse is all that is needed, it is usually the
better option as it is simpler and often less error prone. Shallow
semantic parsing avoids facing one of the biggest problems in natural
language understanding - the inherent ambiguity of language - head-on,
while logical semantic parsing has to solve it or at least make informed
guesses about the correct meaning. Both techniques, however, are capable
of taking unstructured text data and converting it into a usable format.

Although AI is still a long way from possessing a conceptual structure
of the world that is capable of answering questions about the size of
cities versus breadboxes or whether hardwood floors possess fangs,
effective semantic parsing is a necessary step to parsing,
understanding, storing and retrieving unstructured text data.
