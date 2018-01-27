# coding=utf-8
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
import os
import io
# import time
from PIL import Image

index = [0] * 33
index_tmp = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 'a': 9, 'b': 10, 'c': 11, 'd': 12,
             'e': 13, 'f': 14, 'g': 15, 'h': 16, 'i': 17, 'j': 18, 'k': 19, 'l': 20, 'm': 21, 'n': 22, 'p': 23, 'q': 24,
             'r': 25, 's': 26, 't': 27, 'u': 28, 'v': 29, 'w': 30, 'x': 31, 'y': 32}
for k, v in index_tmp.items():
    index[v] = k
# 加载model
model = load_model('D:/Program Files/JetBrains/WorkSpaces/PycharmProject/ZhengFang_System_Spider/yy.h5')


def get(path):
    image = load_img(path, grayscale=True, target_size=(12, 22))
    image = img_to_array(image)
    image = np.resize(image, (1, 12, 22, 1))
    image /= 255
    y_prob = model.predict(image)
    y_classes = y_prob.argmax(axis=-1)
    return index[y_classes[0]]


def depoint(img):  # input: gray image
    pixdata = img.load()
    w, h = img.size
    for i in [0, h - 1]:
        for j in range(w):
            pixdata[j, i] = 255
    for i in [0, w - 1]:
        for j in range(h):
            pixdata[i, j] = 255
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            count = 0
            if pixdata[x, y - 1] > 245:
                count = count + 1
            if pixdata[x, y + 1] > 245:
                count = count + 1
            if pixdata[x - 1, y] > 245:
                count = count + 1
            if pixdata[x + 1, y] > 245:
                count = count + 1
            if count > 2:
                pixdata[x, y] = 255
    return img


def handle_image(path):
    with open(os.path.join(path), 'rb') as f:
        pic = f.read()
    pic = io.BytesIO(pic)
    pic = Image.open(pic).convert('1')
    pic = depoint(pic)
    y_min, y_max = 0, 22
    split_lines = [5, 17, 29, 41, 53]
    images = [pic.crop([u, y_min, v, y_max])
              for u, v in zip(split_lines[:-1], split_lines[1:])]
    result = ''
    for i in images:
        bitio = io.BytesIO()
        i.save(bitio, 'png')
        bitio.seek(0)
        result += get(bitio)
    return result


# if __name__ == '__main__':
#     model = load_model('D:/Program Files/JetBrains/WorkSpaces/PycharmProject/ZhengFang_System_Spider/yy.h5')
#     print(handle_image('D:/Program Files/JetBrains/WorkSpaces/PycharmProject/ZhengFang_System_Spider/cache/check.png'))
