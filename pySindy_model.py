import pysindy as ps
import numpy as np
#import scipy as sp
from epis_test import results 
import matplotlib.pyplot as plt


full_data = results

full_data_x1 = np.array(list(map(float, full_data.loc[:, 'Outlet']))).reshape(-1, 1)
full_data_x2 = np.array(list(map(float, full_data.loc[:, 'Inlet']))).reshape(-1, 1)
full_data_x3 = np.array(list(map(float, full_data.loc[:, 'Voltage']))).reshape(-1, 1)

# full_data_x = file1.get_column('pressure_cathode_inlet_spare').reshape(-1, 1)
# full_data_y = file1.get_column('voltage').reshape(-1, 1)
half_lenth = int(len(full_data_x1))
half_lenth1 = int(len(full_data_x1))

x1train_control = full_data_x1[:half_lenth]
x2train = full_data_x2[:half_lenth]
x3train = full_data_x3[:half_lenth]

x1test_control = full_data_x1[:half_lenth1]
x2test = full_data_x2[:half_lenth1]
x3test = full_data_x3[:half_lenth1]

trainarray = np.concatenate((x2train, x3train), axis=1)
trainarrayfull = np.concatenate((x2train, x3train), axis=1)
testarray = np.concatenate((x2test, x3test), axis=1)
x0 = testarray[0]
#x0 = x3test[0]
#print(testarray[:, 0])
dt = 1

differentiation_method = ps.SmoothedFiniteDifference(order=1)#ps.FiniteDifference(order=2) #
optimizer = ps.STLSQ(threshold=0.02)
# cust_library_functions = [lambda x: np.sqrt(x**2), lambda x: np.exp(x), lambda x: np.exp(-x)]
# cust_library_function_names = [lambda x: 'sqrt(1-'+ x + '^2)', lambda x: 'exp(' + x + ')', lambda x: 'exp(-' + x + ')']
# cust_library_functions = [lambda x, y: np.sin(x + y), lambda x, y: np.cos(x + y)]#, lambda x, y: np.sin(x - y), lambda x, y: np.cos(x - y)]
# cust_library_function_names = [lambda x, y: 'sin(' + x + '+' + y +')', 
#                             lambda x, y: 'cos(' + x + '+' + y + ')'] 
                            # lambda x, y: 'sin(' + x + '-' + y +')', 
                            # lambda x, y: 'cos(' + x + '-' + y + ')']
cust_library_functions = [lambda x, y: x + y, lambda x, y: x - y]#, lambda x, y: np.sin(x - y), lambda x, y: np.cos(x - y)]
cust_library_function_names = [lambda x, y:  x + '+' + y, 
                            lambda x, y: x + '-' + y] 
cust_lib = ps.CustomLibrary(library_functions=cust_library_functions, function_names=cust_library_function_names)

#feature_library = cust_lib # + ps.PolynomialLibrary(degree=2)+ ps.FourierLibrary(n_frequencies=1) + cust_lib
 
feature_library = ps.PolynomialLibrary(degree=2)
model = ps.SINDy(
    differentiation_method=differentiation_method,
    feature_library=feature_library,
    optimizer=optimizer,
    feature_names=["pin", "v", "pout"],
)

model.fit(trainarray, u=x1train_control, t=dt)
model.print()
sim_lenth = len(x1test_control)
t_test = np.linspace(0, sim_lenth, sim_lenth)





simulated_data = model.simulate(x0, u=x1test_control, t=t_test)
# plt.plot(t_test, x3test, 'k', simulated_data, 'r')
print(simulated_data)
##ps.make_3d_plots(test_array)
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.suptitle('A tale of 2 subplots')

ax1.plot(t_test,testarray[:, 0], 'k', simulated_data[:, 0], 'r')
ax1.set_ylim(-2,2)
ax1.set_ylabel('Pressure Inlet')

ax2.plot(t_test,testarray[:, 1], 'k', simulated_data[:, 1], 'r')
ax2.set_xlabel('time (s)')
ax2.set_ylabel('Voltage')
ax2.set_ylim(-2,2)
plt.show()


