# -*- coding: utf-8 -*-
"""Klasifikasi Gambar TFLite.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14NPbm4KZKzMA7E5fRvracPZkKHzeBpoX
"""

! chmod 600 /content/kaggle.json

# import dataset
! KAGGLE_CONFIG_DIR=/content/ kaggle datasets download -d shiv28/animal-5-mammal

import zipfile,os

zip_file = zipfile.ZipFile('/content/animal-5-mammal.zip')
zip_file.extractall('/tmp/')

daftar_hewan=os.listdir('/tmp/Animal/train')
print(daftar_hewan)

from PIL import Image

total = 0

for i in daftar_hewan:
  dir = os.path.join('/tmp/Animal/train', i)
  y = len(os.listdir(dir))
  print(i+':', y)
  total = total + y
  
  img_name = os.listdir(dir)

  for j in range(4):
    img_path = os.path.join(dir, img_name[j])
    img = Image.open(img_path)
    print('-',img.size)
  print('======================')

print('\nTotal Dataset :', total)

from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_data = ImageDataGenerator(
    rescale=1/255,
    horizontal_flip=True,
    vertical_flip=True,
    rotation_range=30,
    shear_range = 0.2,
    fill_mode='nearest',
    validation_split=0.2
)

val_data = ImageDataGenerator(
    rescale=1/255
)

train_generator = train_data.flow_from_directory(
    '/tmp/Animal/train',
    target_size=(150,150),
    class_mode='categorical',
    subset='training'
)

val_generator = train_data.flow_from_directory(
    '/tmp/Animal/train',
    target_size=(150,150),
    class_mode='categorical',
    subset='validation'
)

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Flatten, MaxPool2D, Dense

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(150, 150, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(512, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(5, activation='softmax')
])

model.summary()

model.compile(
    loss='binary_crossentropy',
    optimizer=tf.optimizers.Adam(),
    metrics=['accuracy']
)

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.92 and logs.get('val_accuracy')>0.92):
      print("\nAkurasi telah mencapai > 92%!")
      self.model.stop_training = True
callbacks = myCallback()

history = model.fit(
    train_generator,
    epochs=200,
    steps_per_epoch=115,
    validation_data=val_generator,
    validation_steps=10,
    verbose=2,
    callbacks=[callbacks]
)

import matplotlib.pyplot as plt

# plot accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Accuracy Model')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.grid(True)
plt.show()

# plot loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('Loss')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.grid(True)
plt.show()

# konversi model
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# simpan model
with tf.io.gfile.GFile('klasifikasi_gambar_model.tflite', 'wb') as f:
  f.write(tflite_model)