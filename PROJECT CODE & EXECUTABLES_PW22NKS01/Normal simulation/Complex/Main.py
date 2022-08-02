import traci
import timeit
import os
from shutil import copyfile

from generator import TrafficGenerator
from visualization import Visualization
from utils import import_test_configuration, set_sumo, set_test_path


PHASE_N_GREEN = 0  # action 0 code 00
PHASE_N_YELLOW = 1
PHASE_E_GREEN = 2  # action 1 code 01
PHASE_E_YELLOW = 3
PHASE_S_GREEN = 4  # action 2 code 10
PHASE_S_YELLOW = 5  # action*2 +1
PHASE_W_GREEN = 6  # action 3 code 11
PHASE_W_YELLOW = 7  # action*2 + 1
PHASE_J_GREEN = 8  # action 3 code 11
PHASE_J_YELLOW = 9  # action*2 + 1

class Simulation:
    def __init__(self, TrafficGen, sumo_cmd, max_steps, green_duration, yellow_duration):
        self._TrafficGen = TrafficGen
        self._step = 0
        self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        
        self._reward_episode1 = []
        self._reward_episode2 = []
        self._reward_episode3 = []
        self._reward_episode4 = []

        self._reward_episode = []

        self._queue_length_episode1 = []
        self._queue_length_episode2 = []
        self._queue_length_episode3 = []
        self._queue_length_episode4 = []

        self._queue_length_episode = []

    def run(self, episode):
        start_time = timeit.default_timer()

        # first, generate the route file for this simulation and set up sumo
        self._TrafficGen.generate_routefile(seed=episode)
        traci.start(self._sumo_cmd)
        print("Simulating...")

        # inits
        self._step = 0

        self._waiting_times1 = {}
        self._waiting_times2 = {}
        self._waiting_times3 = {}
        self._waiting_times4 = {}

        old_total_wait1 = 0
        old_total_wait2 = 0
        old_total_wait3 = 0
        old_total_wait4 = 0

        old_action1 = -1  # dummy init
        old_action2 = -1  # dummy init
        old_action3 = -1  # dummy init
        old_action4 = -1  # dummy init

        while self._step < self._max_steps:

            current_total_wait1, current_total_wait2, current_total_wait3, current_total_wait4 = self._collect_waiting_times()
            reward1 = old_total_wait1 - current_total_wait1
            reward2 = old_total_wait2 - current_total_wait2
            reward3 = old_total_wait3 - current_total_wait3
            reward4 = old_total_wait4 - current_total_wait4

            # choose the light phase to activate, based on the current state of the intersection

            action1 = (old_action1+1)%4
            action2 = (old_action2+1)%3
            action3 = (old_action3+1)%3
            action4 = (old_action4+1)%5

            if self._step != 0 and old_action1 != action1:
                self._set_yellow_phase(old_action1, 'TL1')
            if self._step != 0 and old_action2 != action2:
                self._set_yellow_phase(old_action2, 'TL2')
            if self._step != 0 and old_action3 != action3:
                self._set_yellow_phase(old_action3, 'TL3')
            if self._step != 0 and old_action4 != action4:
                self._set_yellow_phase(old_action4, 'TL4')

            if self._step != 0:
                self._simulate(self._yellow_duration)

            self._set_green_phase(action1, 'TL1')
            self._set_green_phase(action2, 'TL2')
            self._set_green_phase(action3, 'TL3')
            self._set_green_phase(action4, 'TL4')

            self._simulate(self._green_duration)

            old_action1 = action1
            old_action2 = action2
            old_action3 = action3
            old_action4 = action4

            old_total_wait1 = current_total_wait1
            old_total_wait2 = current_total_wait2
            old_total_wait3 = current_total_wait3
            old_total_wait4 = current_total_wait4

            self._reward_episode1.append(reward1)
            self._reward_episode2.append(reward2)
            self._reward_episode3.append(reward3)
            self._reward_episode4.append(reward4)

            self._reward_episode.append(reward1+reward2+reward3+reward4)

        # print()
        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time


    def _simulate(self, steps_todo):
        if (self._step + steps_todo) >= self._max_steps:
            steps_todo = self._max_steps - self._step

        while steps_todo > 0:
            traci.simulationStep()  # simulate 1 step in sumo
            self._step += 1  # update the step counter
            steps_todo -= 1
            queue_length1, queue_length2, queue_length3, queue_length4 = self._get_queue_length()

            self._queue_length_episode1.append(queue_length1)
            self._queue_length_episode2.append(queue_length2)
            self._queue_length_episode3.append(queue_length3)
            self._queue_length_episode4.append(queue_length4)

            self._queue_length_episode.append(queue_length1+queue_length2+queue_length3+queue_length4)

    def _collect_waiting_times(self):
        incoming_roads1 = ["A2TL1", "B2TL1", "C2TL1", "TL22TL1"]
        incoming_roads2 = ["TL12TL2", "TL32TL2", "TL42TL2"]
        incoming_roads3 = ["G2TL3", "TL22TL3", "TL42TL3"]
        incoming_roads4 = ["D2TL4", "E2TL4", "F2TL4", "TL22TL4", "TL32TL4"]

        car_list = traci.vehicle.getIDList()
        for car_id in car_list:
            wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            road_id = traci.vehicle.getRoadID(car_id)

            if road_id in incoming_roads1:  # consider only the waiting times of cars in incoming roads
                self._waiting_times1[car_id] = wait_time
            else:
                if car_id in self._waiting_times1:  # a car that was tracked has cleared the intersection
                    del self._waiting_times1[car_id]

            if road_id in incoming_roads2:  # consider only the waiting times of cars in incoming roads
                self._waiting_times2[car_id] = wait_time
            else:
                if car_id in self._waiting_times2:  # a car that was tracked has cleared the intersection
                    del self._waiting_times2[car_id]

            if road_id in incoming_roads3:  # consider only the waiting times of cars in incoming roads
                self._waiting_times3[car_id] = wait_time
            else:
                if car_id in self._waiting_times3:  # a car that was tracked has cleared the intersection
                    del self._waiting_times3[car_id]

            if road_id in incoming_roads4:  # consider only the waiting times of cars in incoming roads
                self._waiting_times4[car_id] = wait_time
            else:
                if car_id in self._waiting_times4:  # a car that was tracked has cleared the intersection
                    del self._waiting_times4[car_id]

        total_waiting_time1 = sum(self._waiting_times1.values())
        total_waiting_time2 = sum(self._waiting_times2.values())
        total_waiting_time3 = sum(self._waiting_times3.values())
        total_waiting_time4 = sum(self._waiting_times4.values())

        return [total_waiting_time1, total_waiting_time2, total_waiting_time3, total_waiting_time4]

    def _set_yellow_phase(self, old_action, intersection):
        yellow_phase_code = old_action * 2 + 1
        traci.trafficlight.setPhase(intersection, yellow_phase_code)

    def _set_green_phase(self, action_number, intersection):
        if action_number == 0:
            traci.trafficlight.setPhase(intersection, PHASE_N_GREEN)
        elif action_number == 1:
            traci.trafficlight.setPhase(intersection, PHASE_E_GREEN)
        elif action_number == 2:
            traci.trafficlight.setPhase(intersection, PHASE_S_GREEN)
        elif action_number == 3:
            traci.trafficlight.setPhase(intersection, PHASE_W_GREEN)
        else:
            traci.trafficlight.setPhase(intersection, PHASE_J_GREEN)

    def _get_queue_length(self):
        halt_N1 = traci.edge.getLastStepHaltingNumber("A2TL1")
        halt_S1 = traci.edge.getLastStepHaltingNumber("B2TL1")
        halt_E1 = traci.edge.getLastStepHaltingNumber("TL22TL1")
        halt_W1 = traci.edge.getLastStepHaltingNumber("C2TL1")

        halt_N2 = traci.edge.getLastStepHaltingNumber("TL12TL2")
        halt_S2 = traci.edge.getLastStepHaltingNumber("TL32TL2")
        halt_E2 = traci.edge.getLastStepHaltingNumber("TL42TL2")

        halt_N3 = traci.edge.getLastStepHaltingNumber("G2TL3")
        halt_S3 = traci.edge.getLastStepHaltingNumber("TL22TL3")
        halt_E3 = traci.edge.getLastStepHaltingNumber("TL42TL3")

        halt_N4 = traci.edge.getLastStepHaltingNumber("TL22TL4")
        halt_S4 = traci.edge.getLastStepHaltingNumber("D2TL4")
        halt_E4 = traci.edge.getLastStepHaltingNumber("E2TL4")
        halt_W4 = traci.edge.getLastStepHaltingNumber("F2TL4")
        halt_J4 = traci.edge.getLastStepHaltingNumber("TL32TL4")

        queue_length1 = halt_N1 + halt_S1 + halt_E1 + halt_W1
        queue_length2 = halt_N2 + halt_S2 + halt_E2
        queue_length3 = halt_N3 + halt_S3 + halt_E3
        queue_length4 = halt_N4 + halt_S4 + halt_E4 + halt_W4 + halt_J4

        return [queue_length1, queue_length2, queue_length3, queue_length4]


    # def _save_episode_stats(self):
    #     self._cumulative_wait_store.append(self._sum_waiting_time)  # total number of seconds waited by cars in this episode
    #     self._avg_queue_length_store.append(self._sum_queue_length / self._max_steps)  # average number of queued cars per step, in this episode

    @property
    def queue_length_episode(self):
        return self._queue_length_episode


    @property
    def reward_episode(self):
        return self._reward_episode


