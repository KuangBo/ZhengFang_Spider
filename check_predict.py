# encoding=utf-8
import numpy as np
from sklearn.externals import joblib
from PIL import Image


def predict():
    photo_path = './cache/check-{}.png'
    x = []
    for i in range(1, 5):
        img = Image.open(photo_path.format(i))
        ls = np.array(img).tostring()
        ls = np.fromstring(ls, dtype=bool)
        x.append(ls)
    file_path = './model/knn.pkl'
    knn = joblib.load(file_path)
    ls = knn.predict(x)
    return "".join(ls)
