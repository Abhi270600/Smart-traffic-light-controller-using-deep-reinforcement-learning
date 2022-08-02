import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy import stats



threeway=[]
fourway=[]
fiveway=[]

with open('plot_reward_data3_cnn.txt') as f:
    lines = f.readlines()

for i in lines:
    threeway.append(float(i.rstrip('\n')))


with open('plot_reward_data4_cnn.txt') as f1:
    lines = f1.readlines()

for i in lines:
    fourway.append(float(i.rstrip('\n')))

with open('plot_reward_data5_cnn.txt') as f:
    lines = f.readlines()

for i in lines:
    fiveway.append(float(i.rstrip('\n')))


'''
x=[i for i in range(0,30)]
y1=threeway
y2=fourway
y3=fiveway

gradient1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(x,y1)
gradient2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(x,y2)
gradient3, intercept3, r_value3, p_value3, std_err3 = stats.linregress(x,y3)
mn=np.min(x)
mx=np.max(x)
x_1=np.linspace(mn,mx,500)
y_1=gradient1*x_1+intercept1
plt.plot(x,y1,'ob',label="3-way", color='blue')
plt.plot(x_1,y_1,'-r')
x_2=np.linspace(mn,mx,500)
y_2=gradient2*x_2+intercept2
plt.plot(x,y2,'ob',label="4-way", color='green')
plt.plot(x_2,y_2,'-r')
x_3=np.linspace(mn,mx,500)
y_3=gradient3*x_3+intercept3
plt.plot(x,y3,'ob',label="5-way", color='purple')
plt.plot(x_3,y_3,'-r')
plt.ylabel('Cumulative delay')
plt.xlabel('Episode')
plt.legend()
#plt.savefig('reward_comparision_reg.png')
plt.show()
'''

min_3 = min(threeway)
max_3 = max(threeway)

min_4 = min(fourway)
max_4 = max(fourway)

min_5 = min(fiveway)
max_5 = max(fiveway)


plt.rcParams.update({'font.size': 24})  # set bigger font size

plt.plot(threeway,label="3-way")
plt.plot(fourway,label="4-way")
plt.plot(fiveway,label="5-way")
plt.ylabel('Cumulative negative reward')
plt.xlabel('Episode')
plt.margins(0)
#plt.ylim(min(min(ann),min(cnn)),0)
fig = plt.gcf()
fig.set_size_inches(20, 11.25)
plt.legend()
plt.show()
# fig.savefig(os.path.join(self._path, 'plot_'+filename+'.png'), dpi=self._dpi)
# plt.close("all")
