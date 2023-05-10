import deepxde as dde
import numpy as np
from file_processing import FileProcessing
from epis_test import results

#file1 = FileProcessing('W:/Qingxin Zhang/01 - FCDX EPIS/01 Data processing code/Sample files/EPIS0311/EPISEPIS2 - 200311 131049.csv', '.csv', sinefit=True)

full_data = results

full_data_x1 = np.array(list(map(float, full_data.loc[:, 'index']))).reshape(-1, 1)
full_data_x2 = np.array(list(map(float, full_data.loc[:, 'Inlet']))).reshape(-1, 1)
full_data_x3 = np.array(list(map(float, full_data.loc[:, 'Voltage']))).reshape(-1, 1)
half_lenth = int(len(full_data_x1) / 2)

xtrain = full_data_x1[:half_lenth]
ytrain = full_data_x3[:half_lenth]

xtest = full_data_x1[half_lenth:]
ytest = full_data_x3[half_lenth:]

data = dde.data.DataSet(X_train=xtrain, y_train=ytrain, X_test=xtest, y_test=ytest)

layer_size = [1] + [50] * 3 + [1]
activation = "tanh"
initializer = "He normal"
net = dde.nn.FNN(layer_size, activation, initializer)

model = dde.Model(data, net)
model.compile("adam", lr=0.0001, metrics=["mean l2 relative error"])#
losshistory, train_state = model.train(iterations=50000)
# model.compile("adam", lr=0.00001, metrics=["l2 relative error"])
# losshistory, train_state = model.train(iterations=50000)
dde.saveplot(losshistory, train_state, issave=True, isplot=True)
model.print_model()