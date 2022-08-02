import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy import stats



ann=[]
cnn=[]


with open('plot_delay_data_ann.txt') as f:
    lines = f.readlines()

for i in lines:
    ann.append(float(i.rstrip('\n')))


with open('plot_delay_data_cnn.txt') as f1:
    lines = f1.readlines()

for i in lines:
    cnn.append(float(i.rstrip('\n')))


x=[i for i in range(0,30)]
y1=ann
y2=cnn

gradient1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(x,y1)
gradient2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(x,y2)
mn=np.min(x)
mx=np.max(x)
x_1=np.linspace(mn,mx,500)
y_1=gradient1*x_1+intercept1
plt.plot(x,y1,'ob',label="ANN", color='blue')
plt.plot(x_1,y_1,'-r')
x_2=np.linspace(mn,mx,500)
y_2=gradient2*x_2+intercept2
plt.plot(x,y2,'ob',label="CNN", color='green')
plt.plot(x_2,y_2,'-r')
plt.ylabel('Cumulative delay(s)')
plt.xlabel('Episode')
plt.legend()
plt.savefig('reward_comparision_reg.png')
plt.show()

'''
min_ann = min(ann)
max_ann = max(ann)

min_cnn = min(cnn)
max_cnn = max(cnn)


plt.rcParams.update({'font.size': 24})  # set bigger font size

plt.plot(ann,label="ANN")
plt.plot(cnn,label="CNN")
plt.ylabel('Cumulative delay(s)')
plt.xlabel('Episode')
plt.margins(0)
#plt.ylim(min(min(ann),min(cnn)),0)
fig = plt.gcf()
fig.set_size_inches(20, 11.25)
plt.legend()
plt.show()
# fig.savefig(os.path.join(self._path, 'plot_'+filename+'.png'), dpi=self._dpi)
# plt.close("all")
'''

