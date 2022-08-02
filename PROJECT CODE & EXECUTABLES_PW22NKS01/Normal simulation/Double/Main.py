import traci
import timeit
import os
from shutil import copyfile

from generator import TrafficGenerator
from visualization import Visualization
from utils import import_test_configuration, set_sumo, set_test_path

PHASE_N_GREEN = 0
PHASE_N_YELLOW = 1
PHASE_E_GREEN = 2
PHASE_E_YELLOW = 3
PHASE_S_GREEN = 4
PHASE_S_YELLOW = 5
PHASE_W_GREEN = 6
PHASE_W_YELLOW = 7

class Simulation:
    def __init__(self, TrafficGen, sumo_cmd, max_steps, green_duration, yellow_duration):
        self._TrafficGen = TrafficGen
        self._step = 0
        self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration

        self._reward_episode1 = []
        self._queue_length_episode1 = []

        self._reward_episode2 = []
        self._queue_length_episode2 = []

    def run(self, episode):
        start_time = timeit.default_timer()

        # first, generate the route file for this simulation and set up sumo
        self._TrafficGen.generate_routefile(seed=episode)
        traci.start(self._sumo_cmd)
        print("Simulating...")

        # inits
        self._step = 0
        self._waiting_times1 = {}
        old_total_wait1 = 0
        old_action1 = -1 # dummy init

        self._waiting_times2 = {}
        old_total_wait2 = 0
        old_action2 = -1  # dummy init

        while self._step < self._max_steps:
            current_total_wait1, current_total_wait2 = self._collect_waiting_times()

            reward1 = old_total_wait1 - current_total_wait1
            reward2 = old_total_wait2 - current_total_wait2

            # choose the light phase to activate, based on the current state of the intersection
            action1 = (old_action1+1)%4
            action2 = (old_action2+1)%4

            # if the chosen phase is different from the last phase, activate the yellow phase
            if self._step != 0 and old_action1 != action1:
                self._set_yellow_phase(old_action1, 'TL1')
            if self._step != 0 and old_action2 != action2:
                self._set_yellow_phase(old_action2, 'TL2')

            self._simulate(self._yellow_duration)

            # execute the phase selected before
            self._set_green_phase(action1, 'TL1')
            self._set_green_phase(action2, 'TL2')

            self._simulate(self._green_duration)

            # saving variables for later & accumulate reward

            old_action1 = action1
            old_action2 = action2

            old_total_wait1 = current_total_wait1
            old_total_wait2 = current_total_wait2

            self._reward_episode1.append(reward1)
            self._reward_episode2.append(reward2)

        # print()
        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time
    
    def _simulate(self, steps_todo):
        """
        Execute steps in sumo while gathering statistics
        """
        if (self._step + steps_todo) >= self._max_steps:  # do not do more steps than the maximum allowed number of steps
            steps_todo = self._max_steps - self._step

        while steps_todo > 0:
            traci.simulationStep()  # simulate 1 step in sumo
            self._step += 1  # update the step counter
            steps_todo -= 1
            queue_length1, queue_length2 = self._get_queue_length()
            self._queue_length_episode1.append(queue_length1)
            self._queue_length_episode2.append(queue_length2)

    def _collect_waiting_times(self):
        incoming_roads1 = ["A2TL1", "B2TL1", "TL22TL1", "F2TL1"]
        incoming_roads2 = ["C2TL2", "D2TL2", "E2TL2", "TL12TL2"]

        car_list = traci.vehicle.getIDList()
        for car_id in car_list:
            wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            # get the road id where the car is located
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

        total_waiting_time1 = sum(self._waiting_times1.values())
        total_waiting_time2 = sum(self._waiting_times2.values())

        return [total_waiting_time1, total_waiting_time2]

    def _set_yellow_phase(self, old_action, intersection):
        # obtain the yellow phase code, based on the old action (ref on environment.net.xml)
        yellow_phase_code = old_action * 2 + 1
        traci.trafficlight.setPhase(intersection, yellow_phase_code)

    def _set_green_phase(self, action_number, intersection):
        """
        Activate the correct green light combination in sumo
        """
        if action_number == 0:
            traci.trafficlight.setPhase(intersection, PHASE_N_GREEN)
        elif action_number == 1:
            traci.trafficlight.setPhase(intersection, PHASE_E_GREEN)
        elif action_number == 2:
            traci.trafficlight.setPhase(intersection, PHASE_S_GREEN)
        else:
            traci.trafficlight.setPhase(intersection, PHASE_W_GREEN)

    def _get_queue_length(self):
        """
        Retrieve the number of cars with speed = 0 in every incoming lane
        """
        halt_N1 = traci.edge.getLastStepHaltingNumber("A2TL1")
        halt_S1 = traci.edge.getLastStepHaltingNumber("B2TL1")
        halt_E1 = traci.edge.getLastStepHaltingNumber("TL22TL1")
        halt_W1 = traci.edge.getLastStepHaltingNumber("F2TL1")

        halt_N2 = traci.edge.getLastStepHaltingNumber("C2TL2")
        halt_S2 = traci.edge.getLastStepHaltingNumber("D2TL2")
        halt_E2 = traci.edge.getLastStepHaltingNumber("E2TL2")
        halt_W2 = traci.edge.getLastStepHaltingNumber("TL12TL2")

        queue_length1 = halt_N1 + halt_S1 + halt_E1 + halt_W1
        queue_length2 = halt_N2 + halt_S2 + halt_E2 + halt_W2
        return [queue_length1, queue_length2]
    
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
        config['yellow_duration'],
    )

    print('\n----- Test episode')
    simulation_time = Simulation.run(config['episode_seed'])  # run the simulation
    print('Simulation time:', simulation_time, 's')

    print("----- Testing info saved at:", plot_path)

    copyfile(src='testing_settings.ini', dst=os.path.join(plot_path, 'testing_settings.ini'))

    Visualization.save_data_and_plot(data=Simulation._reward_episode1, filename='reward1', xlabel='Action step', ylabel='Reward')
    Visualization.save_data_and_plot(data=Simulation._queue_length_episode1, filename='queue1', xlabel='Step', ylabel='Queue lenght (vehicles)')

    Visualization.save_data_and_plot(data=Simulation._reward_episode2, filename='reward2', xlabel='Action step', ylabel='Reward')
    Visualization.save_data_and_plot(data=Simulation._queue_length_episode2, filename='queue2', xlabel='Step', ylabel='Queue lenght (vehicles)')
