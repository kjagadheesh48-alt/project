import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

df=pd.read_csv("../data/dataset.csv")

X=df[["Rainfall","pH","Turbidity","Cases"]]
y=df["Risk"]

model=RandomForestClassifier(n_estimators=200)
model.fit(X,y)

with open("model.pkl","wb") as f:
    pickle.dump(model,f)

print("Model trained!")