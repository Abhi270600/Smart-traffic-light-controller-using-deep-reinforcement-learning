from __future__ import absolute_import
from __future__ import print_function

import os
import datetime
from shutil import copyfile

from training_simulation import Simulation
from generator import TrafficGenerator
from memory import Memory
from model import DQNAgent
from visualization import Visualization
from utils import import_train_configuration, set_sumo, set_train_path


if __name__ == "__main__":

    config = import_train_configuration(config_file='training_settings.ini')
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    path = set_train_path(config['models_path_name'])

    Model1 = DQNAgent(
      config['batch_size'],
      16,
      4
    )

    Model2 = DQNAgent(
      config['batch_size'],
      12,
      3
    )

    Model3 = DQNAgent(
      config['batch_size'],
      12,
      3
    )

    Model4 = DQNAgent(
      config['batch_size'],
      20,
      5
    )
    
    Memory1 = Memory(
        config['memory_size_max'], 
        config['memory_size_min']
    )

    Memory2 = Memory(
        config['memory_size_max'], 
        config['memory_size_min']
    )

    Memory3 = Memory(
        config['memory_size_max'],
        config['memory_size_min']
    )

    Memory4 = Memory(
        config['memory_size_max'],
        config['memory_size_min']
    )

    TrafficGen = TrafficGenerator(
        config['max_steps'], 
        config['n_cars_generated'],
        config['n_low'],
        config['n_high']
    )

    Visualization = Visualization(
        path, 
        dpi=96
    )
        
    Simulation = Simulation(
        Model1,
        Memory1,
        Model2,
        Memory2,
        Model3,
        Memory3,
        Model4,
        Memory4,
        TrafficGen,
        sumo_cmd,
        config['gamma'],
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration'],
        config['training_epochs']
    )
    
    episode = 0
    timestamp_start = datetime.datetime.now()
    #total_episodes = 100
    
    while episode < config['total_episodes']:
        print('\n----- Episode', str(episode+1), 'of', str(config['total_episodes']))
        epsilon = 1.0 - (episode / config['total_episodes'])  # set the epsilon for this episode according to epsilon-greedy policy
        simulation_time, training_time = Simulation.run(episode, epsilon)  # run the simulation
        print('Simulation time:', simulation_time, 's - Training time:', training_time, 's - Total:', round(simulation_time+training_time, 1), 's')
        episode += 1

    print("\n----- Start time:", timestamp_start)
    print("----- End time:", datetime.datetime.now())
    print("----- Session info saved at:", path)

    Model1.save_model(path, '1')
    Model2.save_model(path, '2')
    Model3.save_model(path, '3')
    Model4.save_model(path, '4')

    copyfile(src='training_settings.ini', dst=os.path.join(path, 'training_settings.ini'))

    Visualization.save_data_and_plot(data=Simulation._reward_store, filename='reward', xlabel='Episode', ylabel='Cumulative negative reward')
    Visualization.save_data_and_plot(data=Simulation._cumulative_wait_store, filename='delay', xlabel='Episode', ylabel='Cumulative delay (s)')
    Visualization.save_data_and_plot(data=Simulation._avg_queue_length_store, filename='queue', xlabel='Episode', ylabel='Average queue length (vehicles)')
