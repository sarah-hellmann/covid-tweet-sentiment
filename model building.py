#sentiment model

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score
from sklearn.svm import LinearSVC
from sklearn import metrics
import pickle
from sklearn.metrics import confusion_matrix

pd.set_option('max_columns', 100)

#file = 'training_10.csv'
file = 'tweets_bulk.csv'

df = pd.read_csv(file)



#*****************Sentiment transformation ******************************

#0= Neutral, 0>1 positive, -1>0 negative
# df['sentiment_cat'] = df.sentiment.apply(lambda x: "Low" if x < 0 else "Neutral" if x == 0 else "High")

# NO Neutral 0>1 positive, -1>0 negative
df['sentiment_cat'] = df.sentiment.apply(lambda x: "Low" if x < 0 else "High")


#************************************************************************

#DROP neutral
# x = df[(df.sentiment_cat == "Neutral")].index
# df = df.drop(x)

#************************************************************************

# #rebalancing High 
# df_high = df[df.sentiment_cat=='High']
# df_low =  df[df.sentiment_cat=='Low']

# majority = df_high.shape[0]
# minority = df_low.shape[0]

# from sklearn.utils import resample

# df_high_undersample = resample(df_high, replace=False, n_samples = minority)
# df = pd.concat([df_high_undersample, df_low])

#************************************************************************

print(df.sentiment_cat.value_counts())
print(df.sentiment_cat.value_counts()/df.sentiment_cat.shape[0])


#Summary:
#80/20
#Balanced High and Low with NO Neutral: accuracy = .79 CV, .8 test 
#Unbalanced with NO neutral - accuracy = .81 CV, .81 test
#No neutral-all high - unbalanced - accuracy = .85 cv, .85 test
#No neutral-all high - balanced - accuracy .79, .79


#model
X = df.loc[:,['text']]
y = df.sentiment_cat


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .20, stratify = y)

X_train_doc = [doc for doc in X_train.text]

vect = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=2500).fit(X_train_doc)

X_train_features = vect.transform(X_train_doc)

#features
#print("X_train_features:\n{}".format(repr(X_train_features)))

feature_names = vect.get_feature_names()

# print("Number of features: {}".format(len(feature_names)))
# print("First 100 features:\n{}".format(feature_names[:200]))
# print("Every 100th feature:\n{}".format(feature_names[::100]))

lin_svc = LinearSVC(max_iter=120000)

scores = cross_val_score(lin_svc, X_train_features, y_train, cv=5)

print("mean cross-validation accuracy: {:.2f}".format(np.mean(scores)))

lin_svc.fit(X_train_features, y_train)

X_test_docs = [doc for doc in X_test.text]

X_test_features = vect.transform(X_test_docs)

y_test_pred = lin_svc.predict(X_test_features)

print("test set validation accuracy: {:.2f}".format(metrics.accuracy_score(y_test, y_test_pred)))

print(y_test_pred[1])

# with open('credibility.model', 'ab') as f:
# 	pickle.dump(lin_svc, f)

# with open('credibility.vect', 'ab') as f:
# 	pickle.dump(vect, f)

# with open('y_test', 'ab') as f:
# 	pickle.dump(y_test, f)

# with open('y_test_pred', 'ab') as f:
# 	pickle.dump(y_test_pred, f)

print("Confusion matrics is:")
cm = confusion_matrix(y_test, y_test_pred)
print(cm)