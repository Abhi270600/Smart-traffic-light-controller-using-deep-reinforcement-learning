import numpy as np
import math

class TrafficGenerator:
    def __init__(self, max_steps, n_cars_generated, n_low, n_high):
        self._n_cars_generated = n_cars_generated  # how many cars per episode
        self._max_steps = max_steps
        self._n_low = n_low
        self._n_high = n_high

    def generate_routefile(self, seed):
        """
        Generation of the route of every car for one episode
        """
        np.random.seed(seed)  # make tests reproducible

        # the generation of cars is distributed according to a weibull distribution
        timings = np.random.weibull(2, self._n_cars_generated)
        timings = np.sort(timings)

        # reshape the distribution to fit the interval 0:max_steps
        car_gen_steps = []
        min_old = math.floor(timings[1])
        max_old = math.ceil(timings[-1])
        min_new = 0
        max_new = self._max_steps
        for value in timings:
            car_gen_steps = np.append(car_gen_steps, ((max_new - min_new) / (max_old - min_old)) * (value - max_old) + max_new)

        car_gen_steps = np.rint(car_gen_steps)  # round every value to int -> effective steps when a car will be generated

        # produce the file for cars generation, one car per line
        # p_low = self._n_low/self._n_cars_generated

        p_high = self._n_high/self._n_cars_generated

        with open("intersection/episode_routes.rou.xml", "w") as routes:
            print("""<routes>
            <vTypeDistribution id="low_priority">
                <vType id="standard_car" vClass="passenger" guiShape="passenger" speedDev="0.2" latAlignment="compact" sigma="0.5" probability="0.5" />
                <vType id="bike" vClass="motorcycle" guiShape="motorcycle" speedDev="0.2" latAlignment="compact" sigma="0.5" probability="0.1"/>
                <vType id="bus" vClass="bus" guiShape="truck" speedDev="0.2" latAlignment="compact" sigma="0.5" probability="0.2"/>
                <vType id="taxi" vClass="taxi" guiShape="passenger/sedan" speedDev="0.2" latAlignment="compact" sigma="0.5" color = "255,0,0" probability="0.2"/>
            </vTypeDistribution>

            <vTypeDistribution id="high_priority">
                <vType id="amb" vClass="emergency" guiShape="emergency" speedDev="0.2" latAlignment="compact" probability="0.4"/>
                <vType id="pol" vClass="authority" guiShape="police" speedDev="0.4" latAlignment="compact" probability="0.4"/>
                <vType id="fire" vClass="emergency" guiShape="firebrigade" speedDev="0.4" latAlignment="compact" probability="0.2"/>
            </vTypeDistribution>

            <route id="A_B" edges="A2TL TL2B"/>
            <route id="A_C" edges="A2TL TL2C"/>
            <route id="A_D" edges="A2TL TL2D"/>
            <route id="A_E" edges="A2TL TL2E"/>
            
            <route id="B_A" edges="B2TL TL2A"/>
            <route id="B_C" edges="B2TL TL2C"/>
            <route id="B_D" edges="B2TL TL2D"/>
            <route id="B_E" edges="B2TL TL2E"/>

            <route id="C_A" edges="C2TL TL2A"/>
            <route id="C_B" edges="C2TL TL2B"/>
            <route id="C_D" edges="C2TL TL2D"/>
            <route id="C_E" edges="C2TL TL2E"/>
            
            <route id="D_A" edges="D2TL TL2A"/>
            <route id="D_B" edges="D2TL TL2B"/>
            <route id="D_C" edges="D2TL TL2C"/>
            <route id="D_E" edges="D2TL TL2E"/>

            <route id="E_A" edges="E2TL TL2A"/>
            <route id="E_B" edges="E2TL TL2B"/>
            <route id="E_C" edges="E2TL TL2C"/>
            <route id="E_D" edges="E2TL TL2D"/>""", file=routes)

            for car_counter, step in enumerate(car_gen_steps):
                straight_or_turn = np.random.uniform()
                low_or_high = np.random.uniform()
                if low_or_high <= p_high:
                    veh_type = "high_priority"
                    pr='P'
                else:
                    veh_type = "low_priority"
                    pr=''

                route = np.random.randint(1, 21)  # choose a random source & destination
                if route == 1:
                    print('    <vehicle id="%sA_B%i" type="%s" route="A_B" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 2:
                    print('    <vehicle id="%sA_C%i" type="%s" route="A_C" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 3:
                    print('    <vehicle id="%sA_D%i" type="%s" route="A_D" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 4:
                    print('    <vehicle id="%sA_E%i" type="%s" route="A_E" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 5:
                    print('    <vehicle id="%sB_A%i" type="%s" route="B_A" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 6:
                    print('    <vehicle id="%sB_C%i" type="%s" route="B_C" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 7:
                    print('    <vehicle id="%sB_D%i" type="%s" route="B_D" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 8:
                    print('    <vehicle id="%sB_E%i" type="%s" route="B_E" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 9:
                    print('    <vehicle id="%sC_A%i" type="%s" route="C_A" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 10:
                    print('    <vehicle id="%sC_B%i" type="%s" route="C_B" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 11:
                    print('    <vehicle id="%sC_D%i" type="%s" route="C_D" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 12:
                    print('    <vehicle id="%sC_E%i" type="%s" route="C_E" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 13:
                    print('    <vehicle id="%sD_A%i" type="%s" route="D_A" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 14:
                    print('    <vehicle id="%sD_B%i" type="%s" route="D_B" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 15:
                    print('    <vehicle id="%sD_C%i" type="%s" route="D_C" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 16:
                    print('    <vehicle id="%sD_E%i" type="%s" route="D_E" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 17:
                    print('    <vehicle id="%sE_A%i" type="%s" route="E_A" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 18:
                    print('    <vehicle id="%sE_B%i" type="%s" route="E_B" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                elif route == 19:
                    print('    <vehicle id="%sE_C%i" type="%s" route="E_C" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)
                else:
                    print('    <vehicle id="%sE_D%i" type="%s" route="E_D" depart="%s" departLane="random" departSpeed="10" />' % (pr, car_counter, veh_type, step), file=routes)

            print("</routes>", file=routes)


call= TrafficGenerator(5400,1000,10,900)
call.generate_routefile(0)
