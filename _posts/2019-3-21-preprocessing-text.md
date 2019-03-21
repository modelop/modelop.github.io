---
layout: post
title: "When (not) to Lemmatize or Remove Stop Words in Text Preprocessing"
categories: [data science]
tags: [NLP, AI, robots]
author: Alex Schumacher
---

Natural language text is messy.  It's full of disfluencies ('ums' and 'uhs') or spelling mistakes or unexpected foreign text, among others.  What's worse, even when all of that mess is cleaned up, natural language text has structural aspects that are not ideal for many applications.  Two of those challenges, _inconsistency of form_ and _contentless material_ are addressed by two common practices: _lemmatization_ and _stop word removal_. These practices are effective countermeasures to their respective problems, but they are often taken as writ when in fact they should are application- and problem-specific.  In this blog, I'll be discussing lemmatization and stop word removal, why they're done, when to use them, and when not to.

## Lemmatization

Most every (content) word in English can take on several forms.  Sometimes these changes are meaningful, and sometimes they are just to serve a certain grammatical context.  A change in form that is meaningful is said to be related _derivationally_ from one form to the other.  Consider the following examples:

| Base        | Agentive (er/or)     | Practitive (ist) |
| ------------- |:-------------:| -----:|
| adventure      | adventurer | adventurist |
| separate      | separator      | separatist |
| record | recorder  | recordist |

A change in form that is related to grammatical context is said to be _inflected_.  Especially verbs, but also nouns and adjectives, are inflected in English.  

| Base        | Alternate 1    | Alternate 2 |
| ------------- |:-------------:| -----:|
| determine (verb)   | determines | determined |
| cat (noun)     | cats    | cat's |
| gross (adj) | grosser | grossest |

The goal of lemmatization is to standardize each of the inflectional alternates and derivationally related forms to the base form.  There are roughly two ways to accomplish lemmatization: _stemming_ and _replacement_.  Stemming refers to the practice of cutting off or slicing any pattern of string-terminal characters that is a suffix, thereby rendering every form in an unambiguously non inflected or derived state.

### Stemming

There are a number of ways to do this, but one of the most popular is to use the Porter stemmer, which comes with `nltk`.


```python
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

determine = ['determine', 'determines', 'determined']
cat = ['cat', 'cats', "cat's"]

#Stem
stemmed_determine = list(set([stemmer.stem(x) for x in determine]))
stemmed_cat = list(set([stemmer.stem(x).replace("'", '') for x in cat]))

print(stemmed_determine)
print(stemmed_cat)
```

    ['determin']
    ['cat']


The stemmer has reduced (minus some irrelevant punctuation which would be stripped out later) the forms of 'cat' and 'determine' to a consistent form. The Porter stemmer does not reduce everything, however - some forms are retained.


```python
gross = ['gross', 'grosser', 'grossest']
stemmed_gross = list(set([stemmer.stem(x) for x in gross]))
print(stemmed_gross)
```

    ['grossest', 'grosser', 'gross']


And irregular forms of verbs like 'go'/'went' and nouns like 'child', 'children' are not respected at all by a simple stemmer like the Porter stemmer, which just matches normal suffix patterns and relies on a consistent form of the base.


```python
irr = ['go', 'went', 'child', 'children']
irr = [stemmer.stem(x) for x in irr]
print(irr)
```

    ['go', 'went', 'child', 'children']


### Replacement

The shortcomings (or different decisions) made by different lemmatization techniques might motivate the use of a technique like the replacement technique.  The replacement technique relies on curated lists of English words and the relations between them.  For this task, `wordnet` is the most common resource.  This task can be performed by importing `wordnet` directly and working with it, or with a wrapper provided in `nltk`.


```python
from nltk.stem import WordNetLemmatizer as form_replacer

#Provide shorthand pos tag to lemmatizer, since base form differs by part of speech.
lemmatized_determine = list(set([form_replacer().lemmatize(x, 'v') for x in determine]))
lemmatized_cat = list(set([form_replacer().lemmatize(x, 'n') for x in cat]))
lemmatized_gross = list(set([form_replacer().lemmatize(x, 'a') for x in gross]))
lemmatized_irr1 = list(set([form_replacer().lemmatize(x, 'v') for x in ['go', 'went']]))
lemmatized_irr2 = list(set([form_replacer().lemmatize(x, 'n') for x in ['child', 'children']]))

print(lemmatized_determine)
print(lemmatized_cat)
print(lemmatized_gross)
print(lemmatized_irr1+lemmatized_irr2)
```

    ['determine']
    ['cat', "cat's"]
    ['gross']
    ['go', 'child']


