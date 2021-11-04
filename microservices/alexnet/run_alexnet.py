# Reference: https://towardsdatascience.com/implementing-alexnet-cnn-architecture-using-tensorflow-2-0-and-keras-2113e090ad98
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import os
import time

# Divides the shuffling buffers, sacraficing shuffling perfection to reduce RAM load
ALEXNET_BUFFER_SIZE_REDUCE_MODIFIER = int(os.getenv('ALEXNET_BUFFER_SIZE_REDUCE_MODIFIER', 4))

# Smaller batches result in increased ETA but reduced RAM load
ALEXNET_BATCH_SIZE = int(os.getenv('ALEXNET_BATCH_SIZE', 16))

def process_images(image, label):
    # Normalize images to have a mean of 0 and standard deviation of 1
    image = tf.image.per_image_standardization(image)
    # Resize images from 32x32 to 277x277
    image = tf.image.resize(image, (227,227))
    return image, label

if __name__ == '__main__':

    (train_images, train_labels), (test_images, test_labels) = keras.datasets.cifar10.load_data()

    CLASS_NAMES= ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

    validation_images, validation_labels = train_images[:5000], train_labels[:5000]
    train_images, train_labels = train_images[5000:], train_labels[5000:]

    train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels))
    test_ds = tf.data.Dataset.from_tensor_slices((test_images, test_labels))
    validation_ds = tf.data.Dataset.from_tensor_slices((validation_images, validation_labels))



    train_ds_size = tf.data.experimental.cardinality(train_ds).numpy()
    test_ds_size = tf.data.experimental.cardinality(test_ds).numpy()
    validation_ds_size = tf.data.experimental.cardinality(validation_ds).numpy()
    print("Training data size:", train_ds_size)
    print("Test data size:", test_ds_size)
    print("Validation data size:", validation_ds_size)

    print("Doing shuffling and batching")
    train_ds = (train_ds
                    .map(process_images)
                    .shuffle(buffer_size=train_ds_size/ALEXNET_BUFFER_SIZE_REDUCE_MODIFIER)
                    .batch(batch_size=ALEXNET_BATCH_SIZE, drop_remainder=True))
    test_ds = (test_ds
                    .map(process_images)
                    .shuffle(buffer_size=train_ds_size/ALEXNET_BUFFER_SIZE_REDUCE_MODIFIER)
                    .batch(batch_size=ALEXNET_BATCH_SIZE, drop_remainder=True))
    validation_ds = (validation_ds
                    .map(process_images)
                    .shuffle(buffer_size=train_ds_size/ALEXNET_BUFFER_SIZE_REDUCE_MODIFIER)
                    .batch(batch_size=ALEXNET_BATCH_SIZE, drop_remainder=True))

    print("Defining the model")
    model = keras.models.Sequential([
        keras.layers.Conv2D(filters=96, kernel_size=(11,11), strides=(4,4), activation='relu', input_shape=(227,227,3)),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPool2D(pool_size=(3,3), strides=(2,2)),
        keras.layers.Conv2D(filters=256, kernel_size=(5,5), strides=(1,1), activation='relu', padding="same"),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPool2D(pool_size=(3,3), strides=(2,2)),
        keras.layers.Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), activation='relu', padding="same"),
        keras.layers.BatchNormalization(),
        keras.layers.Conv2D(filters=384, kernel_size=(1,1), strides=(1,1), activation='relu', padding="same"),
        keras.layers.BatchNormalization(),
        keras.layers.Conv2D(filters=256, kernel_size=(1,1), strides=(1,1), activation='relu', padding="same"),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPool2D(pool_size=(3,3), strides=(2,2)),
        keras.layers.Flatten(),
        keras.layers.Dense(4096, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(4096, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(10, activation='softmax')
    ])


    model.compile(loss='sparse_categorical_crossentropy', optimizer=tf.optimizers.SGD(lr=0.001), metrics=['accuracy'])
    model.summary()

    print("Dealing with logging")
    root_logdir = os.path.join(os.curdir, "logs\\fit\\")
    def get_run_logdir():
        run_id = time.strftime("run_%Y_%m_%d-%H_%M_%S")
        return os.path.join(root_logdir, run_id)

    run_logdir = get_run_logdir()
    tensorboard_cb = keras.callbacks.TensorBoard(run_logdir)

    print("Starting to fit")
    model.fit(train_ds,
            epochs=100,
            validation_data=validation_ds,
            validation_freq=1,
            callbacks=[tensorboard_cb])


    print("Evaluating")
    model.evaluate(test_ds)
