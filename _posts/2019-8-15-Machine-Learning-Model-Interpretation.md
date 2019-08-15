---
layout: post
title: "Machine Learning Model Interpretation"
categories: [data science]
tags: [interpretability, modeling]
author: Nan Shi
mathjax: true
---


To either a model-driven company or a company catching up with the rapid adoption of AI in the industry, machine learning model interpretation has become a key factor that helps to make decisions towards promoting models into business. This is not an easy task -- imagine trying to explain a mathematical theory to your parents. Yet business owners should always be curious about these models, and some questions easily raise:

- How do machine learning models work?
- How reliable are the predictions made from these models?
- How carefully do we have to monitor these models?

As people understand more and more about the need and importance of model interpretation, data scientists need to build up a model interpretation strategy at the beginning of model building process that helps them to answer the questions above, for many possible reasons such as auditing. Such a strategy requires a structure aligned with the scope for interpretability:

- model algorithm and model hyperparameter,
- the model training process,
- model interpretability metrics,
- human-friendly explanations.

At this point, we are talking about a model as an asset in business. We need to understand that producing predictions is only the basics of a model. We also need to make sure that the results of the model can be understood in a business sense. A good model interpretation requires a thorough understanding of the model life cycle as well as a clear and intuitive demonstration in each step.


## Interpretable Models

One of the easier ways to handle model interpretation is to start with an interpretable model, such as linear regression, logistic regression, decision tree, CNN, etc. High interpretability and efficiency are part of the main reasons that these models are widely used across different industries. They have a relative easy algorithm and training process, which are easy to monitor and adjust as a result. 

<figure>
  <img src="/assets/posts/images/2019-8-15/pictures/Drop1.png" style="margin-left: 60px; width: 250px;"/> <img src="/assets/posts/images/2019-8-15/pictures/sk-learn.png" style="margin-left: 60px; width: 400px;"/>
  <figcaption> Source: [Kaggle Housing Price](https://www.kaggle.com/c/house-prices-advanced-regression-techniques), [Scikit-Learn](https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html)</figcaption>
</figure>

Feature importance is a very intuitive score that is implemented in many packages. A feature with higher importance not only contributes more to the prediction made by the model but also accounts for more in the prediction error. As a numerical score, importance can be used to create easy visualizations to present model training results. Feature importance not only provides a straightforward understanding of features but also provides a reliable metric for the dimension reduction process.

- Filter methods select a subset of features and compare model performance, and they generate metrics like linear discriminant analysis, ANOVA, Chi-Square, etc.
- Wrapper methods train a model using a selected subset of features, and feature importance serves as a criterion depending on the selection or elimination method used.


## Neural Networks

People have seen how powerful some of the neural network models can be. Cool visualizations illustrating how these models work help a lot for people to understand them more. Examples include illustrating cues to find the “focus” of deep neural networks in image recognition. Because of the linear nature of some neural networks, it is not hard to trace back several layers of neurons and figure out where the model is focusing on when it is making a prediction.

<figure>
  <img src="/assets/posts/images/2019-8-15/pictures/openAI.png" style="display: block; margin-left: auto; margin-right: auto; width: 80%;"/>
  <figcaption> Source: [Open AI](https://openai.com/blog/introducing-activation-atlases/)</figcaption>
</figure>

However, even though sometimes a nice neural network demo looks nice and informative, it may not show you the feature importance information, i.e. which factors drive the model to make such a prediction. The classic example of tensorflow MNIST model using Convolutional Neural Network has an easy trace-back of which pixels are driving the prediction:

<figure>
  <img src="/assets/posts/images/2019-8-15/pictures/mnist.gif" style="display: block; margin-left: auto; margin-right: auto; width: 60%;"/>
  <figcaption> Source: [Not another MNIST tutorial with TensorFlow](https://www.oreilly.com/learning/not-another-mnist-tutorial-with-tensorflow)</figcaption>
</figure>

Recently, tensorflow also introduced a new `tf-explain` package that helps to generate such trace-back for image recognition as well.

```
from tf_explain.callbacks.occlusion_sensitivity import OcclusionSensitivityCallback

callbacks = [
    GradCAMCallback(
        validation_data=(x_val, y_val),
        layer_name="activation_1",
        class_index=0,
        output_dir=output_dir,
    )
]

model.fit(x_train, y_train, batch_size=2, epochs=2, callbacks=callbacks)

!tensorboard --logdir logs
```

<figure>
  <img src="/assets/posts/images/2019-8-15/pictures/tf-explain.png" style="display: block; margin-left: auto; margin-right: auto; width: 20%;"/>
  <figcaption> Source: [TensorFlow Explain](https://tf-explain.readthedocs.io)</figcaption>
</figure>

We have to keep in mind that each example above uses methods designed for the specific type of models or problems. There are a lot of exploratory works and hyperparameter tuning to do before such a nice demonstration can be made.


## LIME and Shapley Values

Over the years, data scientists and researchers have developed tools to help with model interpretation, and Local Interpretable Model-Agnostic Explanations (LIME) is one of the tools based on the paper ["Why Should I Trust You?": Explaining the Predictions of Any Classifier](https://arxiv.org/abs/1602.04938). The goal is obvious from the title of the paper. LIME does a good job of giving a meaningful estimate of feature importance for a given test data using the idea of Shapley Values, which is a game theory method of assigning weights to features depending on their contribution to the final prediction. 

<figure>
  <img src="/assets/posts/images/2019-8-15/pictures/lime.png" style="display: block; margin-left: auto; margin-right: auto; width: 70%;"/>
  <figcaption> Source: [UC Business Analytics R Programming Guide ](https://uc-r.github.io/lime)</figcaption>
</figure>

However, in contrast to a global surrogate model, which is an approximated interpretable model of a black-box model, being local is one of the biggest disadvantages. Seeing LIME results for a particular data point, which could be quite an abnormal one, does not tell enough story of the whole model. The correct interpretation of "local" is hard to answer as well. To have a better understanding of the model, we would need to run tests on a large number of data points. To go from a local observation to a global picture could cost us a lot of computation power. Also, creating a local surrogate model works fine when the black box model consists of a smooth function, but not so well when the black box model contains many discrete (categorical) variables.


## Concluding Remarks

Even with all these data science tools, model interpretability is still one of the main challenges in machine learning as our models are also growing in complexity. It is one of the most important attributes of a model asset from a business perspective. Researchers are trying their best to reveal the mysterious yet fascinating "black-box" of AI models. Only after we understand our AI models from a deeper level can we improve our AI models to a whole new level.


## Resources

[Interpretable Machine Learning](https://christophm.github.io/interpretable-ml-book/) is a very good online book about this topic by Christoph Molnar for people interested in more details.
