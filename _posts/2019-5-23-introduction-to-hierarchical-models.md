---
layout: post
title: "An Introduction to Hierarchical Models"
categories: [data science]
tags: [bayesian, modeling, hierarchical]
author: Steve Avsec
mathjax: true
---


## Introduction
In a previous [post](https://opendatagroup.github.io/data%20science/2019/01/24/introduction-to-bayesian-modeling.html) we gave an introduction to Stan and PyStan using a basic Bayesian logistic regression model. There isn't generally a compelling reason to use sophisticated Bayesian techniques to build a logistic regression model. This could be easily replicated using simpler techniques. In this post, we shall really unlock the power of Stan and full Bayesian inference in the form of a hierarchical model. Suppose we have a dataset which is stratified into N groups. We have a couple of choices for how to handle this situation. We can effectively ignore the stratification and pool all of the data together and train a model on all of the data at once. The cost of this is that we are losing information added by the stratification. We can fit a separate model for each group, but this runs the risk of overfitting. As we shall see below, groups with few observations will typically represent outliers, but this is not indicative that all observations in the group will behave the same way. If some of the groups have few samples and have significant outlying behavior, it is likely that the behavior is driven by the small sample size rather than the group exhibiting behavior that deviates significantly from the mean behavior. 

Hierarchical models split the difference between these two approaches; groups are each assigned their own model coefficients, but, in the Bayesian language, those model coefficients are drawn from the same prior and thus the coefficient posterior distributions are shrunk toward the global mean. This allows for a model which is robust to overfitting but at the same time remains as interpretable as ordinary regression models. 




```python
import matplotlib.pyplot as plt
import pystan as stan
import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from scipy.stats import bernoulli
import scipy
import itertools
import arviz as az
import pickle
import geopandas as gpd

SEED = 875367
```


```python
df_raw = pd.read_csv('LoanStats3b.csv.zip', header=1)
```

    /home/ubuntu/anaconda3/lib/python3.6/site-packages/IPython/core/interactiveshell.py:2785: DtypeWarning: Columns (0,47,123,124,125,128,129,130,133) have mixed types. Specify dtype option on import or set low_memory=False.
      interactivity=interactivity, compiler=compiler, result=result)



```python
df_raw.shape
```




    (188183, 137)



