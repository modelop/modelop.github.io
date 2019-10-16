---
layout: post
title: "Machine Learning and Technological Explosion"
categories: [data science]
tags: [machine learning]
author: Nan Shi
mathjax: true
---

In recent years, as commercial capital nourishing technology development, many technologies that challenge humanity are subverting human society: internet giant monopoly, DNA editing, artificial intelligence, etc. One of the core reason that made this "technological explosion" possible is the well-developed computer science industry, which revolutionized the inheritance of knowledge for human beings. More and more STEM elites are dedicating their whole life to the contemporary technological explosion, hoping to promote humanity to a whole new level. The rapid technological development naturally reminds me of my favorite science fiction "The Three-Body Problem", where I first learned the concept of technological explosion:

> "Explosive advances in technology could occur at any moment in any civilization." -- <cite>[Liu, Cixin](https://en.wikipedia.org/wiki/Liu_Cixin)</cite>

Many people think that Liu's theory provides a reasonable explanation to [Fermi paradox](https://en.wikipedia.org/wiki/Fermi_paradox).

There have been a lot of concerns about this technological explosion (or possibly technological singularity):

- whether we can control the AI we created
- what we should do after technological singularity is reached
- whether we are living in a simulation, similar to thousands of those we built, but much more advanced

I am not here to discuss these concerns (or if they should be a concern at all). I would like to take a look at the mathematical theories/development behind all the techniques and algorithms that we are using today, and if mathematics can provide insights towards answering these questions. If this is the time for our civilization, we ought to take it carefully.

## Neural Networks

With the massive popularization and application of data science and machine learning, AI has been on the top of technological explosion. Although human-like reasoning, speech, and decision-making by AI are still far away, we cannot deny the success brought by the application of AI techniques and associated algorithms. Artificial neural network (ANN) is one of the few occasions of abstract algebra having a significant direct impact in an application. Of course, researchers continuously developed from the basic idea:

- convolutional neural networks (CNN)
- long short-term memory
- deep belief networks
- deep stacking networks

While people are fascinated by the power of neural networks and deep learning, they are also somewhat surprised by the outstanding results they are generating - the Black Box Problem. Because of the complexity of neural networks, when data run through them, it is hard to understand what exactly happened inside the model. From a mathematical point of view, neural networks lack a firm theoretical explanation of why it can be successful (although there have been some biological approaches, for example, see [this](https://www.quantamagazine.org/new-theory-cracks-open-the-black-box-of-deep-learning-20170921/) post for a quick overview). Some held the "trust the AI and let it do its thing" kind of attitude. However, if we want to answer the question "whether we can control the AI", we do want to understand what is going on, which also increases the explainability of the model.

While seeking a rigorous mathematical explanation, I started with two fundamental questions:

- What is the fundamental problem in this field?
- Does the fundamental problem have a precise mathematical formulation?

One of the restrictions of neural networks is that they require a huge amount of (training) data, and obtaining high-quality data with proper tags is a bottleneck for many experiments. This is where Generative Adversarial Networks (GANs) shines.

## Generative Adversarial Networks (GANs)

GANs is introduced by Ian Goodfellow et al. in 2014. It consists of two neural networks contesting with each other. One neural network, called the generator, generates new data while the other, the discriminator, evaluates them for authenticity. In a way, these two models are evolving together with continuous feedback to each other. Both nets are trying to optimize a different and opposing objective function, or loss function, in a zero-sum game. (Check out ["A Beginner's Guide to GANs"](https://skymind.ai/wiki/generative-adversarial-network-gan) for a code sample of such a network.)

To put it in a mathematical formulation, the generator turns a Gaussian distribution into corresponding data, and GANs are calculating the distance between two different measures. Even the famous mathematician [Shing-Tung Yau](https://en.wikipedia.org/wiki/Shing-Tung_Yau) tried to understand the question using differential geometry. Yau suggested using optimal transportation theory, which essentially changed to question to solving [Monge–Ampère Equation](https://en.wikipedia.org/wiki/Monge%E2%80%93Amp%C3%A8re_equation). The non-linearity feature of such an equation contradicts with the massive training data in reality. Yau identified the geometric variational principle of the Mongolian-ampere Equation, providing a new mathematical understanding of GANs (see ["A Geometric View of Optimal Transportation and Generative Model"](https://arxiv.org/abs/1710.05488)).

Yau's study revealed a blind spot: people used to think the competition between two neural networks is the essence for GANs' success, while Yau suggested that the generator and the discriminator have a congruent relation. So after the training of the generator, one should naturally obtain a discriminator accordingly without training. Yau's work eventually raised interests from another Fields Medal winner, optimal transportation theory expert and cutting-edge AI researcher Cédric Villani. His report ["For a Meaningful Artificial Intelligence"](https://www.aiforhumanity.fr/pdfs/MissionVillani_Report_ENG-VF.pdf) provides a lot of inspiring thoughts about AI.

## Geometry Processing

While the explanation for GANs is still developing, another application of differential geometry, Geometry Processing, has already shown its capability. It combines concepts from computer graphics and computer science, applied mathematics and physics, mechanics, and engineering.

If you have heard the story of Klein bottles in topology, then the way differential geometry characterize geometric objects should be no surprise to you. Differential geometry provides numeric characterizations of geometric objects like shapes, surfaces, spaces, manifolds, etc. It provides computers a method to represent objects and to visualize them efficiently. For example, graphics texture compression with the help of differential forms and Hodge theory; image smoothing through Laplace operator.

The growing availability of geometry acquisition devices is an important reason why we can implement some of the most abstract mathematical theories into production. That together with a better understanding of the mathematics behind these models have contributed to the realistic pictures and animations we are seeing nowadays.

## Concluding Remarks

I used to have the misunderstanding that theoretical mathematics is far from real-world applications, not realizing the importance of mathematical abstraction in industry. However, from a brief glimpse in one aspect of machine learning, one can already see the power of a rigorous mathematical formulation and the wisdom of a theoretical mathematician.

But there is still a big gap between theoretical studies and industrial application. For one thing, communication between researchers and engineers is still hard. The development of mathematics has always been rigorous yet concealed, so the creation of a new theory that fits industrial needs can only be described as a long-lasting meditation. For another, as the scale of collected data growing rapidly, we are also approaching our computational limit.

Again, if this is the technological explosion for our civilization, the computerized materialization of profound mathematical thought is possibly one of the greatest breakthroughs on our way to the technological singularity.
