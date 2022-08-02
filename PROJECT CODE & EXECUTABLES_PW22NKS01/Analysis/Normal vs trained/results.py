import matplotlib.pyplot as plt

queue_trained=[]
queue_normal=[]

with open('plot_queue_data.txt') as f:
    lines = f.readlines()
    
for i in lines:
    queue_trained.append(float(i.rstrip('\n')))


with open('plot_queue_data_normal.txt') as f1:
    lines = f1.readlines()

for i in lines:
    queue_normal.append(float(i.rstrip('\n')))



min_val_normal = min(queue_normal)
max_val_normal = max(queue_normal)

min_val_trained = min(queue_trained)
max_val_trained = max(queue_trained)


plt.rcParams.update({'font.size': 24})  # set bigger font size

plt.plot(queue_normal,label="normal")
plt.plot(queue_trained,label="trained")
plt.ylabel('Average queue length')
plt.xlabel('Action step')
plt.margins(0)
plt.ylim(min_val_normal - 0.05 * abs(min_val_normal), max_val_normal + 0.05 * abs(max_val_normal))
fig = plt.gcf()
fig.set_size_inches(20, 11.25)
plt.legend()
plt.show()
#fig.savefig(os.path.join(self._path, 'plot_'+filename+'.png'), dpi=self._dpi)
#plt.close("all")

