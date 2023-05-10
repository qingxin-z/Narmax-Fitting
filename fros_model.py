import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from file_processing import FileProcessing
from sysidentpy.model_structure_selection import FROLS
from sysidentpy.basis_function._basis_function import Polynomial, Fourier
from sysidentpy.metrics import root_relative_squared_error
from sysidentpy.utils.plotting import plot_residues_correlation, plot_results
from epis_test import results

#file1 = FileProcessing('W:/Qingxin Zhang/01 - FCDX EPIS/01 Data processing code/Sample files/EPIS0311/EPISEPIS2 - 200311 131049.csv', '.csv', sinefit=False)
#file2 = FileProcessing('W:/Qingxin Zhang/01 - FCDX EPIS/01 Data processing code/Sample files/EPIS0311/EPISEPIS2 - 200311 130709.csv', '.csv', sinefit=False)

full_data = results

full_data_x = np.array(list(map(float, full_data.loc[:, 'Outlet']))).reshape(-1, 1)
full_data_y = np.array(list(map(float, full_data.loc[:, 'Voltage']))).reshape(-1, 1)

# full_data_x = file1.get_column('pressure_cathode_inlet_spare').reshape(-1, 1)
# full_data_y = file1.get_column('voltage').reshape(-1, 1)
half_lenth = int(len(full_data_x) / 2)

xtrain = full_data_x[:half_lenth]
ytrain = full_data_y[:half_lenth]

xtest = full_data_x[half_lenth:]
ytest = full_data_y[half_lenth:]

# xtrain = file1.get_column('pressure_cathode_inlet_spare').reshape(-1, 1)
# ytrain = file1.get_column('voltage').reshape(-1, 1)

# xtest = file2.get_column('pressure_cathode_inlet_spare').reshape(-1, 1)
# ytest = file2.get_column('voltage').reshape(-1, 1)

#basis_function = Polynomial(degree=2)
basis_function = Fourier(degree=1, n=1, p=2*np.pi, ensemble=True)

model = FROLS(
    order_selection=True,
    n_info_values=3,
    extended_least_squares=False,
    ylag=2, xlag=2,
    info_criteria='aic',
    #model_type='NARMAX',
    estimator='least_squares',
    basis_function=basis_function
)

model.fit(X=xtrain, y=ytrain)
yhat = model.predict(X=xtest, y=ytest)
plot_results(y=ytest, yhat=yhat, n=100000)