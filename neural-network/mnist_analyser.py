from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from random import Random
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


def read_csv(file):
    return np.genfromtxt(file, delimiter=',')

csv_raw = read_csv('exdata.csv')
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
    hidden_layer_sizes=(100, 100, 100, 50), learning_rate_init=0.0035,
    learning_rate='adaptive', solver='sgd', activation='relu', verbose=True
)

clf.fit(data[train_indexes], expected[train_indexes])
predicted = clf.predict(data[test_indexes])

conf_mat = "Confusion Matrix:\n {}". \
    format(confusion_matrix(expected[test_indexes], predicted))
hit = clf.score(data[test_indexes], expected[test_indexes])
print(conf_mat)
print("Hit Rate: {}".format(hit))
print("Miss Rate: {}".format(1 - hit))