The output of the replacement method is more interpretable (it returns actual words) and it handles irregular forms, but it depends on seeing all and only words which exist in its database.  In practice, neologisms or out-of-vocabulary items will occur in any sufficiently large body of text.  Imagine a new verb, 'glorf'.  WordNet fails to return a usable output, while the Porter stemmer correctly lemmatizes it.


```python
print(stemmer.stem('glorfed'))
print(form_replacer().lemmatize('glorfed', 'v'))
```

    glorf
    glorfed


### When to Lemmatize

Lemmatization is a critical step in a number of tasks, but there are times in which it is not appropriate. Some applications decisively benefit from lemmatization.  Topic modeling, for example, relies on the distribution of content words, the identification of which is dependent on a string match between words, which is achieved by lemmatizing their forms so that all variants are consistent across documents.  TD-IDF and LDA therefore both benefit in general from lemmatization.  Lemmatization is also important for training word vectors, since accurate counts within the window of a word would be disrupted by an irrelevant inflection like a simple plural or present tense infleciton.

The general rule for whether to lemmatize is unsurprising: if it does not improve performance, do not lemmatize.  Not lemmatizing is the conservative approach, and should be favored unless there is a significant performance gain.  For example, a popular sentiment analysis method, VADER, has different ratings depending on the form of the word and therefore the input should _not_ be stemmed or lemmatized.


```python
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
print(sid.polarity_scores('He hates broccoli'))
print(sid.polarity_scores('He hated broccoli'))
```

    {'neg': 0.592, 'neu': 0.408, 'pos': 0.0, 'compound': -0.4404}
    {'neg': 0.677, 'neu': 0.323, 'pos': 0.0, 'compound': -0.6369}


The past tense 'hated' is judged more negative by VADER than the present tense 'hates'.  Stemming the input causes them to have the same scores, even though in reality they should be different.


```python
print(sid.polarity_scores(stemmer.stem('He')+" "+stemmer.stem('hates')+" "+stemmer.stem('broccoli')))
print(sid.polarity_scores(stemmer.stem('He')+" "+stemmer.stem('hated')+" "+stemmer.stem('broccoli')))
```

    {'neg': 0.649, 'neu': 0.351, 'pos': 0.0, 'compound': -0.5719}
    {'neg': 0.649, 'neu': 0.351, 'pos': 0.0, 'compound': -0.5719}


This is just a note of caution, then, about always applying lemmatization regardless of the problem.  All preprocessing does not require stemming for the eventual model or application to be effective and it may in fact impede the success or accuracy of the model or application.

## Stop Words

Any slice of natural language text contains seemingly contentless material - think words like 'the' or 'of' (so-called "stop words").  Often, stop words such as those are the most frequent words in any slice of text, and they are so because they form the functional skeleton of any sentence that communicates the grammatical relationships that the content materials has.  Many NLP libraries come equipped with lists of stop words, but there is no fixed definition of a stop word. Rules of thumb like selecting the 10-100 most frequent words in a body of text are also common ways of identifying stop words.

In many NLP applications, stop words are eliminated because NLP applications heavily leverage the statistical profile of the input  for their success.  Irrelevant or contentless and frequent words consequently appear to be nothing but very intrusive noise. And in certain applications, like topic modeling, this can be true.  But in many cases, removing stop words is a mistake.

As mentioned, there are many packages and resources that provide lists of stop words or methods for their removal, but the process itself is exceedingly simple.  Below I demonstrate a simple way to remove stop words using `nltk`, before moving on to showing what problems it can lead to.


