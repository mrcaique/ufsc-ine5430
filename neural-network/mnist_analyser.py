import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix

def display_digit(csv, column):
    data = csv[:-1]
    raw_number = np.copy(data[:, column])
    write_digit = np.reshape(raw_number, (20, 20), 'F')
    plt.imshow(write_digit, cmap='gray')
    plt.show()

def read_csv(file='exdata.csv'):
    return np.genfromtxt(file, delimiter=',')

csv_raw = read_csv()
expected = csv_raw[-1]
data = csv_raw[:-1].transpose()

clf = MLPClassifier(
    hidden_layer_sizes=(100, 100, 100, 100, 100, 100), 
    learning_rate='adaptive', solver='sgd', activation='relu', verbose=True
    )
clf.fit(data, expected)
predicted = clf.predict(data)

conf_mat = "Confusion Matrix:\n {}". \
    format(confusion_matrix(expected, predicted))
print(conf_mat)
hit = clf.score(data, expected)
print("Hit Rate: {}".format(hit))
print("Miss Rate: {}".format(1 - hit))
