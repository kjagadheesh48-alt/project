import pandas as pd
import numpy as np

np.random.seed(1)
wards = ["Ward1","Ward2","Ward3","Ward4","Ward5"]

rows=500
data=[]

for i in range(rows):
    ward=np.random.choice(wards)
    rainfall=np.random.randint(0,200)
    ph=np.random.uniform(5.5,8.5)
    turbidity=np.random.uniform(1,10)
    cases=int((rainfall*0.05)+(turbidity*1.2)+np.random.randint(0,5))

    if cases>18:
        risk="High"
    elif cases>10:
        risk="Medium"
    else:
        risk="Low"

    data.append([ward,rainfall,ph,turbidity,cases,risk])

df=pd.DataFrame(data,columns=["Ward","Rainfall","pH","Turbidity","Cases","Risk"])
df.to_csv("../data/dataset.csv",index=False)

print("Dataset created!")