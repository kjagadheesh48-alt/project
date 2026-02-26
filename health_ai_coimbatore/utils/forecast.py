import numpy as np

def forecast_cases(current_cases):
    forecast=[]
    base=current_cases
    for i in range(7):
        base=base+np.random.randint(-2,4)
        base=max(0,base)
        forecast.append(base)
    return forecast