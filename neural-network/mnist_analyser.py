from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from random import Random
from itertools import product
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix

SEED = 42
TRAIN_DATA = 0.75


def display_digit(csv, column):
    data = csv[:-1]
    raw_number = np.copy(data[:, column])
    write_digit = np.reshape(raw_number, (20, 20), 'F')
    plt.imshow(write_digit, cmap='gray')
    plt.show()
    return


def read_csv(file='exdata.csv'):
    return np.genfromtxt(file, delimiter=',')


def plot_confusion_matrix(
        conf_mat, names=[], title='Confusion Matrix',
        img=False, cmap=plt.cm.Blues):
    if not img:
        print("{}:\n {}".format(title, conf_mat))
        return
    else:
        plt.figure(1)
        plt.imshow(conf_mat, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()
        plt.xticks(names)
        plt.yticks(names)

        mid = conf_mat.max() / 2.
        for i, j in product(
                range(conf_mat.shape[0]),
                range(conf_mat.shape[1])):
            plt.text(j, i, conf_mat[i, j],
                horizontalalignment="center",
                color="white" if conf_mat[i, j] > mid else "black")

        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
    return


def display_trained_predicted(data, expected, predicted, test_indexes):
    imgs_and_labels = list(zip(data, expected))
    plt.figure(2)
    for index, (image, label) in enumerate(imgs_and_labels[:4]):
        plt.subplot(2, 4, index + 1)
        plt.axis('off')
        img = np.reshape(image, (20, 20), 'F')
        plt.imshow(img, cmap=plt.cm.gray_r, interpolation='nearest')
        plt.title('Training: {}'.format(label if label != 10 else 0.0))

    imgs_and_prdcts = list(zip(data[test_indexes], predicted))
    for index, (image, prediction) in enumerate(imgs_and_prdcts[:4]):
        plt.subplot(2, 4, index + 5)
        plt.axis('off')
        img = np.reshape(image, (20, 20), 'F')
        plt.imshow(img, cmap=plt.cm.gray_r, interpolation='nearest')
        plt.title('Prediction: {}'.format(prediction if prediction != 10 else 0.0))

    plt.show()
    return

csv_raw = read_csv()
expected = csv_raw[-1]
data = csv_raw[:-1].transpose()
total_pop = len(expected)

rand = Random()
try:
    rand.seed(SEED, 1)
except TypeError:
    rand.seed(SEED)

train_indexes = []
for digit in sorted(set(expected)):
    print("Getting sample for digit {}".format(digit))
    pop = list(i for i, d in enumerate(expected) if d == digit)
    pop_length = len(pop)
    sample_length = int(pop_length*TRAIN_DATA)
    sample = rand.sample(pop, sample_length)
    print("Sample generated for digit {}:\n\
    - Length of the sample: {}\n\
    - Length of the population: {}\n\
    - Sample: {}".\
          format(digit, sample_length, pop_length, sample))
    train_indexes.extend(sample)

# Separate indexes that are used for testing..
test_indexes = list(set(range(total_pop))-set(train_indexes))
print("Total train data selected: {}\nTotal test data selected: {}".\
        format(len(train_indexes), len(test_indexes)))

clf = MLPClassifier(
    hidden_layer_sizes=(100, 100), learning_rate_init=0.0035,
    learning_rate='adaptive', solver='lbfgs', activation='logistic',
    verbose=True
)

clf.fit(data[train_indexes], expected[train_indexes])
predicted = clf.predict(data[test_indexes])

hit = clf.score(data[test_indexes], expected[test_indexes])
print("Hit Rate: {}".format(hit))
print("Miss Rate: {}".format(1 - hit))

conf_mat = confusion_matrix(expected[test_indexes], predicted)

yxnames = [i for i in range(10)]
plot_confusion_matrix(conf_mat, names=yxnames, img=True)
display_trained_predicted(data, expected, predicted, test_indexes)
