import sqlalchemy as db
import pandas as pd
import pickle

from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

engine = db.create_engine('postgresql://iti:iti@localhost/FirstDB')

query = """
SELECT *
FROM public."IRIS";
"""

data =pd.read_sql(query,con=engine)
data.head()

X = data.drop(['species'], axis=1)
y = data['species']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=5)

# experimenting with different n values
k_range = list(range(1,26))
scores = []
for k in k_range:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X, y)
    y_pred = knn.predict(X)
    scores.append(metrics.accuracy_score(y, y_pred))

logreg = LogisticRegression()
logreg.fit(X, y)
y_pred = logreg.predict(X)

knn = KNeighborsClassifier(n_neighbors=12)
knn.fit(X, y)

# make a prediction for an example of an out-of-sample observation
knn.predict([[3, 5, 1, 2]])

# generate model pickle file
file_name = "generated_model"
pickle.dump(knn,open(file_name,'wb'))

# load pickle file
loadaed_model = pickle.load(open(file_name,'rb'))
loadaed_model.predict([[3, 5, 1, 2]])
