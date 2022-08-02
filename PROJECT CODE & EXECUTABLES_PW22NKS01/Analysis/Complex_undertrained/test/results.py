import matplotlib.pyplot as plt

queue_data_10=[]
queue_data_60=[]

with open('plot_queue_data_10.txt') as f:
    lines = f.readlines()
    
for i in lines:
    queue_data_10.append(float(i.rstrip('\n')))


with open('plot_queue_data_60.txt') as f1:
    lines = f1.readlines()

for i in lines:
    queue_data_60.append(float(i.rstrip('\n')))



min_val_normal = min(queue_data_10)
max_val_normal = max(queue_data_10)

min_val_trained = min(queue_data_60)
max_val_trained = max(queue_data_60)


plt.rcParams.update({'font.size': 24})  # set bigger font size

plt.plot(queue_data_10,label="Partially_trained")
plt.plot(queue_data_60,label="Fully_trained")
plt.ylabel('Queue length (all vehicles)')
plt.xlabel('Action step')
plt.margins(0)
# plt.ylim(min_val_normal - 0.05 * abs(min_val_normal), max_val_normal + 0.05 * abs(max_val_normal))
fig = plt.gcf()
fig.set_size_inches(20, 11.25)
plt.legend()
plt.show()
#fig.savefig(os.path.join(self._path, 'plot_'+filename+'.png'), dpi=self._dpi)
#plt.close("all")