if __name__ == "__main__":
    config = import_test_configuration(config_file='testing_settings.ini')
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    model_path, plot_path = set_test_path(config['models_path_name'], config['model_to_test'])

    TrafficGen = TrafficGenerator(
        config['max_steps'], 
        config['n_cars_generated'],
        config['n_low'],
        config['n_high']
    )

    Visualization = Visualization(
        plot_path, 
        dpi=96
    )

    Simulation = Simulation(
        TrafficGen,
        sumo_cmd,
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration']
    )

    print('\n----- Test episode')
    simulation_time = Simulation.run(config['episode_seed'])  # run the simulation
    print('Simulation time:', simulation_time, 's')

    print("----- Testing info saved at:", plot_path)

    copyfile(src='testing_settings.ini', dst=os.path.join(plot_path, 'testing_settings.ini'))

    # Visualization.save_data_and_plot(data=Simulation._reward_episode1, filename='reward1', xlabel='Action step', ylabel='Reward')
    # Visualization.save_data_and_plot(data=Simulation._queue_length_episode1, filename='queue1', xlabel='Step', ylabel='Queue lenght (vehicles)')

    # Visualization.save_data_and_plot(data=Simulation._reward_episode2, filename='reward2', xlabel='Action step', ylabel='Reward')
    # Visualization.save_data_and_plot(data=Simulation._queue_length_episode2, filename='queue2', xlabel='Step', ylabel='Queue lenght (vehicles)')

    # Visualization.save_data_and_plot(data=Simulation._reward_episode3, filename='reward3', xlabel='Action step', ylabel='Reward')
    # Visualization.save_data_and_plot(data=Simulation._queue_length_episode3, filename='queue3', xlabel='Step', ylabel='Queue lenght (vehicles)')

    # Visualization.save_data_and_plot(data=Simulation._reward_episode4, filename='reward4', xlabel='Action step', ylabel='Reward')
    # Visualization.save_data_and_plot(data=Simulation._queue_length_episode4, filename='queue4', xlabel='Step', ylabel='Queue lenght (vehicles)')

    Visualization.save_data_and_plot(data=Simulation._reward_episode, filename='reward', xlabel='Action step', ylabel='Reward')
    Visualization.save_data_and_plot(data=Simulation._queue_length_episode, filename='queue', xlabel='Step', ylabel='Queue lenght (vehicles)')