```python
from nltk import word_tokenize
from nltk.corpus import stopwords
stop = set(stopwords.words('english'))

#Passage from Roger Ebert's review of 'Office Space'
sample_text = 'Mike Judges "Office Space" is a comic cry of rage against the nightmare of modern office life. It has many of the same complaints as "Dilbert" and the movie "Clockwatchers" and, for that matter, the works of Kafka and the Book of Job. It is about work that crushes the spirit. Office cubicles are cells, supervisors are the wardens, and modern management theory is skewed to employ as many managers and as few workers as possible.'
sample_text = word_tokenize(sample_text.lower())
print(sample_text)

sample_text_without_stop = [x for x in sample_text if x not in stop]
print(sample_text_without_stop)
```

    ['mike', 'judges', '``', 'office', 'space', "''", 'is', 'a', 'comic', 'cry', 'of', 'rage', 'against', 'the', 'nightmare', 'of', 'modern', 'office', 'life', '.', 'it', 'has', 'many', 'of', 'the', 'same', 'complaints', 'as', '``', 'dilbert', "''", 'and', 'the', 'movie', '``', 'clockwatchers', "''", 'and', ',', 'for', 'that', 'matter', ',', 'the', 'works', 'of', 'kafka', 'and', 'the', 'book', 'of', 'job', '.', 'it', 'is', 'about', 'work', 'that', 'crushes', 'the', 'spirit', '.', 'office', 'cubicles', 'are', 'cells', ',', 'supervisors', 'are', 'the', 'wardens', ',', 'and', 'modern', 'management', 'theory', 'is', 'skewed', 'to', 'employ', 'as', 'many', 'managers', 'and', 'as', 'few', 'workers', 'as', 'possible', '.']
    ['mike', 'judges', '``', 'office', 'space', "''", 'comic', 'cry', 'rage', 'nightmare', 'modern', 'office', 'life', '.', 'many', 'complaints', '``', 'dilbert', "''", 'movie', '``', 'clockwatchers', "''", ',', 'matter', ',', 'works', 'kafka', 'book', 'job', '.', 'work', 'crushes', 'spirit', '.', 'office', 'cubicles', 'cells', ',', 'supervisors', 'wardens', ',', 'modern', 'management', 'theory', 'skewed', 'employ', 'many', 'managers', 'workers', 'possible', '.']


With the stop words removed, the first sentence now lacks all instances of 'is', 'a', 'of', 'against', and 'the'.

There are two principle considerations for whether it is appropriate to remove stop words for a given application.  Although stop words lack _lexical_ content, by which I mean, they lack reference to some quality of the external world being described by a given sentence, they are not entirely devoid of content.  Indeed, in the GloVe vectors, stop words are retained.  This is because they may be relevant to the meaning and function of similar words.  In certain cases, stop words do indeed contribute meaning, and if an application is sensitive to such meanings, then stop words should not be eliminated.

To understand how and when this may be the case, consider a verb like 'believe'. 'Believe' with a variety of collocates - all of which are stop words - and all of which change its meaning and thereby also the statistical profile of 'believe'.  This is similar to but not the same thing as word sense, since 'believe' possesses roughly the same meaning in each case.  Instead what changes is the meaning of the event.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The crowd believed the man.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The crowd believed in the man.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The crowd believed that the man was lying.

With stop words removed, each of these examples become the same sequence, namely _crowd believed man_, one of which is indicating the opposite. Retaining the stop words allows distinctions to be drawn between uses of 'believed', and prevents downstream errors as a consequence of failing to make such necessary conditions.

The second consideration is whether or not important information is being lost by their removal.  There are many circumstances in which this might be true.  Consider first a simple case of reference to Dwayne Johnson, also known as "The Rock".  If stop words are removed from a sentiment analysis task on movie reviews, any distinction between The Rock and his role in monster movies and references to the rock monsters from the Thor movies is lost. This is one example, but amplified over many such examples and many reviews, there is potential for substantial information loss, whereas the cost for leaving stop words in may be quite low.

Another case concerns important ordering information.  In the sentences below, the correct interpretation and information to be extracted depends on the ordering of the words and the presence or absence of a stop word 'to'.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stacy gave her doll to the puppy.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stacy gave her doll the puppy.

Those distinction between those two plausible scenarios is lost when stop words are eliminated.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stacy gave doll puppy.

With the stop words gone, there is no way to know which of the two scenarios, the doll being given to the puppy, or the puppy being given to the doll, was intended.  Natural language text is replete with cases where the stop words are critical to understanding the actual meaning being considered.  For any application that needs to be sure of such things, removing stop words would be a critical mistake.

## Concluding Remarks

Lemmatization and stop word removal are both _potentially_ useful steps in preprocessing text, but they are not necessarily necessary.  In order to determine whether either or both such steps should be taken, it is important to consider the nature of the problem.  Is important information being lost by taking either step? Or is irrelevant information being removed? Discussions of preprocessing rarely frame the task in those terms, but they're the ones that count.
