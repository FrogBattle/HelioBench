# Reference: https://mxnet.apache.org/versions/1.3.1/tutorials/python/predict_image.html
# @article{recht2018cifar10.1,
#   author = {Benjamin Recht and Rebecca Roelofs and Ludwig Schmidt and Vaishaal Shankar},
#   title = {Do CIFAR-10 Classifiers Generalize to CIFAR-10?},
#   year = {2018},
#   note = {\url{https://arxiv.org/abs/1806.00451} },
# }

# @article{torralba2008tinyimages,
#   author = {Antonio Torralba and Rob Fergus and William T. Freeman},
#   journal = {IEEE Transactions on Pattern Analysis and Machine Intelligence},
#   title = {80 Million Tiny Images: A Large Data Set for Nonparametric Object and Scene Recognition},
#   year = {2008},
#   volume = {30},
#   number = {11},
#   pages = {1958-1970}
# }

from os import getenv
from time import time
import mxnet as mx
import matplotlib.pyplot as plt
import numpy as np
from collections import namedtuple
from tensorflow.keras import datasets, layers, models
import tarfile

Batch = namedtuple('Batch', ['data'])
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']
DATASET_NAME = 'cifar-10-python.tar.gz'


def run():
    # Set seed for reproducible workloads
    np.random.seed(0)

    print("Running inference of an 18-layer Resnet pretrained model on a CIFAR10 dataset")
    path = 'http://data.mxnet.io/models/imagenet/'
    [mx.test_utils.download(path+'resnet/18-layers/resnet-18-0000.params'),
     mx.test_utils.download(path+'resnet/18-layers/resnet-18-symbol.json'),
     mx.test_utils.download(path+'synset.txt')]

    ctx = mx.cpu()
    sym, arg_params, aux_params = mx.model.load_checkpoint('resnet-18', 0)
    mod = mx.mod.Module(symbol=sym, context=ctx, label_names=None)
    mod.bind(for_training=False, data_shapes=[('data', (1, 3, 1536, 1536))],
             label_shapes=mod._label_shapes)
    mod.set_params(arg_params, aux_params, allow_missing=True)

    print("Downloading CIFAR10 dataset")
    (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
    train_images, test_images = train_images / 255.0, test_images / 255.0

    start_time = time()
    duration = getenv('ALEXNET_INFERENCE_DURATION', '10m')
    try:
        duration_in_seconds = int(duration.split('m')[0]) * 60
    except ValueError:
        print("Error parsing duration. Specify minutes in format MMMMm.")
    while True:
        image_index = np.random.randint(0, len(train_images))
        image = train_images[image_index]
        # for image_index, image in enumerate(train_images):
        img = mx.image.imresize(mx.nd.array(image), 1536, 1536)  # resize
        img = img.transpose((2, 0, 1))  # Channel first
        img = img.expand_dims(axis=0)  # batchify
        # compute the predict probabilities
        mod.forward(Batch([img]))
        prob = mod.get_outputs()[0].asnumpy()
        # print the top-3
        prob = np.squeeze(prob)
        a = np.argsort(prob)[::-1]
        print(f"Inference for picture {image_index}")
        for i in a[0:2]:
            print('Inferred probability=%f, class=%s' % (prob[i], class_names[train_labels[i][0]]))
        print('')

        if time() > start_time + duration_in_seconds:
            print("Experiment finished")
            return


if __name__ == '__main__':
    run()
