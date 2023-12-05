# https://www.tensorflow.org/tutorials/keras/classification
# This guide uses tf.keras, a high-level API to build and train models in TensorFlow


# TensorFlow and tf.keras
import tensorflow as tf

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt

print(tf.__version__)



#~~~~~~~~~~~~~~~~~~~~~~~~`
# Import the Fashion MNIST dataset
#~~~~~~~~~~~~~~~~~~~~~~~~`

# The Fashion MNIST dataset contains 70,000 grayscale images in 10 categories.
# The images show individual articles of clothing at low resolution (28 by 28 pixels)

fashion_mnist = tf.keras.datasets.fashion_mnist

(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
print(np.unique(test_labels))

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']



#~~~~~~~~~~~~~~~~~~~~~~~~`
# Explore the data
#~~~~~~~~~~~~~~~~~~~~~~~~`

print(train_images.shape)
print(len(train_labels))



#~~~~~~~~~~~~~~~~~~~~~~~~`
# Preprocess the data
#~~~~~~~~~~~~~~~~~~~~~~~~`


if 0:
    plt.figure()
    plt.imshow(train_images[0])
    plt.colorbar()
    plt.grid(False)
    plt.show()

# The data must be preprocessed before training the network. 
# Scale these values to a range of 0 to 1 before feeding them to the neural network model.
# To do so, divide the values by 255.
# It's important that the training set and the testing set be preprocessed in the same way:

train_images = train_images / 255.0

test_images = test_images / 255.0

# Verify data are in the correct order and format
if 0:
    plt.figure(figsize=(10,10))
    for i in range(25):
        plt.subplot(5,5,i+1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.imshow(train_images[i], cmap=plt.cm.binary)
        plt.xlabel(class_names[train_labels[i]])
    plt.show()



#~~~~~~~~~~~~~~~~~~~~~~~~`
# Build the model
#~~~~~~~~~~~~~~~~~~~~~~~~`

# Set up the layers

model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10)
])

"""
Flatten: transforms the format of the images from
    a two-dimensional array (of 28 by 28 pixels) to
    a one-dimensional array (of 28 * 28 = 784 pixels).
    This layer has no parameters to learn; it only
    reformats the data.
Dense: fully connected, neural layers.
    The second Dense layer returns a logits array with
    length of 10. Each node contains a score that indicates
    the current image belongs to one of the 10 classes.
"""

# Compile the model

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

"""
Before the model is ready for training, it needs a few more settings.
These are added during the model's compile step:

Optimizer: This is how the model is updated based on
    the data it sees and its loss function.
Loss function: This measures how accurate the model is
    during training. You want to minimize this function
    to "steer" the model in the right direction.
Metrics: Used to monitor the training and testing steps.
    The following example uses accuracy, the fraction
    of the images that are correctly classified.
"""


#~~~~~~~~~~~~~~~~~~~~~~~~`
# Train the model
#~~~~~~~~~~~~~~~~~~~~~~~~`


# Fit the model: To start training, call the model.fit method.
model.fit(train_images, train_labels, epochs=10)

# Evaluate accuracy: Next, compare how the model performs on the test dataset:
test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)
print('\nTest accuracy:', test_acc)

# Make predictions: With the model trained, you can use it to
# make predictions about some images. Attach a softmax layer
# to convert the model's linear outputs—logits to
# probabilities, which should be easier to interpret.
probability_model = tf.keras.Sequential([model, 
                                         tf.keras.layers.Softmax()])
predictions = probability_model.predict(test_images)

# Let's take a look at the first prediction:
# A prediction is an array of 10 numbers. They represent the model's
# "confidence" that the image corresponds to each of the 10
# different articles of clothing
print("First prediction:", predictions[0])

# You can see which label has the highest confidence value:
print(np.argmax(predictions[0]))

# Examining the test label shows that this classification is correct:
print(test_labels[0])



# Define functions to graph the full set of 10 class predictions.

def plot_image(i, predictions_array, true_label, img):
  true_label, img = true_label[i], img[i]
  plt.grid(False)
  plt.xticks([])
  plt.yticks([])

  plt.imshow(img, cmap=plt.cm.binary)

  predicted_label = np.argmax(predictions_array)
  if predicted_label == true_label:
    color = 'blue'
  else:
    color = 'red'

  plt.xlabel("{} {:2.0f}% ({})".format(class_names[predicted_label],
                                100*np.max(predictions_array),
                                class_names[true_label]),
                                color=color)

def plot_value_array(i, predictions_array, true_label):
  true_label = true_label[i]
  plt.grid(False)
  plt.xticks(range(10))
  plt.yticks([])
  thisplot = plt.bar(range(10), predictions_array, color="#777777")
  plt.ylim([0, 1])
  predicted_label = np.argmax(predictions_array)

  thisplot[predicted_label].set_color('red')
  thisplot[true_label].set_color('blue')



# Verify predictions
# Let's look at the 0th image, predictions, and prediction array.
# Correct prediction labels are blue and incorrect prediction
# labels are red. The number gives the percentage (out of 100)
# for the predicted label.

i = 0
plt.figure(figsize=(6,3))
plt.subplot(1,2,1)
plot_image(i, predictions[i], test_labels, test_images)
plt.subplot(1,2,2)
plot_value_array(i, predictions[i],  test_labels)
plt.show()

i = 12
plt.figure(figsize=(6,3))
plt.subplot(1,2,1)
plot_image(i, predictions[i], test_labels, test_images)
plt.subplot(1,2,2)
plot_value_array(i, predictions[i],  test_labels)
plt.show()


# Let's plot several images with their predictions.
# Note that the model can be wrong even when very confident
# Plot the first X test images, their predicted labels, and the true labels.
# Color correct predictions in blue and incorrect predictions in red.
num_rows = 5
num_cols = 3
num_images = num_rows*num_cols
plt.figure(figsize=(2*2*num_cols, 2*num_rows))
for i in range(num_images):
  plt.subplot(num_rows, 2*num_cols, 2*i+1)
  plot_image(i, predictions[i], test_labels, test_images)
  plt.subplot(num_rows, 2*num_cols, 2*i+2)
  plot_value_array(i, predictions[i], test_labels)
plt.tight_layout()
plt.show()