### The Data
We shall use the same data that we used in our previous [post](https://opendatagroup.github.io/data%20science/2019/01/24/introduction-to-bayesian-modeling.html):
'loan_amnt': The amount of principle given in the loan

'int_rate': The interest rate

'sub_grade': A grade assigned to the loan internally by Lending Club

'annual_inc': The lendee's annual income

'dti': The lendee's debt-to-income ratio

'loan_status': The final status, either "Paid" or "Charged Off", of the loan 

We will also add 'addr_state', which is the state in which the borrower lives. 


```python
keeps = ['loan_amnt', 'int_rate','sub_grade','annual_inc','dti','addr_state','loan_status']

df = df_raw.loc[:,keeps]

df.loan_status.value_counts()
```




    Fully Paid            148549
    Charged Off            28643
    Current                10262
    Late (31-120 days)       331
    In Grace Period          284
    Late (16-30 days)         73
    Default                   39
    Name: loan_status, dtype: int64




```python
def encode_status(x):
    if x == 'Fully Paid':
        return 1
    else:
        return 0
```


```python
#Slice out loans whose terms haven't expired and numerically encode the final status
df = df[df['loan_status'].isin(["Fully Paid", "Charged Off"])]
df.loan_status = df.loan_status.apply(encode_status)
```

We encode the sub_grade feature ordinally and treat this as a numerical feature. There are more sophisticated methods we can use on ordinal features, but this will be the topic of a future post.


```python
#Ordinally encode the sub_grade
df.sub_grade = df.sub_grade.apply(lambda x: 5*ord(x[0]) + int(x[1]))
#Strip the label from interest rate
df.int_rate = df.int_rate.apply(lambda x: float(x.split('%')[0]))
```


```python
features = ['loan_amnt', 'int_rate', 'sub_grade', 'annual_inc', 'dti']
```

### Normalization
We shall use the same normalizations as in the [post](https://opendatagroup.github.io/data%20science/2019/01/24/introduction-to-bayesian-modeling.html).


```python
#Transform features to help with normalization.
df['log_int_rate'] = df.int_rate.apply(np.log)
df['log_annual_inc'] = df.annual_inc.apply(np.log)
df['trans_sub_grade'] = df.sub_grade.apply(lambda x: np.exp(x/100))
df['log_loan_amnt'] = df.loan_amnt.apply(np.log)
```


```python
trans_features = ['log_int_rate', 'log_annual_inc', 'log_loan_amnt', 'trans_sub_grade', 'dti']
```


```python
df['intercept'] = 1
```


```python
agg = df[trans_features + ['addr_state']].groupby('addr_state').mean()
num_loans = df[['addr_state', 'intercept']].groupby('addr_state').count()
num_charged_off = df[['addr_state', 'loan_status']].groupby('addr_state').sum()
```


```python
percentage_charged_off = num_charged_off['loan_status']/num_loans['intercept']
```


```python
num_loans.intercept.sort_values()
```




    addr_state
    IA        1
    ID        2
    MS        3
    NE        3
    VT      285
    SD      388
    WY      421
    DE      436
    MT      534
    AK      535
    DC      537
    RI      741
    NH      828
    WV      838
    NM      941
    HI     1051
    AR     1341
    UT     1413
    OK     1571
    KY     1586
    KS     1665
    TN     1847
    SC     1943
    IN     2085
    LA     2109
    WI     2143
    AL     2168
    OR     2435
    NV     2658
    CT     2688
    MO     2771
    MN     3038
    CO     3752
    MD     4000
    AZ     4073
    MA     4156
    WA     4240
    MI     4252
    NC     5079
    VA     5391
    OH     5502
    GA     5503
    PA     5900
    NJ     6751
    IL     6836
    FL    12197
    TX    13673
    NY    15365
    CA    29517
    Name: intercept, dtype: int64




```python
map_df = gpd.read_file('tl_2017_us_state.shx')
```

    INFO:fiona.ogrext:Failed to auto identify EPSG: 7



```python
map_df.shape

map_df.STUSPS.sort_values()
#These states and territories appear in our shape file but not in the data
not_in_data = ['AS', 'GU', 'MP', 'VI', 'PR', 'ND', 'ME']
#Use states as indices to make merging easier
map_df.set_index('STUSPS', inplace=True)

map_df.drop(not_in_data, inplace=True, axis=0)
#This cuts out the Aleutian Islands since they were causing issues rendering the map
map_df.loc['AK', 'geometry'] = map_df.loc['AK', 'geometry'][48]
```


```python
map_df = pd.concat([map_df, agg], axis=1)
```


```python
map_df['number_of_loans'] = num_loans['intercept']
map_df['log_number_of_loans'] = map_df.number_of_loans.apply(np.log)
map_df['percentage_charged_off'] = num_charged_off['loan_status']/map_df.number_of_loans
```

Below we see plots of averages of each feature by state as well the log of the number of observations and a normalized percentage of charged off loans. Notice that the outliers are Idaho, Iowa, Mississippi, and Nebraska, the states with the fewest data points.


```python
for feature in trans_features + ['log_number_of_loans', 'percentage_charged_off']:
    ax = map_df.plot(feature, figsize=(30,15), legend=True)
    ax.set_title(feature, fontsize=18)

```


![png](output_23_0.png)



![png](output_23_1.png)



![png](output_23_2.png)



![png](output_23_3.png)



![png](output_23_4.png)



![png](output_23_5.png)



![png](output_23_6.png)



```python
final = df.loc[:,trans_features+['addr_state','loan_status']]
final['addr_state_codes'] = final.addr_state.astype('category').cat.codes + 1
final['intercept'] = 1

train, test = train_test_split(final, train_size = 0.8, random_state=SEED)
print(len(train))
print(len(test))
```

    141753
    35439


    /home/ubuntu/anaconda3/lib/python3.6/site-packages/sklearn/model_selection/_split.py:2026: FutureWarning: From version 0.21, test_size will always complement train_size unless both are specified.
      FutureWarning)



```python
final.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>log_int_rate</th>
      <th>log_annual_inc</th>
      <th>log_loan_amnt</th>
      <th>trans_sub_grade</th>
      <th>dti</th>
      <th>addr_state</th>
      <th>loan_status</th>
      <th>addr_state_codes</th>
      <th>intercept</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2.030776</td>
      <td>12.691580</td>
      <td>10.239960</td>
      <td>26.575773</td>
      <td>18.55</td>
      <td>CA</td>
      <td>1</td>
      <td>5</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2.706716</td>
      <td>11.407565</td>
      <td>9.314700</td>
      <td>29.370771</td>
      <td>3.73</td>
      <td>NY</td>
      <td>1</td>
      <td>33</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2.604909</td>
      <td>11.512925</td>
      <td>10.085809</td>
      <td>28.502734</td>
      <td>22.18</td>
      <td>MI</td>
      <td>1</td>
      <td>22</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2.396986</td>
      <td>10.404263</td>
      <td>8.987197</td>
      <td>27.660351</td>
      <td>15.75</td>
      <td>CO</td>
      <td>0</td>
      <td>6</td>
      <td>1</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2.672078</td>
      <td>11.492723</td>
      <td>9.615805</td>
      <td>29.078527</td>
      <td>6.15</td>
      <td>NY</td>
      <td>1</td>
      <td>33</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>




```python
len(train.addr_state.value_counts())
```




    49




```python
test.addr_state.value_counts()
```




    CA    5879
    NY    3107
    TX    2796
    FL    2420
    NJ    1307
    IL    1296
    GA    1126
    PA    1116
    VA    1114
    OH    1112
    NC    1061
    WA     881
    AZ     834
    MA     831
    MI     820
    MD     777
    CO     682
    MO     609
    MN     565
    CT     532
    NV     529
    OR     487
    AL     456
    LA     439
    SC     413
    IN     404
    WI     403
    TN     377
    KY     333
    OK     329
    KS     328
    UT     293
    AR     271
    HI     220
    NM     195
    WV     162
    NH     156
    RI     148
    AK     112
    DC     107
    MT     105
    DE      98
    SD      77
    WY      72
    VT      58
    NE       2
    Name: addr_state, dtype: int64




```python
train.addr_state.astype('category').cat.codes
```




    158925    21
    44469     36
    184000    45
    69645     47
    185689    38
    263        4
    147208    16
    56444     39
    59523      4
    41995     33
    106414    43
    113278     4
    37510     36
    97609     36
    24733     26
    134001    41
    29383      0
    80420     32
    55874      4
    4394      32
    104677    40
    71772      9
    139493    29
    135066    36
    134982     4
    149350    10
    95968     32
    148455    43
    16338      4
    9747      15
              ..
    119911    18
    74705      4
    97524      9
    14466     29
    40478     22
    175799    32
    6751      41
    22582      4
    68393      4
    40162     43
    112193    40
    62495      9
    26629      2
    15900     10
    48097      4
    182468    32
    107745    29
    186572    19
    96366      6
    157966     1
    21213     32
    10985     18
    153411    16
    98794     32
    138658    43
    16392     11
    110020     9
    178935    14
    31507      4
    158272     4
    Length: 141753, dtype: int8




```python
train.addr_state.head()
```




    158925    MI
    44469     PA
    184000    WA
    69645     WV
    185689    SC
    Name: addr_state, dtype: object



### Standard Normalization
Finally, we shall perform some standard normalization of the data in order to improve performance of the sampler.


```python
means = train.loc[:, trans_features].mean()

standard_dev = train.loc[:, trans_features].std()

train.loc[:, trans_features] = (train.loc[:, trans_features] - means)/standard_dev

test.loc[:, trans_features] = (test.loc[:, trans_features] - means)/standard_dev
```

    /home/ubuntu/anaconda3/lib/python3.6/site-packages/pandas/core/indexing.py:537: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
      self.obj[item] = s



```python
train.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>log_int_rate</th>
      <th>log_annual_inc</th>
      <th>log_loan_amnt</th>
      <th>trans_sub_grade</th>
      <th>dti</th>
      <th>addr_state</th>
      <th>loan_status</th>
      <th>addr_state_codes</th>
      <th>intercept</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>158925</th>
      <td>0.595505</td>
      <td>-0.704328</td>
      <td>-0.311701</td>
      <td>0.366447</td>
      <td>-0.605021</td>
      <td>MI</td>
      <td>1</td>
      <td>22</td>
      <td>1</td>
    </tr>
    <tr>
      <th>44469</th>
      <td>1.773829</td>
      <td>-0.944183</td>
      <td>0.587072</td>
      <td>2.567464</td>
      <td>1.501574</td>
      <td>PA</td>
      <td>1</td>
      <td>37</td>
      <td>1</td>
    </tr>
    <tr>
      <th>184000</th>
      <td>1.345375</td>
      <td>0.818958</td>
      <td>1.107789</td>
      <td>2.387811</td>
      <td>-0.096487</td>
      <td>WA</td>
      <td>1</td>
      <td>46</td>
      <td>1</td>
    </tr>
    <tr>
      <th>69645</th>
      <td>0.684856</td>
      <td>-1.576136</td>
      <td>-2.321709</td>
      <td>0.525785</td>
      <td>0.657092</td>
      <td>WV</td>
      <td>1</td>
      <td>48</td>
      <td>1</td>
    </tr>
    <tr>
      <th>185689</th>
      <td>0.825274</td>
      <td>-1.878349</td>
      <td>-0.812906</td>
      <td>1.179311</td>
      <td>0.401508</td>
      <td>SC</td>
      <td>1</td>
      <td>39</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



### The Stan Model
Below there are two Stan models. The first is a simple model based on the model specification given in the introduction. This model suffers from a difficulty in described and visualized excellently in this [blog post](https://twiecki.io/blog/2017/02/08/bayesian-hierchical-non-centered/). The second model is the reparameterization describe in Dr. Wiecki's post and recoded in Stan. If what is happening here seems contrived and confusing, think back to when you took vector calculus; this reparameterization is akin to changing variables to make an integral computation easier. In more sophisticated mathematical language, we are reparameterizing a particular manifold in order to make an integral computation more efficient. 


```python
hierarchical_model = '''
data {
    int<lower=1> D;
    int<lower=0> N;
    int<lower=1> L;
    int<lower=0,upper=1> y[N];
    int<lower=1,upper=L> ll[N];
    row_vector[D] x[N];
}
parameters {
    real mu[D];
    real<lower=0> sigma[D];
    vector[D] beta[L];
}
model {
    mu ~ normal(0, 100);
    for (l in 1:L)
        beta[l] ~ normal(mu, sigma);
    for (n in 1:N)
        y[n] ~ bernoulli(inv_logit(x[n] * beta[ll[n]]));
}
'''
```


```python
noncentered_model = '''
data {
int N;
int D;
int L;
row_vector[D] x[N];
int<lower=0, upper=L> ll[N];
int<lower=0, upper=1> y[N];
}
parameters {
vector[D] mu;
vector<lower=0>[D] sigma;
vector[D] offset[L];
real eps[L];
}
transformed parameters{
vector[D] theta[L];
for (l in 1:L){
theta[l] = mu + offset[l].*sigma;
}
}
model {
vector[N] x_theta_ll;
mu ~ normal(0,100);
sigma ~ cauchy(0,50);
eps ~ normal(0,1);
for (l in 1:L){
    offset[l] ~ normal(0,1);
}

for (n in 1:N){
y[n] ~ bernoulli_logit(x[n]*theta[ll[n]] + eps[ll[n]]);
}
}
'''

```

### Compiling the Stan model
Stan is a domain-specific language written in C++. The model must be compiled into a C++ program. The upshot of this is that a model can be compiled once and reused as long as the data schema does not change. Here we are serializing the model and then deserializing later to save the compilation step.


```python
sm = stan.StanModel(model_code=noncentered_model, model_name='HLR')
```


```python
pickle.dump(sm, open('HLR_model_20190522.pkl','wb'))
```


```python
sm = pickle.load(open('HLR_model_20190522.pkl', 'rb'))
```


```python
#The sampling methods in PyStan require the data to be input as a Python dictionary whose keys match
#the data block of the Stan code.
data = dict(x = train.loc[:,trans_features].values,  
            N = len(train), 
            L = len(train.addr_state.value_counts()),
            D = len(trans_features), 
            ll = train.addr_state_codes.values,
            y = train.loan_status.values)


```


```python
data
```

### Sampling
The sampling step takes about 90 minutes on a compute-optimized AWS EC2 instance. This is another object that can be serialized for later use. It does depend on the Stan model that was used for sampling, and so the model deserialization step above is necessary to deserialize the samples as well. If an hour and a half seems like a long time to sample, bear in mind that we are drawing 6000 samples from 49 states times 6 features, so 6000 samples for almost three hundred model parameters.


```python
fit = sm.sampling(data=data, chains=4, iter=2000, warmup=500)
```


    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-29-ce9f7abab878> in <module>()
    ----> 1 fit = sm.sampling(data=data, chains=4, iter=2000, warmup=500)
    

    NameError: name 'data' is not defined



```python
pickle.dump(fit, open('HLR_fit_20190522.pkl', 'wb'))
```


    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-30-32f7ed1513d8> in <module>()
    ----> 1 pickle.dump(fit, open('HLR_fit_20190522.pkl', 'wb'))
    

    NameError: name 'fit' is not defined



```python
fit = pickle.load(open('HLR_fit_20190522.pkl','rb'))
```

    /home/ubuntu/anaconda3/lib/python3.6/site-packages/pystan/misc.py:399: FutureWarning: Conversion of the second argument of issubdtype from `float` to `np.floating` is deprecated. In future, it will be treated as `np.float64 == np.dtype(float).type`.
      elif np.issubdtype(np.asarray(v).dtype, float):



```python
print(fit)
```

    Inference for Stan model: HLR_9c6e03d80712460fa2867bb8c7ed8f71.
    4 chains, each with iter=2000; warmup=500; thin=1; 
    post-warmup draws per chain=1500, total post-warmup draws=6000.
    
                   mean se_mean     sd   2.5%    25%    50%    75%  97.5%  n_eff   Rhat
    mu[0]         -0.43  3.4e-4   0.03  -0.48  -0.45  -0.43  -0.41  -0.38   6000    1.0
    mu[1]           0.3  1.5e-4   0.01   0.28   0.29    0.3   0.31   0.32   6000    1.0
    mu[2]         -0.26  1.5e-4   0.01  -0.28  -0.27  -0.26  -0.25  -0.24   6000    1.0
    mu[3]          -0.2  2.8e-4   0.02  -0.24  -0.22   -0.2  -0.19  -0.16   6000    1.0
    mu[4]          -0.1  1.4e-4   0.01  -0.12  -0.11   -0.1  -0.09  -0.08   6000    1.0
    sigma[0]       0.02  3.2e-4   0.01 1.3e-3   0.01   0.02   0.03   0.05   1947    1.0
    sigma[1]       0.02  3.6e-4   0.01 1.5e-3   0.01   0.02   0.03   0.06   1682    1.0
    sigma[2]       0.03  3.4e-4   0.01 3.3e-3   0.02   0.03   0.04   0.06   1823    1.0
    sigma[3]       0.02  2.4e-4   0.01 7.1e-4 6.7e-3   0.01   0.02   0.04   1967    1.0
    sigma[4]       0.04  2.5e-4   0.01   0.01   0.03   0.04   0.04   0.06   2321    1.0
    offset[0,0] -2.5e-3    0.01   0.98  -1.96  -0.66-1.8e-4   0.66   1.91   6000    1.0
    offset[1,0]   -0.01    0.01   0.93  -1.83  -0.63  -0.02    0.6   1.81   6000    1.0
    offset[2,0]  9.4e-3    0.01   0.97  -1.84  -0.65 5.7e-3   0.66   1.89   6000    1.0
    offset[3,0]    0.11    0.01    0.9  -1.65  -0.49   0.09   0.73   1.89   6000    1.0
    offset[4,0]   -0.27    0.01   0.79  -1.78  -0.77  -0.28   0.23   1.33   6000    1.0
    offset[5,0]     0.3    0.01   0.95   -1.6  -0.33   0.31   0.92   2.16   6000    1.0
    offset[6,0]    0.22    0.01   0.94  -1.63  -0.42   0.22   0.87   2.04   6000    1.0
    offset[7,0]    0.04    0.01   0.99  -1.89  -0.63   0.04   0.71   1.97   6000    1.0
    offset[8,0]   -0.01    0.01   0.99  -1.98  -0.69  -0.02   0.67   1.94   6000    1.0
    offset[9,0]    0.61    0.01   0.88  -1.23   0.05   0.64    1.2    2.3   6000    1.0
    offset[10,0]   -0.2    0.01   0.92  -1.99  -0.82  -0.22   0.38   1.64   6000    1.0
    offset[11,0]  -0.31    0.01   0.99  -2.28  -0.99  -0.31   0.36   1.64   6000    1.0
    offset[12,0]  -0.01    0.01    1.0  -1.97  -0.68-3.1e-3   0.65   1.94   6000    1.0
    offset[13,0]-4.4e-3    0.01    1.0  -1.94  -0.68 2.7e-3   0.68   1.88   6000    1.0
    offset[14,0]   0.51    0.01   0.91  -1.35  -0.09   0.53   1.12   2.24   6000    1.0
    offset[15,0]  -0.32    0.01   0.96  -2.22  -0.97  -0.33   0.33    1.6   6000    1.0
    offset[16,0]-7.3e-3    0.01   0.97  -1.91  -0.68 1.7e-6   0.67   1.87   6000    1.0
    offset[17,0]  -0.04    0.01   0.97  -1.92   -0.7  -0.04   0.62   1.83   6000    1.0
    offset[18,0]  -0.06    0.01   0.97  -1.99  -0.71  -0.05   0.59   1.82   6000    1.0
    offset[19,0]   0.12    0.01    0.9  -1.67  -0.48   0.13   0.71   1.86   6000    1.0
    offset[20,0]  -0.13    0.01   0.91   -1.9  -0.74  -0.13   0.46    1.7   6000    1.0
    offset[21,0]  -0.44    0.01   0.94  -2.24  -1.08  -0.46   0.18   1.45   6000    1.0
    offset[22,0]   0.42    0.01   0.98  -1.52  -0.24   0.44   1.08   2.27   6000    1.0
    offset[23,0]  -0.29    0.01   0.95  -2.15  -0.93  -0.29   0.34   1.61   6000    1.0
    offset[24,0]  -0.02    0.01   1.01  -2.01  -0.71-7.3e-3   0.64   1.96   6000    1.0
    offset[25,0]  -0.05    0.01   0.98  -1.99   -0.7  -0.05   0.61   1.88   6000    1.0
    offset[26,0]   0.12    0.01   0.92  -1.74  -0.49   0.12   0.74   1.88   6000    1.0
    offset[27,0]-8.5e-3    0.01    1.0  -2.01  -0.67-3.2e-3   0.68   1.92   6000    1.0
    offset[28,0] 1.4e-3    0.01   0.98  -1.89  -0.67   0.01   0.67   1.95   6000    1.0
    offset[29,0]    0.2    0.01   0.91  -1.63   -0.4    0.2    0.8   1.97   6000    1.0
    offset[30,0]  -0.07    0.01   0.99  -1.99  -0.73  -0.08   0.58   1.87   6000    1.0
    offset[31,0]   0.52    0.01   0.98  -1.46  -0.14   0.56   1.18    2.4   6000    1.0
    offset[32,0]   0.61    0.01   0.87  -1.21   0.07   0.64   1.19   2.28   6000    1.0
    offset[33,0]  -0.51    0.01   0.94  -2.32  -1.14  -0.53   0.11   1.37   6000    1.0
    offset[34,0]   0.24    0.01   0.98  -1.64  -0.43   0.26   0.91   2.13   6000    1.0
    offset[35,0]   0.12    0.01   0.97  -1.74  -0.55   0.11   0.77   1.97   6000    1.0
    offset[36,0]  -0.64    0.01   0.96  -2.42   -1.3  -0.65-9.9e-3   1.33   6000    1.0
    offset[37,0]   0.06    0.01   0.97  -1.81  -0.61   0.05   0.71   1.96   6000    1.0
    offset[38,0]    0.1    0.01   0.96  -1.76  -0.54    0.1   0.75   2.03   6000    1.0
    offset[39,0]   0.11    0.01   0.98  -1.81  -0.57    0.1   0.78   2.08   6000    1.0
    offset[40,0]-3.9e-3    0.01   0.95  -1.85  -0.65  -0.01   0.66   1.84   6000    1.0
    offset[41,0]  -0.09    0.01   0.87  -1.83  -0.65  -0.08   0.47   1.64   6000    1.0
    offset[42,0]   -0.2    0.01   0.98  -2.12  -0.86  -0.21   0.45   1.76   6000    1.0
    offset[43,0]  -0.25    0.01   0.91  -2.07  -0.83  -0.24   0.34   1.56   6000    1.0
    offset[44,0]   0.06    0.01   0.99  -1.87  -0.61   0.07   0.72   1.97   6000    1.0
    offset[45,0]  -0.18    0.01   0.93  -2.02  -0.79  -0.19   0.43   1.62   6000    1.0
    offset[46,0]  -0.34    0.01   0.97   -2.2  -0.99  -0.37    0.3   1.63   6000    1.0
    offset[47,0]  -0.08    0.01    1.0  -2.07  -0.74  -0.07   0.59   1.91   6000    1.0
    offset[48,0]   0.08    0.01   0.99  -1.87  -0.58   0.06   0.73   2.06   6000    1.0
    offset[0,1]    0.05    0.01    1.0  -1.91  -0.62   0.06   0.73    2.0   6000    1.0
    offset[1,1]    0.13    0.01   0.96  -1.77  -0.48   0.12   0.75   2.02   6000    1.0
    offset[2,1]    0.13    0.01   0.94  -1.72  -0.51   0.14   0.74   2.01   6000    1.0
    offset[3,1]    0.58    0.01   0.94  -1.37  -0.02   0.62   1.22   2.33   6000    1.0
    offset[4,1]   -0.31  9.9e-3   0.76  -1.82   -0.8  -0.33   0.15   1.26   6000    1.0
    offset[5,1]    1.09    0.01   1.05  -1.09    0.4   1.13   1.84   3.01   6000    1.0
    offset[6,1]    0.03    0.01   0.93  -1.82   -0.6   0.02   0.64   1.89   6000    1.0
    offset[7,1]     0.2    0.01    1.0  -1.77  -0.48   0.19   0.89    2.2   6000    1.0
    offset[8,1]    0.21    0.01   1.01  -1.78  -0.47   0.22    0.9   2.21   6000    1.0
    offset[9,1]   -0.39    0.01   0.85  -2.03  -0.93  -0.41   0.13   1.36   6000    1.0
    offset[10,1]   0.11    0.01   0.89  -1.61   -0.5   0.11   0.72   1.82   6000    1.0
    offset[11,1]  -0.27    0.01   0.98  -2.16  -0.92  -0.28   0.38   1.69   6000    1.0
    offset[12,1]   0.01    0.01   0.97  -1.86  -0.64 6.1e-3   0.65   1.92   6000    1.0
    offset[13,1]  -0.01    0.01   1.01  -1.96   -0.7 4.5e-3   0.66   1.95   6000    1.0
    offset[14,1]   0.03    0.01   0.89  -1.81  -0.55   0.02   0.62   1.78   6000    1.0
    offset[15,1]   0.08    0.01   0.97  -1.85  -0.56   0.07   0.73   2.01   6000    1.0
    offset[16,1]  -0.28    0.01   0.97  -2.16  -0.93  -0.29   0.37   1.63   6000    1.0
    offset[17,1]  -0.05    0.01   0.96  -1.87  -0.71  -0.05    0.6   1.85   6000    1.0
    offset[18,1]   0.08    0.01   0.94  -1.71  -0.56   0.07    0.7   1.95   6000    1.0
    offset[19,1]   0.48    0.01   0.94  -1.41  -0.13    0.5   1.11    2.3   6000    1.0
    offset[20,1]  -0.12    0.01   0.93  -1.94  -0.74  -0.11   0.48   1.71   6000    1.0
    offset[21,1]   0.04    0.01    0.9  -1.71  -0.55   0.03   0.64   1.84   6000    1.0
    offset[22,1]   0.09    0.01   0.94  -1.78  -0.55    0.1   0.71   1.94   6000    1.0
    offset[23,1]   0.08    0.01   0.93  -1.71  -0.55   0.08   0.71   1.88   6000    1.0
    offset[24,1]  -0.01    0.01   1.02  -2.02  -0.71  -0.01   0.68   1.96   6000    1.0
    offset[25,1]  -0.22    0.01   1.02   -2.2  -0.91  -0.22   0.46   1.84   6000    1.0
    offset[26,1]   0.14    0.01    0.9  -1.69  -0.46   0.14   0.72   1.93   6000    1.0
    offset[27,1]-3.0e-3    0.01   1.01  -1.98  -0.69-2.3e-3   0.69   1.94   6000    1.0
    offset[28,1]   0.28    0.01   0.98   -1.6  -0.39   0.27   0.96   2.19   6000    1.0
    offset[29,1]  -0.29    0.01   0.88  -1.99  -0.88  -0.31   0.27   1.52   6000    1.0
    offset[30,1]   0.09    0.01   0.99  -1.81  -0.57   0.09   0.76   2.04   6000    1.0
    offset[31,1]   0.18    0.01   0.94  -1.68  -0.43   0.17   0.82   2.04   6000    1.0
    offset[32,1]  -0.41    0.01   0.81  -1.97  -0.95  -0.43    0.1   1.22   6000    1.0
    offset[33,1]   0.14    0.01   0.88   -1.6  -0.43   0.15   0.72   1.89   6000    1.0
    offset[34,1]  -0.56    0.01   1.03  -2.53  -1.27  -0.58   0.13   1.48   6000    1.0
    offset[35,1]   0.34    0.01   0.95  -1.55  -0.27   0.35   0.96   2.18   6000    1.0
    offset[36,1]   -0.3    0.01   0.91  -2.02  -0.92  -0.31    0.3   1.49   6000    1.0
    offset[37,1]   0.15    0.01   0.96  -1.73  -0.51   0.16    0.8   2.04   6000    1.0
    offset[38,1]  -0.16    0.01   0.95   -2.0  -0.81  -0.16   0.48   1.77   6000    1.0
    offset[39,1]  -0.12    0.01   0.99  -2.04  -0.79  -0.12   0.55   1.83   6000    1.0
    offset[40,1]  -0.21    0.01   0.96  -2.08  -0.87   -0.2   0.43   1.69   6000    1.0
    offset[41,1]  -0.76    0.01    0.9  -2.43  -1.38   -0.8  -0.19   1.11   6000    1.0
    offset[42,1]  -0.07    0.01   0.96  -1.95  -0.73  -0.08   0.57   1.82   6000    1.0
    offset[43,1]   0.29    0.01   0.91  -1.55  -0.32   0.29   0.89   2.08   6000    1.0
    offset[44,1]-9.4e-3    0.01   1.01   -2.0   -0.7-2.7e-3   0.67   1.96   6000    1.0
    offset[45,1]  -0.08    0.01   0.91   -1.9  -0.66  -0.09   0.52   1.74   6000    1.0
    offset[46,1]   0.03    0.01   0.95  -1.86   -0.6   0.03   0.67   1.85   6000    1.0
    offset[47,1]  -0.32    0.01    1.0  -2.26  -0.99  -0.32   0.37   1.62   6000    1.0
    offset[48,1]  -0.19    0.01   0.98  -2.12  -0.86  -0.19   0.46   1.74   6000    1.0
    offset[0,2]    0.14    0.01   0.99  -1.79  -0.54   0.13   0.83   2.07   6000    1.0
    offset[1,2]    0.03    0.01   0.93  -1.79   -0.6   0.04   0.64   1.86   6000    1.0
    offset[2,2]   -0.07    0.01   0.95  -1.94  -0.71  -0.07   0.56    1.8   6000    1.0
    offset[3,2]   -0.17    0.01    0.9  -1.95  -0.76  -0.19   0.43   1.61   6000    1.0
    offset[4,2]    0.77  9.2e-3   0.71  -0.69   0.33   0.77   1.23   2.15   6000    1.0
    offset[5,2]    0.88    0.01   0.96  -1.06   0.26   0.91   1.54   2.71   6000    1.0
    offset[6,2]   -0.13    0.01    0.9  -1.94  -0.74  -0.13   0.47   1.66   6000    1.0
    offset[7,2]    0.14    0.01   1.01  -1.87  -0.54   0.14   0.82   2.09   6000    1.0
    offset[8,2]    0.12    0.01   0.97  -1.78  -0.55   0.14   0.78   2.01   6000    1.0
    offset[9,2]    0.53  9.9e-3   0.77   -1.0   0.03   0.54   1.04   2.02   6000    1.0
    offset[10,2] 3.7e-3    0.01   0.87  -1.72  -0.58-2.0e-3    0.6   1.73   6000    1.0
    offset[11,2]  -0.16    0.01   0.92  -1.92  -0.78  -0.16   0.47   1.61   6000    1.0
    offset[12,2] 1.2e-3    0.01   0.97  -1.89  -0.65  -0.02   0.64   1.94   6000    1.0
    offset[13,2]  -0.02    0.01   0.99  -1.92  -0.71  -0.02   0.66   1.88   6000    1.0
    offset[14,2]   0.41    0.01   0.85  -1.34  -0.13   0.43   0.97   2.09   6000    1.0
    offset[15,2]  -0.15    0.01   0.92  -1.93  -0.78  -0.16   0.48   1.67   6000    1.0
    offset[16,2]    0.2    0.01   0.93  -1.64  -0.41    0.2   0.82   2.01   6000    1.0
    offset[17,2]  -0.31    0.01   0.96  -2.16  -0.96  -0.32   0.33   1.58   6000    1.0
    offset[18,2]  -0.26    0.01   0.94   -2.1  -0.86  -0.26   0.36   1.59   6000    1.0
    offset[19,2]   0.27    0.01   0.94  -1.57  -0.36   0.28    0.9   2.17   6000    1.0
    offset[20,2]  -0.24    0.01   0.87  -1.98  -0.81  -0.25   0.35   1.53   6000    1.0
    offset[21,2]  -0.09    0.01   0.87  -1.77  -0.68   -0.1   0.49    1.6   6000    1.0
    offset[22,2]   -0.1    0.01   0.91  -1.88   -0.7  -0.09   0.52   1.65   6000    1.0
    offset[23,2]   0.12    0.01    0.9   -1.7  -0.45   0.12    0.7    1.9   6000    1.0
    offset[24,2]  -0.03    0.01   1.01  -2.07  -0.68  -0.02   0.66   1.97   6000    1.0
    offset[25,2]  -0.19    0.01   0.98  -2.18  -0.84  -0.19   0.46    1.7   6000    1.0
    offset[26,2]  -0.51    0.01   0.87   -2.2   -1.1  -0.53   0.05   1.27   6000    1.0
    offset[27,2]   0.02    0.01   0.99  -1.92  -0.66   0.02    0.7   1.98   6000    1.0
    offset[28,2]   0.41    0.01   1.01   -1.6  -0.25   0.39   1.08   2.41   6000    1.0
    offset[29,2]  -0.02    0.01   0.84  -1.68  -0.58  -0.02   0.52    1.6   6000    1.0
    offset[30,2]  -0.02    0.01   0.98  -1.96  -0.69  -0.02   0.64   1.91   6000    1.0
    offset[31,2]   0.46    0.01    0.9  -1.34  -0.14   0.46   1.06   2.22   6000    1.0
    offset[32,2]  -0.63  9.7e-3   0.75  -2.11  -1.11  -0.63  -0.15   0.89   6000    1.0
    offset[33,2]  -0.11    0.01   0.84  -1.78  -0.68  -0.11   0.45   1.55   6000    1.0
    offset[34,2]  -0.16    0.01   0.94  -1.97  -0.79  -0.17   0.48   1.69   6000    1.0
    offset[35,2]    0.9    0.01   0.99  -1.15   0.26   0.93   1.58   2.73   6000    1.0
    offset[36,2]  -0.97    0.01   0.88  -2.64  -1.56  -1.01   -0.4   0.86   6000    1.0
    offset[37,2]   0.44    0.01   0.97  -1.45  -0.21   0.45   1.08   2.37   6000    1.0
    offset[38,2]  -0.44    0.01   0.95   -2.3  -1.09  -0.45   0.19   1.44   6000    1.0
    offset[39,2]   -0.2    0.01   0.97  -2.11  -0.86  -0.21   0.45    1.7   6000    1.0
    offset[40,2]  -0.06    0.01   0.93  -1.86  -0.67  -0.06   0.56   1.76   6000    1.0
    offset[41,2]   0.43  9.7e-3   0.75  -1.09  -0.06   0.44   0.92    1.9   6000    1.0
    offset[42,2]   -0.5    0.01   0.98  -2.42  -1.18  -0.51   0.16   1.45   6000    1.0
    offset[43,2]   0.12    0.01   0.86  -1.58  -0.46   0.12    0.7    1.8   6000    1.0
    offset[44,2]   0.05    0.01   0.99  -1.88  -0.62   0.04   0.72   2.02   6000    1.0
    offset[45,2]   0.13    0.01   0.89  -1.66  -0.46   0.14   0.72    1.9   6000    1.0
    offset[46,2]  -0.23    0.01   0.92  -2.06  -0.84  -0.22   0.39   1.59   6000    1.0
    offset[47,2]  -0.38    0.01    1.0  -2.29  -1.07  -0.39   0.31   1.58   6000    1.0
    offset[48,2]  -0.23    0.01   0.98  -2.15  -0.89  -0.23   0.43   1.71   6000    1.0
    offset[0,3]    0.06    0.01   1.01  -1.96  -0.61   0.07   0.73   2.07   6000    1.0
    offset[1,3]    0.04    0.01   0.93  -1.77   -0.6   0.04   0.68    1.8   6000    1.0
    offset[2,3]  3.3e-3    0.01   0.98  -1.94  -0.64 9.7e-3   0.67   1.88   6000    1.0
    offset[3,3]    0.04    0.01   0.93   -1.8   -0.6   0.04   0.66   1.88   6000    1.0
    offset[4,3]   -0.24    0.01   0.85  -1.91  -0.79  -0.26    0.3   1.43   6000    1.0
    offset[5,3]    0.33    0.01   0.97  -1.57  -0.33   0.34   0.98    2.2   6000    1.0
    offset[6,3]    0.13    0.01   0.97  -1.78  -0.53   0.14    0.8   2.01   6000    1.0
    offset[7,3]   -0.02    0.01   1.01  -2.03  -0.68  -0.02   0.67   2.01   6000    1.0
    offset[8,3]   -0.01    0.01   0.98  -1.93  -0.68  -0.01   0.64   1.89   6000    1.0
    offset[9,3]    0.19    0.01   0.91  -1.66  -0.41   0.21    0.8   1.92   6000    1.0
    offset[10,3]  -0.24    0.01   0.95  -2.09  -0.87  -0.27   0.37    1.7   6000    1.0
    offset[11,3]  -0.31    0.01   0.98  -2.26  -0.96  -0.32   0.35   1.58   6000    1.0
    offset[12,3]-7.8e-3    0.01   1.01  -2.05  -0.65  -0.01   0.65    2.0   6000    1.0
    offset[13,3]-7.9e-3    0.01   0.96  -1.89  -0.66  -0.01   0.65   1.87   6000    1.0
    offset[14,3]   0.34    0.01   0.92   -1.5  -0.26   0.36   0.97   2.11   6000    1.0
    offset[15,3]  -0.16    0.01   0.97  -2.12   -0.8  -0.16   0.49   1.77   6000    1.0
    offset[16,3]  -0.04    0.01   0.99   -2.0  -0.72  -0.05   0.65   1.88   6000    1.0
    offset[17,3]  -0.03    0.01   0.98  -1.97  -0.67  -0.04   0.62   1.84   6000    1.0
    offset[18,3]   0.08    0.01   0.97  -1.79  -0.59   0.09   0.72   2.01   6000    1.0
    offset[19,3]   0.17    0.01   0.95  -1.71  -0.49   0.17   0.82    2.0   6000    1.0
    offset[20,3]  -0.08    0.01   0.97  -2.01  -0.73  -0.09   0.56   1.83   6000    1.0
    offset[21,3]  -0.41    0.01   0.98  -2.33  -1.06  -0.42   0.23   1.53   6000    1.0
    offset[22,3]   0.22    0.01   0.97  -1.73  -0.42   0.22   0.88   2.09   6000    1.0
    offset[23,3]  -0.14    0.01   0.99  -2.08  -0.79  -0.13   0.52   1.77   6000    1.0
    offset[24,3]-2.9e-3    0.01    1.0  -1.95  -0.67  -0.02   0.68   1.96   6000    1.0
    offset[25,3]  -0.06    0.01   0.99  -1.99  -0.73  -0.06   0.61   1.91   6000    1.0
    offset[26,3]  -0.12    0.01   0.94  -1.97  -0.75  -0.13   0.51   1.79   6000    1.0
    offset[27,3]  -0.01    0.01   1.02  -2.02  -0.72  -0.01   0.69    2.0   6000    1.0
    offset[28,3] 6.6e-3    0.01   0.97  -1.92  -0.64 1.7e-3   0.64   1.95   6000    1.0
    offset[29,3]   0.14    0.01   0.92  -1.72  -0.45   0.15   0.74   1.97   6000    1.0
    offset[30,3]  -0.02    0.01   0.99  -1.95  -0.69  -0.02   0.63   1.91   6000    1.0
    offset[31,3]   0.42    0.01    1.0  -1.58  -0.26   0.45    1.1   2.32   6000    1.0
    offset[32,3]   0.58    0.01   0.94  -1.36  -0.03   0.63    1.2   2.38   6000    1.0
    offset[33,3]   -0.6    0.01    1.0  -2.48  -1.31  -0.64   0.07   1.43   6000    1.0
    offset[34,3]   0.11    0.01   0.98   -1.8  -0.54   0.12   0.77   2.04   6000    1.0
    offset[35,3]   0.08    0.01   0.96  -1.79  -0.55   0.09   0.73   1.96   6000    1.0
    offset[36,3]  -0.26    0.01   0.94  -2.11  -0.89  -0.27   0.35   1.66   6000    1.0
    offset[37,3]   0.09    0.01   0.98  -1.83  -0.57   0.08   0.76    2.0   6000    1.0
    offset[38,3]   0.07    0.01   0.97   -1.8  -0.58   0.07    0.7   1.98   6000    1.0
    offset[39,3] 3.2e-3    0.01   0.99  -1.97  -0.66  -0.01   0.67   1.97   6000    1.0
    offset[40,3]   0.07    0.01   0.98  -1.84   -0.6   0.06   0.72   1.98   6000    1.0
    offset[41,3]  -0.11    0.01   0.89  -1.84   -0.7  -0.12   0.47    1.7   6000    1.0
    offset[42,3]  -0.21    0.01   0.97  -2.09  -0.87  -0.21   0.45   1.66   6000    1.0
    offset[43,3]    0.1    0.01   0.92  -1.74   -0.5   0.09   0.72    1.9   6000    1.0
    offset[44,3]   0.06    0.01    1.0   -1.9  -0.62   0.05   0.74   2.03   6000    1.0
    offset[45,3]  -0.11    0.01   0.95  -1.96  -0.76  -0.12   0.52   1.79   6000    1.0
    offset[46,3]  -0.22    0.01   0.98  -2.09  -0.89  -0.22   0.44   1.72   6000    1.0
    offset[47,3]  -0.03    0.01   0.99  -1.95  -0.71  -0.02   0.66   1.91   6000    1.0
    offset[48,3]   0.04    0.01   1.01  -1.95  -0.64   0.03   0.72   2.04   6000    1.0
    offset[0,4]    0.22    0.01   0.94  -1.62  -0.42    0.2   0.86   2.08   6000    1.0
    offset[1,4]   -0.17    0.01   0.88   -1.9  -0.75  -0.19    0.4   1.56   6000    1.0
    offset[2,4]   -0.12    0.01   0.91   -1.9  -0.73  -0.14   0.49   1.66   6000    1.0
    offset[3,4]    0.08    0.01   0.82  -1.57  -0.46   0.08   0.62    1.7   6000    1.0
    offset[4,4]   -1.18  7.8e-3   0.61  -2.39  -1.57  -1.15  -0.77  -0.05   6000    1.0
    offset[5,4]   -0.31    0.01   0.84  -1.97  -0.88  -0.31   0.25   1.36   6000    1.0
    offset[6,4]   -0.24    0.01   0.91  -2.02  -0.84  -0.25   0.38   1.56   6000    1.0
    offset[7,4]   -0.33    0.01   0.99  -2.24   -1.0  -0.34   0.32   1.59   6000    1.0
    offset[8,4]   -0.28    0.01   0.96  -2.23  -0.94  -0.28   0.38    1.6   6000    1.0
    offset[9,4]    0.32  8.6e-3   0.67  -1.02   -0.1   0.32   0.75   1.68   6000    1.0
    offset[10,4]  -0.48    0.01    0.8  -2.03  -1.02  -0.48   0.04   1.08   6000    1.0
    offset[11,4]   0.19    0.01   0.93  -1.63  -0.44   0.19   0.85   1.99   6000    1.0
    offset[12,4]  -0.02    0.01   1.03  -2.05  -0.71-8.1e-3   0.67   2.04   6000    1.0
    offset[13,4]-4.6e-3    0.01    1.0   -2.0  -0.68-7.6e-3   0.68   1.94   6000    1.0
    offset[14,4]  -0.97    0.01   0.78  -2.48  -1.49  -0.98  -0.46   0.57   6000    1.0
    offset[15,4]  -0.25    0.01   0.88  -1.95  -0.85  -0.25   0.36   1.48   6000    1.0
    offset[16,4]   0.51    0.01   0.91   -1.3   -0.1   0.52   1.13   2.25   6000    1.0
    offset[17,4]  -0.75    0.01   0.92   -2.5  -1.38  -0.76  -0.13   1.07   6000    1.0
    offset[18,4]   0.61    0.01   0.87  -1.08   0.04   0.62    1.2   2.33   6000    1.0
    offset[19,4]  -0.11    0.01   0.83  -1.75  -0.65  -0.12   0.46    1.5   6000    1.0
    offset[20,4]  -0.29    0.01   0.85   -1.9  -0.86  -0.29   0.31    1.4   6000    1.0
    offset[21,4]    1.2    0.01   0.85  -0.52   0.64   1.22   1.77   2.85   6000    1.0
    offset[22,4]  -0.36    0.01   0.84  -2.03  -0.92  -0.36    0.2   1.29   6000    1.0
    offset[23,4]   0.29    0.01   0.86  -1.39  -0.29   0.31   0.87   1.94   6000    1.0
    offset[24,4]  -0.02    0.01   0.97  -1.94  -0.66  -0.02   0.63   1.87   6000    1.0
    offset[25,4]   0.07    0.01   0.98  -1.84  -0.58   0.07   0.72   2.04   6000    1.0
    offset[26,4]   0.21    0.01   0.78  -1.32   -0.3   0.21   0.73   1.76   6000    1.0
    offset[27,4]   0.01    0.01   0.98  -1.94  -0.62   0.03   0.65   1.94   6000    1.0
    offset[28,4]  -0.02    0.01   0.96  -1.94  -0.66  -0.02   0.63   1.84   6000    1.0
    offset[29,4]   0.49  9.8e-3   0.76  -1.05-2.8e-3   0.49   1.01   1.97   6000    1.0
    offset[30,4]  -0.15    0.01   0.96  -2.02  -0.78  -0.16    0.5   1.75   6000    1.0
    offset[31,4]  -0.13    0.01   0.84  -1.78  -0.69  -0.13   0.44   1.54   6000    1.0
    offset[32,4]   -0.1  8.2e-3   0.64  -1.39  -0.51   -0.1   0.31   1.19   6000    1.0
    offset[33,4]   0.31    0.01    0.8  -1.32  -0.21    0.3   0.84   1.87   6000    1.0
    offset[34,4]    0.4    0.01    0.9  -1.37   -0.2    0.4   0.99   2.18   6000    1.0
    offset[35,4]    0.1    0.01   0.89  -1.61   -0.5    0.1    0.7   1.82   6000    1.0
    offset[36,4]   0.05  9.8e-3   0.76  -1.46  -0.44   0.03   0.55   1.58   6000    1.0
    offset[37,4]  -0.31    0.01   0.93  -2.16  -0.93  -0.33   0.33   1.55   6000    1.0
    offset[38,4]   0.79    0.01   0.92  -1.07   0.18   0.79   1.41   2.59   6000    1.0
    offset[39,4]  -0.14    0.01   1.01  -2.05  -0.85  -0.14   0.54   1.83   6000    1.0
    offset[40,4]   0.21    0.01    0.9  -1.53  -0.39   0.21    0.8   1.99   6000    1.0
    offset[41,4]   1.29  8.8e-3   0.68  -0.05   0.85   1.29   1.73   2.64   6000    1.0
    offset[42,4]  -0.22    0.01   0.93  -2.03  -0.86  -0.24   0.41   1.62   6000    1.0
    offset[43,4]  -0.43    0.01   0.79  -1.96  -0.94  -0.43   0.09   1.19   6000    1.0
    offset[44,4]   0.18    0.01    1.0  -1.74  -0.51   0.19   0.86   2.12   6000    1.0
    offset[45,4]  -0.35    0.01   0.81  -1.93  -0.92  -0.36   0.21   1.23   6000    1.0
    offset[46,4]  -0.39    0.01   0.89  -2.08  -0.99  -0.41   0.22   1.36   6000    1.0
    offset[47,4]   0.17    0.01   0.95  -1.68  -0.47   0.18   0.82   2.01   6000    1.0
    offset[48,4]   0.37    0.01   0.98  -1.51  -0.29   0.37   1.03   2.32   6000    1.0
    eps[0]         2.07  1.8e-3   0.14    1.8   1.97   2.07   2.16   2.35   6000    1.0
    eps[1]         1.72  8.8e-4   0.07   1.59   1.68   1.72   1.77   1.86   6000    1.0
    eps[2]         1.74  1.1e-3   0.09   1.58   1.68   1.74    1.8   1.91   6000    1.0
    eps[3]         1.78  6.5e-4   0.05   1.68   1.75   1.78   1.81   1.88   6000    1.0
    eps[4]         1.85  2.6e-4   0.02   1.81   1.84   1.85   1.86   1.89   6000    1.0
    eps[5]         2.09  7.4e-4   0.06   1.98   2.05   2.09   2.13   2.21   6000    1.0
    eps[6]         1.78  8.2e-4   0.06   1.66   1.74   1.78   1.83    1.9   6000    1.0
    eps[7]         2.23  2.1e-3   0.16   1.91   2.11   2.22   2.34   2.55   6000    1.0
    eps[8]         1.73  1.9e-3   0.15   1.45   1.63   1.73   1.83   2.02   6000    1.0
    eps[9]         1.69  3.7e-4   0.03   1.63   1.67   1.69   1.71   1.75   6000    1.0
    eps[10]        1.91  5.9e-4   0.05   1.82   1.88   1.91   1.94    2.0   6000    1.0
    eps[11]        1.83  1.2e-3   0.09   1.65   1.77   1.83    1.9   2.02   6000    1.0
    eps[12]       -0.37    0.01   0.91  -2.15  -0.98  -0.38   0.24    1.4   6000    1.0
    eps[13]        0.49    0.01   0.89  -1.24  -0.11   0.48   1.06   2.32   6000    1.0
    eps[14]        1.96  5.4e-4   0.04   1.88   1.93   1.96   1.99   2.04   6000    1.0
    eps[15]        1.71  8.7e-4   0.07   1.58   1.67   1.71   1.76   1.84   6000    1.0
    eps[16]         2.0  1.0e-3   0.08   1.85   1.95    2.0   2.06   2.16   6000    1.0
    eps[17]        1.87  1.1e-3   0.08   1.71   1.82   1.87   1.93   2.04   6000    1.0
    eps[18]        1.78  8.8e-4   0.07   1.64   1.73   1.78   1.82   1.91   6000    1.0
    eps[19]        1.77  6.6e-4   0.05   1.67   1.73   1.77   1.81   1.87   6000    1.0
    eps[20]        1.78  6.5e-4   0.05   1.68   1.74   1.78   1.81   1.88   6000    1.0
    eps[21]        1.79  6.3e-4   0.05    1.7   1.76   1.79   1.82   1.89   6000    1.0
    eps[22]        1.91  7.8e-4   0.06   1.79   1.87   1.91   1.95   2.03   6000    1.0
    eps[23]        1.84  8.0e-4   0.06   1.72    1.8   1.84   1.89   1.97   6000    1.0
    eps[24]        0.31    0.01   0.79  -1.18  -0.24   0.31   0.84   1.86   6000    1.0
    eps[25]        2.14  1.9e-3   0.15   1.86   2.04   2.14   2.25   2.44   6000    1.0
    eps[26]        1.78  5.8e-4   0.04   1.69   1.75   1.78   1.81   1.87   6000    1.0
    eps[27]        -0.3    0.01   0.92  -2.17   -0.9  -0.29   0.32   1.46   6000    1.0
    eps[28]        2.26  1.7e-3   0.13   2.01   2.17   2.25   2.34   2.51   6000    1.0
    eps[29]        1.61  4.9e-4   0.04   1.54   1.59   1.62   1.64   1.69   6000    1.0
    eps[30]         1.8  1.3e-3    0.1    1.6   1.73    1.8   1.87    2.0   6000    1.0
    eps[31]        1.66  7.6e-4   0.06   1.55   1.62   1.66    1.7   1.78   6000    1.0
    eps[32]        1.71  3.4e-4   0.03   1.66   1.69   1.71   1.73   1.76   6000    1.0
    eps[33]        1.83  5.9e-4   0.05   1.74    1.8   1.83   1.86   1.92   6000    1.0
    eps[34]        1.77  1.0e-3   0.08   1.62   1.72   1.77   1.83   1.93   6000    1.0
    eps[35]        1.98  9.0e-4   0.07   1.84   1.93   1.98   2.02   2.11   6000    1.0
    eps[36]        1.81  5.5e-4   0.04   1.73   1.79   1.81   1.84    1.9   6000    1.0
    eps[37]        1.71  1.5e-3   0.11    1.5   1.64   1.71   1.79   1.94   6000    1.0
    eps[38]        2.02  1.0e-3   0.08   1.87   1.97   2.02   2.07   2.18   6000    1.0
    eps[39]        1.88  2.1e-3   0.16   1.57   1.77   1.87   1.98   2.21   6000    1.0
    eps[40]        1.63  9.0e-4   0.07   1.49   1.58   1.63   1.68   1.77   6000    1.0
    eps[41]        1.93  4.0e-4   0.03   1.88   1.91   1.93   1.96    2.0   6000    1.0
    eps[42]        1.85  1.1e-3   0.09   1.69    1.8   1.85   1.91   2.02   6000    1.0
    eps[43]        1.71  5.7e-4   0.04   1.63   1.68   1.71   1.74    1.8   6000    1.0
    eps[44]        1.94  2.5e-3   0.19   1.58   1.81   1.94   2.07   2.31   6000    1.0
    eps[45]        1.93  6.7e-4   0.05   1.83   1.89   1.93   1.96   2.03   6000    1.0
    eps[46]        1.97  9.5e-4   0.07   1.84   1.93   1.97   2.02   2.12   6000    1.0
    eps[47]        2.18  1.6e-3   0.12   1.95   2.09   2.18   2.26   2.43   6000    1.0
    eps[48]        2.04  2.0e-3   0.16   1.74   1.93   2.04   2.14   2.35   6000    1.0
    theta[0,0]    -0.43  4.7e-4   0.04   -0.5  -0.45  -0.43  -0.41  -0.36   6000    1.0
    theta[1,0]    -0.43  4.5e-4   0.03   -0.5  -0.45  -0.43  -0.41  -0.36   6000    1.0
    theta[2,0]    -0.43  4.8e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.36   6000    1.0
    theta[3,0]    -0.43  4.3e-4   0.03  -0.49  -0.45  -0.43   -0.4  -0.36   6000    1.0
    theta[4,0]    -0.44  3.9e-4   0.03  -0.49  -0.45  -0.44  -0.41  -0.38   6000    1.0
    theta[5,0]    -0.42  4.5e-4   0.04  -0.49  -0.44  -0.42   -0.4  -0.35   6000    1.0
    theta[6,0]    -0.42  4.5e-4   0.03  -0.49  -0.44  -0.42   -0.4  -0.35   6000    1.0
    theta[7,0]    -0.43  4.8e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.35   6000    1.0
    theta[8,0]    -0.43  4.8e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.36   6000    1.0
    theta[9,0]    -0.41  4.2e-4   0.03  -0.47  -0.43  -0.41  -0.39  -0.34   6000    1.0
    theta[10,0]   -0.43  4.4e-4   0.03  -0.51  -0.46  -0.43  -0.41  -0.37   6000    1.0
    theta[11,0]   -0.44  4.9e-4   0.04  -0.52  -0.46  -0.44  -0.41  -0.37   6000    1.0
    theta[12,0]   -0.43  4.9e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.35   6000    1.0
    theta[13,0]   -0.43  4.9e-4   0.04  -0.51  -0.45  -0.43   -0.4  -0.35   6000    1.0
    theta[14,0]   -0.41  4.5e-4   0.03  -0.48  -0.44  -0.41  -0.39  -0.34   6000    1.0
    theta[15,0]   -0.44  4.8e-4   0.04  -0.52  -0.46  -0.44  -0.41  -0.37   6000    1.0
    theta[16,0]   -0.43  4.7e-4   0.04   -0.5  -0.45  -0.43  -0.41  -0.36   6000    1.0
    theta[17,0]   -0.43  4.6e-4   0.04   -0.5  -0.45  -0.43  -0.41  -0.36   6000    1.0
    theta[18,0]   -0.43  4.7e-4   0.04   -0.5  -0.45  -0.43  -0.41  -0.36   6000    1.0
    theta[19,0]   -0.42  4.3e-4   0.03  -0.49  -0.45  -0.42   -0.4  -0.36   6000    1.0
    theta[20,0]   -0.43  4.4e-4   0.03   -0.5  -0.45  -0.43  -0.41  -0.37   6000    1.0
    theta[21,0]   -0.44  4.7e-4   0.04  -0.52  -0.46  -0.44  -0.42  -0.38   6000    1.0
    theta[22,0]   -0.42  4.6e-4   0.04  -0.48  -0.44  -0.42  -0.39  -0.34   6000    1.0
    theta[23,0]   -0.44  4.7e-4   0.04  -0.52  -0.46  -0.44  -0.41  -0.37   6000    1.0
    theta[24,0]   -0.43  4.9e-4   0.04  -0.51  -0.45  -0.43  -0.41  -0.36   6000    1.0
    theta[25,0]   -0.43  4.7e-4   0.04   -0.5  -0.45  -0.43  -0.41  -0.36   6000    1.0
    theta[26,0]   -0.42  4.3e-4   0.03  -0.49  -0.45  -0.42   -0.4  -0.36   6000    1.0
    theta[27,0]   -0.43  4.9e-4   0.04  -0.51  -0.45  -0.43   -0.4  -0.36   6000    1.0
    theta[28,0]   -0.43  4.7e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.36   6000    1.0
    theta[29,0]   -0.42  4.2e-4   0.03  -0.49  -0.44  -0.42   -0.4  -0.36   6000    1.0
    theta[30,0]   -0.43  4.7e-4   0.04   -0.5  -0.45  -0.43  -0.41  -0.36   6000    1.0
    theta[31,0]   -0.41  4.8e-4   0.04  -0.48  -0.44  -0.41  -0.39  -0.33   6000    1.0
    theta[32,0]   -0.41  4.2e-4   0.03  -0.47  -0.43  -0.41  -0.39  -0.35   6000    1.0
    theta[33,0]   -0.44  4.7e-4   0.04  -0.52  -0.47  -0.44  -0.42  -0.38   6000    1.0
    theta[34,0]   -0.42  4.8e-4   0.04  -0.49  -0.44  -0.42   -0.4  -0.34   6000    1.0
    theta[35,0]   -0.42  4.6e-4   0.04  -0.49  -0.45  -0.42   -0.4  -0.35   6000    1.0
    theta[36,0]   -0.45  4.9e-4   0.04  -0.53  -0.47  -0.44  -0.42  -0.38   6000    1.0
    theta[37,0]   -0.43  4.8e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.35   6000    1.0
    theta[38,0]   -0.42  4.6e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.35   6000    1.0
    theta[39,0]   -0.42  4.8e-4   0.04   -0.5  -0.45  -0.42   -0.4  -0.35   6000    1.0
    theta[40,0]   -0.43  4.6e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.36   6000    1.0
    theta[41,0]   -0.43  4.2e-4   0.03   -0.5  -0.45  -0.43  -0.41  -0.37   6000    1.0
    theta[42,0]   -0.43  4.8e-4   0.04  -0.51  -0.46  -0.43  -0.41  -0.36   6000    1.0
    theta[43,0]   -0.44  4.4e-4   0.03  -0.51  -0.46  -0.43  -0.41  -0.37   6000    1.0
    theta[44,0]   -0.43  4.8e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.35   6000    1.0
    theta[45,0]   -0.43  4.5e-4   0.03  -0.51  -0.46  -0.43  -0.41  -0.37   6000    1.0
    theta[46,0]   -0.44  4.8e-4   0.04  -0.52  -0.46  -0.44  -0.41  -0.37   6000    1.0
    theta[47,0]   -0.43  4.7e-4   0.04  -0.51  -0.45  -0.43  -0.41  -0.36   6000    1.0
    theta[48,0]   -0.43  4.9e-4   0.04   -0.5  -0.45  -0.43   -0.4  -0.35   6000    1.0
    theta[0,1]      0.3  3.8e-4   0.03   0.24   0.28    0.3   0.32   0.37   6000    1.0
    theta[1,1]      0.3  3.6e-4   0.03   0.25   0.29    0.3   0.32   0.37   6000    1.0
    theta[2,1]      0.3  3.5e-4   0.03   0.25   0.29    0.3   0.32   0.37   6000    1.0
    theta[3,1]     0.32  3.9e-4   0.03   0.27    0.3   0.31   0.33   0.39   6000    1.0
    theta[4,1]     0.29  2.2e-4   0.02   0.26   0.28   0.29    0.3   0.32   6000    1.0
    theta[5,1]     0.33  8.1e-4   0.04   0.28    0.3   0.32   0.36   0.43   2397    1.0
    theta[6,1]      0.3  3.4e-4   0.03   0.25   0.29    0.3   0.31   0.36   6000    1.0
    theta[7,1]     0.31  4.0e-4   0.03   0.25   0.29    0.3   0.32   0.38   6000    1.0
    theta[8,1]     0.31  4.0e-4   0.03   0.25   0.29    0.3   0.32   0.38   6000    1.0
    theta[9,1]     0.29  2.7e-4   0.02   0.24   0.28   0.29    0.3   0.33   6000    1.0
    theta[10,1]     0.3  3.1e-4   0.02   0.26   0.29    0.3   0.32   0.36   6000    1.0
    theta[11,1]    0.29  3.7e-4   0.03   0.23   0.28   0.29   0.31   0.35   6000    1.0
    theta[12,1]     0.3  3.8e-4   0.03   0.24   0.28    0.3   0.31   0.36   6000    1.0
    theta[13,1]     0.3  4.0e-4   0.03   0.24   0.28    0.3   0.31   0.37   6000    1.0
    theta[14,1]     0.3  3.0e-4   0.02   0.25   0.29    0.3   0.31   0.35   6000    1.0
    theta[15,1]     0.3  3.6e-4   0.03   0.25   0.29    0.3   0.32   0.36   6000    1.0
    theta[16,1]    0.29  3.7e-4   0.03   0.23   0.28   0.29   0.31   0.35   6000    1.0
    theta[17,1]     0.3  3.6e-4   0.03   0.24   0.28    0.3   0.31   0.36   6000    1.0
    theta[18,1]     0.3  3.5e-4   0.03   0.25   0.29    0.3   0.32   0.36   6000    1.0
    theta[19,1]    0.31  3.7e-4   0.03   0.27   0.29   0.31   0.33   0.38   6000    1.0
    theta[20,1]     0.3  3.2e-4   0.02   0.24   0.28    0.3   0.31   0.35   6000    1.0
    theta[21,1]     0.3  3.2e-4   0.02   0.25   0.29    0.3   0.31   0.36   6000    1.0
    theta[22,1]     0.3  3.4e-4   0.03   0.25   0.29    0.3   0.32   0.36   6000    1.0
    theta[23,1]     0.3  3.4e-4   0.03   0.25   0.29    0.3   0.32   0.36   6000    1.0
    theta[24,1]     0.3  4.0e-4   0.03   0.24   0.28    0.3   0.31   0.37   6000    1.0
    theta[25,1]    0.29  3.9e-4   0.03   0.22   0.28   0.29   0.31   0.35   6000    1.0
    theta[26,1]     0.3  3.2e-4   0.02   0.26   0.29    0.3   0.32   0.36   6000    1.0
    theta[27,1]     0.3  3.9e-4   0.03   0.24   0.28    0.3   0.31   0.37   6000    1.0
    theta[28,1]    0.31  4.1e-4   0.03   0.26   0.29    0.3   0.32   0.39   6000    1.0
    theta[29,1]    0.29  2.9e-4   0.02   0.24   0.28   0.29    0.3   0.33   6000    1.0
    theta[30,1]     0.3  3.7e-4   0.03   0.25   0.29    0.3   0.32   0.37   6000    1.0
    theta[31,1]     0.3  3.5e-4   0.03   0.25   0.29    0.3   0.32   0.37   6000    1.0
    theta[32,1]    0.29  2.6e-4   0.02   0.25   0.28   0.29    0.3   0.32   6000    1.0
    theta[33,1]     0.3  3.1e-4   0.02   0.26   0.29    0.3   0.32   0.36   6000    1.0
    theta[34,1]    0.28  4.0e-4   0.03   0.21   0.27   0.29    0.3   0.33   6000    1.0
    theta[35,1]    0.31  3.8e-4   0.03   0.26   0.29   0.31   0.32   0.38   6000    1.0
    theta[36,1]    0.29  3.1e-4   0.02   0.24   0.28   0.29   0.31   0.34   6000    1.0
    theta[37,1]     0.3  3.8e-4   0.03   0.25   0.29    0.3   0.32   0.37   6000    1.0
    theta[38,1]    0.29  3.6e-4   0.03   0.23   0.28    0.3   0.31   0.35   6000    1.0
    theta[39,1]     0.3  3.8e-4   0.03   0.23   0.28    0.3   0.31   0.35   6000    1.0
    theta[40,1]    0.29  3.6e-4   0.03   0.23   0.28   0.29   0.31   0.35   6000    1.0
    theta[41,1]    0.28  3.1e-4   0.02   0.22   0.26   0.28    0.3   0.32   6000    1.0
    theta[42,1]     0.3  3.6e-4   0.03   0.24   0.28    0.3   0.31   0.36   6000    1.0
    theta[43,1]    0.31  3.2e-4   0.03   0.27   0.29    0.3   0.32   0.37   6000    1.0
    theta[44,1]     0.3  4.0e-4   0.03   0.24   0.28    0.3   0.31   0.37   6000    1.0
    theta[45,1]     0.3  3.2e-4   0.02   0.24   0.28    0.3   0.31   0.35   6000    1.0
    theta[46,1]     0.3  3.4e-4   0.03   0.25   0.29    0.3   0.31   0.36   6000    1.0
    theta[47,1]    0.29  3.9e-4   0.03   0.22   0.27   0.29   0.31   0.35   6000    1.0
    theta[48,1]    0.29  3.8e-4   0.03   0.23   0.28   0.29   0.31   0.35   6000    1.0
    theta[0,2]    -0.25  4.3e-4   0.03  -0.32  -0.27  -0.25  -0.23  -0.18   6000    1.0
    theta[1,2]    -0.26  3.8e-4   0.03  -0.32  -0.27  -0.26  -0.24   -0.2   6000    1.0
    theta[2,2]    -0.26  4.1e-4   0.03  -0.33  -0.28  -0.26  -0.24   -0.2   6000    1.0
    theta[3,2]    -0.26  3.6e-4   0.03  -0.32  -0.28  -0.26  -0.25  -0.21   6000    1.0
    theta[4,2]    -0.24  2.4e-4   0.02  -0.27  -0.25  -0.24  -0.22   -0.2   6000    1.0
    theta[5,2]    -0.23  4.3e-4   0.03  -0.28  -0.25  -0.23  -0.21  -0.15   6000    1.0
    theta[6,2]    -0.26  3.7e-4   0.03  -0.33  -0.28  -0.26  -0.24  -0.21   6000    1.0
    theta[7,2]    -0.25  4.3e-4   0.03  -0.32  -0.27  -0.25  -0.23  -0.18   6000    1.0
    theta[8,2]    -0.25  4.3e-4   0.03  -0.32  -0.27  -0.25  -0.24  -0.18   6000    1.0
    theta[9,2]    -0.24  2.8e-4   0.02  -0.28  -0.26  -0.24  -0.23  -0.19   6000    1.0
    theta[10,2]   -0.26  3.4e-4   0.03  -0.31  -0.27  -0.26  -0.24  -0.21   6000    1.0
    theta[11,2]   -0.26  4.0e-4   0.03  -0.33  -0.28  -0.26  -0.24  -0.21   6000    1.0
    theta[12,2]   -0.26  4.4e-4   0.03  -0.33  -0.28  -0.26  -0.24  -0.19   6000    1.0
    theta[13,2]   -0.26  4.4e-4   0.03  -0.33  -0.28  -0.26  -0.24  -0.19   6000    1.0
    theta[14,2]   -0.24  3.3e-4   0.03  -0.29  -0.26  -0.25  -0.23  -0.19   6000    1.0
    theta[15,2]   -0.26  3.9e-4   0.03  -0.33  -0.28  -0.26  -0.24  -0.21   6000    1.0
    theta[16,2]   -0.25  4.0e-4   0.03  -0.31  -0.27  -0.25  -0.23  -0.18   6000    1.0
    theta[17,2]   -0.27  4.1e-4   0.03  -0.34  -0.29  -0.26  -0.25  -0.21   6000    1.0
    theta[18,2]   -0.27  4.0e-4   0.03  -0.34  -0.28  -0.26  -0.25  -0.21   6000    1.0
    theta[19,2]   -0.25  3.9e-4   0.03  -0.31  -0.27  -0.25  -0.23  -0.18   6000    1.0
    theta[20,2]   -0.27  3.6e-4   0.03  -0.33  -0.28  -0.26  -0.25  -0.21   6000    1.0
    theta[21,2]   -0.26  3.5e-4   0.03  -0.32  -0.28  -0.26  -0.24  -0.21   6000    1.0
    theta[22,2]   -0.26  3.7e-4   0.03  -0.32  -0.28  -0.26  -0.24  -0.21   6000    1.0
    theta[23,2]   -0.25  3.6e-4   0.03  -0.31  -0.27  -0.25  -0.24   -0.2   6000    1.0
    theta[24,2]   -0.26  4.4e-4   0.03  -0.33  -0.28  -0.26  -0.24  -0.19   6000    1.0
    theta[25,2]   -0.26  4.4e-4   0.03  -0.34  -0.28  -0.26  -0.25   -0.2   6000    1.0
    theta[26,2]   -0.27  3.6e-4   0.03  -0.34  -0.29  -0.27  -0.25  -0.23   6000    1.0
    theta[27,2]   -0.26  4.4e-4   0.03  -0.33  -0.27  -0.26  -0.24  -0.19   6000    1.0
    theta[28,2]   -0.24  4.4e-4   0.03  -0.31  -0.26  -0.25  -0.23  -0.16   6000    1.0
    theta[29,2]   -0.26  3.1e-4   0.02  -0.31  -0.27  -0.26  -0.24  -0.21   6000    1.0
    theta[30,2]   -0.26  4.2e-4   0.03  -0.33  -0.28  -0.26  -0.24  -0.19   6000    1.0
    theta[31,2]   -0.24  3.8e-4   0.03  -0.29  -0.26  -0.25  -0.23  -0.18   6000    1.0
    theta[32,2]   -0.28  2.9e-4   0.02  -0.32  -0.29  -0.27  -0.26  -0.24   6000    1.0
    theta[33,2]   -0.26  3.3e-4   0.03  -0.32  -0.28  -0.26  -0.25  -0.21   6000    1.0
    theta[34,2]   -0.26  3.9e-4   0.03  -0.33  -0.28  -0.26  -0.24  -0.21   6000    1.0
    theta[35,2]   -0.23  4.6e-4   0.04  -0.28  -0.25  -0.23  -0.21  -0.14   6000    1.0
    theta[36,2]   -0.29  5.1e-4   0.03  -0.36  -0.31  -0.28  -0.26  -0.24   3814    1.0
    theta[37,2]   -0.24  4.4e-4   0.03   -0.3  -0.26  -0.25  -0.22  -0.16   6000    1.0
    theta[38,2]   -0.27  4.2e-4   0.03  -0.35  -0.29  -0.27  -0.25  -0.22   6000    1.0
    theta[39,2]   -0.26  4.3e-4   0.03  -0.34  -0.28  -0.26  -0.24   -0.2   6000    1.0
    theta[40,2]   -0.26  3.8e-4   0.03  -0.32  -0.28  -0.26  -0.24   -0.2   6000    1.0
    theta[41,2]   -0.24  2.8e-4   0.02  -0.28  -0.26  -0.25  -0.23   -0.2   6000    1.0
    theta[42,2]   -0.27  4.4e-4   0.03  -0.35  -0.29  -0.27  -0.25  -0.22   6000    1.0
    theta[43,2]   -0.25  3.4e-4   0.03  -0.31  -0.27  -0.25  -0.24   -0.2   6000    1.0
    theta[44,2]   -0.26  4.4e-4   0.03  -0.33  -0.27  -0.26  -0.24  -0.19   6000    1.0
    theta[45,2]   -0.25  3.5e-4   0.03  -0.31  -0.27  -0.25  -0.24   -0.2   6000    1.0
    theta[46,2]   -0.27  3.9e-4   0.03  -0.33  -0.28  -0.26  -0.25  -0.21   6000    1.0
    theta[47,2]   -0.27  4.5e-4   0.03  -0.35  -0.29  -0.27  -0.25  -0.21   6000    1.0
    theta[48,2]   -0.27  4.4e-4   0.03  -0.34  -0.28  -0.26  -0.25   -0.2   6000    1.0
    theta[0,3]     -0.2  3.7e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[1,3]     -0.2  3.5e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.15   6000    1.0
    theta[2,3]     -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[3,3]     -0.2  3.4e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.15   6000    1.0
    theta[4,3]    -0.21  3.2e-4   0.02  -0.25  -0.22  -0.21  -0.19  -0.16   6000    1.0
    theta[5,3]    -0.19  3.7e-4   0.03  -0.25  -0.21   -0.2  -0.18  -0.13   6000    1.0
    theta[6,3]     -0.2  3.6e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[7,3]     -0.2  3.7e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[8,3]     -0.2  3.7e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[9,3]     -0.2  3.3e-4   0.03  -0.25  -0.21   -0.2  -0.18  -0.15   6000    1.0
    theta[10,3]   -0.21  3.5e-4   0.03  -0.26  -0.22  -0.21  -0.19  -0.16   6000    1.0
    theta[11,3]   -0.21  3.7e-4   0.03  -0.27  -0.22  -0.21  -0.19  -0.15   6000    1.0
    theta[12,3]    -0.2  3.7e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[13,3]    -0.2  3.7e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[14,3]   -0.19  3.5e-4   0.03  -0.24  -0.21  -0.19  -0.18  -0.14   6000    1.0
    theta[15,3]    -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.19  -0.15   6000    1.0
    theta[16,3]    -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.15   6000    1.0
    theta[17,3]    -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.15   6000    1.0
    theta[18,3]    -0.2  3.6e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[19,3]    -0.2  3.5e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[20,3]    -0.2  3.5e-4   0.03  -0.26  -0.22   -0.2  -0.19  -0.15   6000    1.0
    theta[21,3]   -0.21  3.7e-4   0.03  -0.27  -0.23  -0.21  -0.19  -0.16   6000    1.0
    theta[22,3]    -0.2  3.5e-4   0.03  -0.25  -0.21   -0.2  -0.18  -0.14   6000    1.0
    theta[23,3]    -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.19  -0.15   6000    1.0
    theta[24,3]    -0.2  3.7e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[25,3]    -0.2  3.7e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.15   6000    1.0
    theta[26,3]    -0.2  3.5e-4   0.03  -0.26  -0.22   -0.2  -0.19  -0.15   6000    1.0
    theta[27,3]    -0.2  3.7e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[28,3]    -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[29,3]    -0.2  3.4e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[30,3]    -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.15   6000    1.0
    theta[31,3]   -0.19  3.8e-4   0.03  -0.24  -0.21  -0.19  -0.17  -0.13   6000    1.0
    theta[32,3]   -0.19  3.5e-4   0.03  -0.24  -0.21  -0.19  -0.17  -0.13   6000    1.0
    theta[33,3]   -0.21  3.7e-4   0.03  -0.28  -0.23  -0.21  -0.19  -0.16   6000    1.0
    theta[34,3]    -0.2  3.6e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[35,3]    -0.2  3.5e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[36,3]   -0.21  3.5e-4   0.03  -0.26  -0.22  -0.21  -0.19  -0.15   6000    1.0
    theta[37,3]    -0.2  3.6e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[38,3]    -0.2  3.6e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[39,3]    -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[40,3]    -0.2  3.5e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[41,3]    -0.2  3.2e-4   0.03  -0.25  -0.22   -0.2  -0.19  -0.16   6000    1.0
    theta[42,3]   -0.21  3.7e-4   0.03  -0.26  -0.22   -0.2  -0.19  -0.15   6000    1.0
    theta[43,3]    -0.2  3.4e-4   0.03  -0.25  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[44,3]    -0.2  3.7e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[45,3]    -0.2  3.4e-4   0.03  -0.26  -0.22   -0.2  -0.19  -0.15   6000    1.0
    theta[46,3]   -0.21  3.7e-4   0.03  -0.26  -0.22   -0.2  -0.19  -0.15   6000    1.0
    theta[47,3]    -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[48,3]    -0.2  3.6e-4   0.03  -0.26  -0.22   -0.2  -0.18  -0.14   6000    1.0
    theta[0,4]    -0.09  4.8e-4   0.04  -0.16  -0.11  -0.09  -0.07-9.9e-3   6000    1.0
    theta[1,4]     -0.1  4.3e-4   0.03  -0.17  -0.12   -0.1  -0.08  -0.04   6000    1.0
    theta[2,4]     -0.1  4.5e-4   0.03  -0.17  -0.12   -0.1  -0.08  -0.04   6000    1.0
    theta[3,4]     -0.1  3.9e-4   0.03  -0.15  -0.11   -0.1  -0.08  -0.04   6000    1.0
    theta[4,4]    -0.14  2.4e-4   0.02  -0.18  -0.15  -0.14  -0.13   -0.1   6000    1.0
    theta[5,4]    -0.11  4.0e-4   0.03  -0.17  -0.13  -0.11  -0.09  -0.05   6000    1.0
    theta[6,4]    -0.11  4.4e-4   0.03  -0.18  -0.13  -0.11  -0.09  -0.04   6000    1.0
    theta[7,4]    -0.11  5.0e-4   0.04  -0.19  -0.13  -0.11  -0.09  -0.04   6000    1.0
    theta[8,4]    -0.11  4.9e-4   0.04  -0.19  -0.13  -0.11  -0.09  -0.04   6000    1.0
    theta[9,4]    -0.09  2.8e-4   0.02  -0.13   -0.1  -0.09  -0.07  -0.04   6000    1.0
    theta[10,4]   -0.12  3.7e-4   0.03  -0.18  -0.13  -0.11   -0.1  -0.06   6000    1.0
    theta[11,4]   -0.09  4.5e-4   0.04  -0.16  -0.11  -0.09  -0.07  -0.01   6000    1.0
    theta[12,4]    -0.1  5.2e-4   0.04  -0.18  -0.12   -0.1  -0.07  -0.02   6000    1.0
    theta[13,4]    -0.1  5.2e-4   0.04  -0.18  -0.12   -0.1  -0.07  -0.02   6000    1.0
    theta[14,4]   -0.13  3.9e-4   0.03   -0.2  -0.15  -0.13  -0.11  -0.08   6000    1.0
    theta[15,4]   -0.11  4.3e-4   0.03  -0.18  -0.13  -0.11  -0.09  -0.04   6000    1.0
    theta[16,4]   -0.08  4.6e-4   0.04  -0.14   -0.1  -0.08  -0.06-3.2e-3   6000    1.0
    theta[17,4]   -0.13  4.8e-4   0.04  -0.21  -0.15  -0.12   -0.1  -0.06   6000    1.0
    theta[18,4]   -0.07  4.4e-4   0.03  -0.14   -0.1  -0.08  -0.05-2.7e-3   6000    1.0
    theta[19,4]    -0.1  3.9e-4   0.03  -0.16  -0.12   -0.1  -0.08  -0.04   6000    1.0
    theta[20,4]   -0.11  4.0e-4   0.03  -0.17  -0.13  -0.11  -0.09  -0.05   6000    1.0
    theta[21,4]   -0.05  4.5e-4   0.04  -0.11  -0.08  -0.06  -0.03   0.02   6000    1.0
    theta[22,4]   -0.11  4.0e-4   0.03  -0.18  -0.13  -0.11  -0.09  -0.05   6000    1.0
    theta[23,4]   -0.09  4.2e-4   0.03  -0.15  -0.11  -0.09  -0.07  -0.02   6000    1.0
    theta[24,4]    -0.1  4.9e-4   0.04  -0.17  -0.12   -0.1  -0.08  -0.02   6000    1.0
    theta[25,4]    -0.1  4.9e-4   0.04  -0.17  -0.12   -0.1  -0.07  -0.02   6000    1.0
    theta[26,4]   -0.09  3.6e-4   0.03  -0.14  -0.11  -0.09  -0.07  -0.03   6000    1.0
    theta[27,4]    -0.1  4.9e-4   0.04  -0.18  -0.12   -0.1  -0.08  -0.02   6000    1.0
    theta[28,4]    -0.1  4.8e-4   0.04  -0.17  -0.12   -0.1  -0.08  -0.02   6000    1.0
    theta[29,4]   -0.08  3.5e-4   0.03  -0.13   -0.1  -0.08  -0.06  -0.02   6000    1.0
    theta[30,4]    -0.1  4.8e-4   0.04  -0.18  -0.13   -0.1  -0.08  -0.03   6000    1.0
    theta[31,4]    -0.1  4.0e-4   0.03  -0.17  -0.12   -0.1  -0.08  -0.04   6000    1.0
    theta[32,4]    -0.1  2.6e-4   0.02  -0.14  -0.12   -0.1  -0.09  -0.06   6000    1.0
    theta[33,4]   -0.09  3.7e-4   0.03  -0.14  -0.11  -0.09  -0.07  -0.03   6000    1.0
    theta[34,4]   -0.08  4.5e-4   0.03  -0.15  -0.11  -0.09  -0.06-9.4e-3   6000    1.0
    theta[35,4]   -0.09  4.3e-4   0.03  -0.16  -0.12   -0.1  -0.07  -0.03   6000    1.0
    theta[36,4]    -0.1  3.4e-4   0.03  -0.15  -0.11   -0.1  -0.08  -0.04   6000    1.0
    theta[37,4]   -0.11  4.7e-4   0.04  -0.19  -0.13  -0.11  -0.09  -0.04   6000    1.0
    theta[38,4]   -0.07  4.8e-4   0.04  -0.13  -0.09  -0.07  -0.04   0.01   6000    1.0
    theta[39,4]    -0.1  5.0e-4   0.04  -0.18  -0.13   -0.1  -0.08  -0.02   6000    1.0
    theta[40,4]   -0.09  4.4e-4   0.03  -0.16  -0.11  -0.09  -0.07  -0.02   6000    1.0
    theta[41,4]   -0.05  3.3e-4   0.03   -0.1  -0.07  -0.05  -0.04-9.1e-5   6000    1.0
    theta[42,4]   -0.11  4.5e-4   0.04  -0.18  -0.13  -0.11  -0.08  -0.04   6000    1.0
    theta[43,4]   -0.11  3.6e-4   0.03  -0.17  -0.13  -0.11  -0.09  -0.06   6000    1.0
    theta[44,4]   -0.09  5.1e-4   0.04  -0.17  -0.12  -0.09  -0.07  -0.01   6000    1.0
    theta[45,4]   -0.11  3.9e-4   0.03  -0.17  -0.13  -0.11  -0.09  -0.05   6000    1.0
    theta[46,4]   -0.11  4.4e-4   0.03  -0.18  -0.13  -0.11  -0.09  -0.05   6000    1.0
    theta[47,4]   -0.09  4.7e-4   0.04  -0.16  -0.11  -0.09  -0.07  -0.01   6000    1.0
    theta[48,4]   -0.08  5.0e-4   0.04  -0.15  -0.11  -0.09  -0.06 1.9e-4   6000    1.0
    lp__         -5.8e4    0.38  15.07 -5.8e4 -5.8e4 -5.8e4 -5.8e4 -5.8e4   1590    1.0
    
    Samples were drawn using NUTS at Wed May 22 18:22:17 2019.
    For each parameter, n_eff is a crude measure of effective sample size,
    and Rhat is the potential scale reduction factor on split chains (at 
    convergence, Rhat=1).


### Assessment of Convergence
We use the Arviz library again to give a brief assessment of convergence of the MCMC method. Refer back to the previous [post](https://opendatagroup.github.io/data%20science/2019/01/24/introduction-to-bayesian-modeling.html) for an interpretation of the metrics below. We seem to be in good shape.


```python
inf_data = az.convert_to_inference_data(fit)
```


```python
az.plot_energy(inf_data)
```




    <matplotlib.axes._subplots.AxesSubplot at 0x7f86044180b8>




![png](output_49_1.png)



```python
az.rhat(inf_data).max()
```




    <xarray.Dataset>
    Dimensions:  ()
    Data variables:
        mu       float64 1.0
        sigma    float64 1.0
        offset   float64 1.0
        eps      float64 1.0
        theta    float64 1.0



### Prediction
If you have read the first post in this series, you may have noticed that we are using an unbalanced training set. Our approach to prediction is going to be slightly different in this post. Our approach here will be to use random number generation and the posteriors generated by the MCMC to generate synthetic outcomes for each sample. Notice the similarity of our scoring code to the Stan model definition above.   


```python
#This dictionary allows us to move from 3-tensors to a dictionary of 2-tensors for each state.
state_translate = dict(list(zip(train.addr_state_codes.unique()-1, train.addr_state.unique())))
```


```python
#Extracts the samples from the fit object.
samples = fit.extract()
```


```python
theta = samples['theta']
```


```python
theta.shape
```




    (6000, 49, 5)




```python
theta_state = {}
for j in range(49):
    theta_state[state_translate[j]] = theta[:,j,:]
```


```python
theta_state['AK'].shape
```




    (6000, 5)




```python
eps = samples['eps']
```


```python
eps.shape
```




    (6000, 49)




```python
eps_state = {}
for j in range(49):
    eps_state[state_translate[j]] = eps[:,j]
```


```python
#Here we are using the same "model" as in the Stan code above to generate so-called synthetic outcomes for each
#sample in our posterior. E.g. each sample is randomly assigned an outcome according to 
#y ~ bernoulli(inv_logit(x.theta + eps))
outcomes = {}
for j in range(49):
    s = state_translate[j]
    vals = test.loc[test.addr_state==s].loc[:,trans_features].values
    outcomes[s] = np.dot(theta_state[s], np.transpose(vals)) + np.repeat(eps_state[s].reshape(-1,1), vals.shape[0], axis=1)
    outcomes[s] = scipy.special.expit(outcomes[s])
    outcomes[s] = bernoulli.rvs(p=outcomes[s], size=outcomes[s].shape, random_state=SEED)
```


```python
means = {}
for j in range(49):
    means[state_translate[j]] = outcomes[state_translate[j]].sum(axis=0).mean()/6000
```

    /home/ubuntu/anaconda3/lib/python3.6/site-packages/ipykernel_launcher.py:3: RuntimeWarning: Mean of empty slice.
      This is separate from the ipykernel package so we can avoid doing imports until
    /home/ubuntu/anaconda3/lib/python3.6/site-packages/numpy/core/_methods.py:85: RuntimeWarning: invalid value encountered in double_scalars
      ret = ret.dtype.type(ret / rcount)



```python
#Here we have a bulk mean behavior of outcomes for each state.
pd.DataFrame.from_dict(means, orient='index')
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>AK</th>
      <td>0.860305</td>
    </tr>
    <tr>
      <th>AL</th>
      <td>0.810346</td>
    </tr>
    <tr>
      <th>AR</th>
      <td>0.819547</td>
    </tr>
    <tr>
      <th>AZ</th>
      <td>0.831808</td>
    </tr>
    <tr>
      <th>CA</th>
      <td>0.848516</td>
    </tr>
    <tr>
      <th>CO</th>
      <td>0.873511</td>
    </tr>
    <tr>
      <th>CT</th>
      <td>0.839806</td>
    </tr>
    <tr>
      <th>DC</th>
      <td>0.899450</td>
    </tr>
    <tr>
      <th>DE</th>
      <td>0.835026</td>
    </tr>
    <tr>
      <th>FL</th>
      <td>0.823190</td>
    </tr>
    <tr>
      <th>GA</th>
      <td>0.849306</td>
    </tr>
    <tr>
      <th>HI</th>
      <td>0.816192</td>
    </tr>
    <tr>
      <th>IA</th>
      <td>NaN</td>
    </tr>
    <tr>
      <th>ID</th>
      <td>NaN</td>
    </tr>
    <tr>
      <th>IL</th>
      <td>0.860913</td>
    </tr>
    <tr>
      <th>IN</th>
      <td>0.806308</td>
    </tr>
    <tr>
      <th>KS</th>
      <td>0.858311</td>
    </tr>
    <tr>
      <th>KY</th>
      <td>0.835005</td>
    </tr>
    <tr>
      <th>LA</th>
      <td>0.828594</td>
    </tr>
    <tr>
      <th>MA</th>
      <td>0.841324</td>
    </tr>
    <tr>
      <th>MD</th>
      <td>0.837103</td>
    </tr>
    <tr>
      <th>MI</th>
      <td>0.830536</td>
    </tr>
    <tr>
      <th>MN</th>
      <td>0.851228</td>
    </tr>
    <tr>
      <th>MO</th>
      <td>0.838572</td>
    </tr>
    <tr>
      <th>MS</th>
      <td>NaN</td>
    </tr>
    <tr>
      <th>MT</th>
      <td>0.874037</td>
    </tr>
    <tr>
      <th>NC</th>
      <td>0.831902</td>
    </tr>
    <tr>
      <th>NE</th>
      <td>0.519417</td>
    </tr>
    <tr>
      <th>NH</th>
      <td>0.885235</td>
    </tr>
    <tr>
      <th>NJ</th>
      <td>0.817354</td>
    </tr>
    <tr>
      <th>NM</th>
      <td>0.828945</td>
    </tr>
    <tr>
      <th>NV</th>
      <td>0.816005</td>
    </tr>
    <tr>
      <th>NY</th>
      <td>0.824079</td>
    </tr>
    <tr>
      <th>OH</th>
      <td>0.830508</td>
    </tr>
    <tr>
      <th>OK</th>
      <td>0.825519</td>
    </tr>
    <tr>
      <th>OR</th>
      <td>0.856078</td>
    </tr>
    <tr>
      <th>PA</th>
      <td>0.832139</td>
    </tr>
    <tr>
      <th>RI</th>
      <td>0.845055</td>
    </tr>
    <tr>
      <th>SC</th>
      <td>0.858934</td>
    </tr>
    <tr>
      <th>SD</th>
      <td>0.844788</td>
    </tr>
    <tr>
      <th>TN</th>
      <td>0.801999</td>
    </tr>
    <tr>
      <th>TX</th>
      <td>0.855880</td>
    </tr>
    <tr>
      <th>UT</th>
      <td>0.847335</td>
    </tr>
    <tr>
      <th>VA</th>
      <td>0.822405</td>
    </tr>
    <tr>
      <th>VT</th>
      <td>0.848991</td>
    </tr>
    <tr>
      <th>WA</th>
      <td>0.850302</td>
    </tr>
    <tr>
      <th>WI</th>
      <td>0.856926</td>
    </tr>
    <tr>
      <th>WV</th>
      <td>0.867103</td>
    </tr>
    <tr>
      <th>WY</th>
      <td>0.874102</td>
    </tr>
  </tbody>
</table>
</div>




```python
map_df['predicted_percentage_charged_off'] = pd.DataFrame.from_dict(means, orient='index')
```


```python
#Notice the similarity in outcomes for each column
map_df.loc[:, ['predicted_percentage_charged_off','percentage_charged_off']]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>predicted_percentage_charged_off</th>
      <th>percentage_charged_off</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>AK</th>
      <td>0.860305</td>
      <td>0.863551</td>
    </tr>
    <tr>
      <th>AL</th>
      <td>0.810346</td>
      <td>0.803506</td>
    </tr>
    <tr>
      <th>AR</th>
      <td>0.819547</td>
      <td>0.818792</td>
    </tr>
    <tr>
      <th>AZ</th>
      <td>0.831808</td>
      <td>0.837957</td>
    </tr>
    <tr>
      <th>CA</th>
      <td>0.848516</td>
      <td>0.847003</td>
    </tr>
    <tr>
      <th>CO</th>
      <td>0.873511</td>
      <td>0.870203</td>
    </tr>
    <tr>
      <th>CT</th>
      <td>0.839806</td>
      <td>0.840402</td>
    </tr>
    <tr>
      <th>DC</th>
      <td>0.899450</td>
      <td>0.901304</td>
    </tr>
    <tr>
      <th>DE</th>
      <td>0.835026</td>
      <td>0.827982</td>
    </tr>
    <tr>
      <th>FL</th>
      <td>0.823190</td>
      <td>0.820940</td>
    </tr>
    <tr>
      <th>GA</th>
      <td>0.849306</td>
      <td>0.852081</td>
    </tr>
    <tr>
      <th>HI</th>
      <td>0.816192</td>
      <td>0.824929</td>
    </tr>
    <tr>
      <th>IA</th>
      <td>NaN</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>ID</th>
      <td>NaN</td>
      <td>1.000000</td>
    </tr>
    <tr>
      <th>IL</th>
      <td>0.860913</td>
      <td>0.856349</td>
    </tr>
    <tr>
      <th>IN</th>
      <td>0.806308</td>
      <td>0.814388</td>
    </tr>
    <tr>
      <th>KS</th>
      <td>0.858311</td>
      <td>0.860661</td>
    </tr>
    <tr>
      <th>KY</th>
      <td>0.835005</td>
      <td>0.837957</td>
    </tr>
    <tr>
      <th>LA</th>
      <td>0.828594</td>
      <td>0.824561</td>
    </tr>
    <tr>
      <th>MA</th>
      <td>0.841324</td>
      <td>0.842156</td>
    </tr>
    <tr>
      <th>MD</th>
      <td>0.837103</td>
      <td>0.831000</td>
    </tr>
    <tr>
      <th>MI</th>
      <td>0.830536</td>
      <td>0.825729</td>
    </tr>
    <tr>
      <th>MN</th>
      <td>0.851228</td>
      <td>0.850560</td>
    </tr>
    <tr>
      <th>MO</th>
      <td>0.838572</td>
      <td>0.834356</td>
    </tr>
    <tr>
      <th>MS</th>
      <td>NaN</td>
      <td>0.666667</td>
    </tr>
    <tr>
      <th>MT</th>
      <td>0.874037</td>
      <td>0.878277</td>
    </tr>
    <tr>
      <th>NC</th>
      <td>0.831902</td>
      <td>0.826147</td>
    </tr>
    <tr>
      <th>NE</th>
      <td>0.519417</td>
      <td>0.333333</td>
    </tr>
    <tr>
      <th>NH</th>
      <td>0.885235</td>
      <td>0.885266</td>
    </tr>
    <tr>
      <th>NJ</th>
      <td>0.817354</td>
      <td>0.818694</td>
    </tr>
    <tr>
      <th>NM</th>
      <td>0.828945</td>
      <td>0.829968</td>
    </tr>
    <tr>
      <th>NV</th>
      <td>0.816005</td>
      <td>0.812641</td>
    </tr>
    <tr>
      <th>NY</th>
      <td>0.824079</td>
      <td>0.823690</td>
    </tr>
    <tr>
      <th>OH</th>
      <td>0.830508</td>
      <td>0.827336</td>
    </tr>
    <tr>
      <th>OK</th>
      <td>0.825519</td>
      <td>0.820496</td>
    </tr>
    <tr>
      <th>OR</th>
      <td>0.856078</td>
      <td>0.860780</td>
    </tr>
    <tr>
      <th>PA</th>
      <td>0.832139</td>
      <td>0.834407</td>
    </tr>
    <tr>
      <th>RI</th>
      <td>0.845055</td>
      <td>0.828610</td>
    </tr>
    <tr>
      <th>SC</th>
      <td>0.858934</td>
      <td>0.858466</td>
    </tr>
    <tr>
      <th>SD</th>
      <td>0.844788</td>
      <td>0.837629</td>
    </tr>
    <tr>
      <th>TN</th>
      <td>0.801999</td>
      <td>0.799675</td>
    </tr>
    <tr>
      <th>TX</th>
      <td>0.855880</td>
      <td>0.856286</td>
    </tr>
    <tr>
      <th>UT</th>
      <td>0.847335</td>
      <td>0.845718</td>
    </tr>
    <tr>
      <th>VA</th>
      <td>0.822405</td>
      <td>0.830458</td>
    </tr>
    <tr>
      <th>VT</th>
      <td>0.848991</td>
      <td>0.856140</td>
    </tr>
    <tr>
      <th>WA</th>
      <td>0.850302</td>
      <td>0.849528</td>
    </tr>
    <tr>
      <th>WI</th>
      <td>0.856926</td>
      <td>0.844144</td>
    </tr>
    <tr>
      <th>WV</th>
      <td>0.867103</td>
      <td>0.879475</td>
    </tr>
    <tr>
      <th>WY</th>
      <td>0.874102</td>
      <td>0.874109</td>
    </tr>
  </tbody>
</table>
</div>




```python
#MS, IA, and ID did not appear in the test set. These choices will help keep the color schemes consistent in the
#chloropleths.
map_df.loc[['MS','IA'],'predicted_percentage_charged_off'] = 0.0

map_df.loc[['ID'],'predicted_percentage_charged_off'] = 1.0
```

Be wary of the scales on the right. We see that for states with large numbers of oberservations, the percentage of predicted paid off loans matches the percentage of paid off loans in that state while for states with fewer observations, the behavior is drawn back toward the mean.


```python
for per in ['predicted_percentage_charged_off', 'percentage_charged_off']:
    ax = map_df.plot(per, figsize=(30,15), legend=True)
    ax.set_title(per, fontsize=18)
```


![png](output_68_0.png)



![png](output_68_1.png)


### Concluding Remarks
The model we have presented represents an elegant way to handle stratified data in a way that is robust to overfitting but remains highly interpretable. There are few methods that can achieve this balance!
