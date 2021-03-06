from problems import ImbalancedProblem, SequentialProblem, MMcProblem, MinedProblem
from simulator import Simulator, Reporter, EventLogReporterElement, TimeUnit
from planners import GreedyPlanner, HeuristicPlanner, ImbalancedPredictivePlanner, PredictiveHeuristicPlanner
from predicters import ImbalancedPredicter, PerfectPredicter, MeanPredicter
from visualizers import boxplot, line_with_ci
from miners import mine_problem
import pandas
import numpy as np


def try_mmc():
    problem_instances = []
    for i in range(20):
        problem_instances.append(MMcProblem().from_generator(51000))  # Running for longer than the simulation time, so we do not run out of tasks
    planner = GreedyPlanner()
    reporter = Reporter(10000)
    results = Simulator.replicate(problem_instances, planner, reporter, 50000)
    print(Reporter.aggregate(results))


# Simulating several planners and predicters for the imbalanced problem
def try_several_planners():
    problem_instances = []
    for i in range(20):
        problem_instances.append(ImbalancedProblem(spread=1.0).from_generator(51000))  # Running for longer than the simulation time, so we do not run out of tasks
    print(Reporter.aggregate(Simulator.replicate(problem_instances, GreedyPlanner(), Reporter(10000), 50000)))
    print(Reporter.aggregate(Simulator.replicate(problem_instances, HeuristicPlanner(), Reporter(10000), 50000)))
    print(Reporter.aggregate(Simulator.replicate(problem_instances, ImbalancedPredictivePlanner(ImbalancedPredicter), Reporter(10000), 50000)))
    print(Reporter.aggregate(Simulator.replicate(problem_instances, ImbalancedPredictivePlanner(PerfectPredicter), Reporter(10000), 50000)))


# Comparing two spreads of the imbalanced problem in a box plot
def try_comparison():
    problem_instances = []
    for i in range(5):
        problem_instances.append(ImbalancedProblem(spread=1.0).from_generator(51000))  # Running for longer than the simulation time, so we do not run out of tasks
    spread10 = Simulator.replicate(problem_instances, HeuristicPlanner(), Reporter(10000), 50000)
    problem_instances = []
    for i in range(5):
        problem_instances.append(ImbalancedProblem(spread=0.5).from_generator(51000))  # Running for longer than the simulation time, so we do not run out of tasks
    spread05 = Simulator.replicate(problem_instances, HeuristicPlanner(), Reporter(10000), 50000)
    boxplot({'spread 0.5': spread05['task proc time'], 'spread 1.0': spread10['task proc time']})


# Comparing multiple spreads of the imbalanced problem in a line plot
def try_multiple_comparison():
    results = dict()
    for spread in np.arange(0.5, 1.01, 0.05):
        problem_instances = []
        for i in range(5):
            problem_instances.append(ImbalancedProblem(spread=spread).from_generator(51000))  # Running for longer than the simulation time, so we do not run out of tasks
        result = Reporter.aggregate(Simulator.replicate(problem_instances, HeuristicPlanner(), Reporter(10000), 50000))
        results[spread] = result['task wait time']
    line_with_ci(results)


# Printing a trace for the sequential problem
def try_execution_traces():
    problem_instance = SequentialProblem().from_generator(51000)  # Running for longer than the simulation time, so we do not run out of tasks
    reporter = Reporter(warmup=0, reporter_elements=[EventLogReporterElement("../temp/my_log.csv", TimeUnit.MINUTES)])
    simulator = Simulator(problem_instance, reporter, GreedyPlanner())
    simulator.simulate(1000)


# Mining a problem from an event log and saving it to file
def try_mine_problem_generator():
    log = pandas.read_csv("./resources/BPI Challenge 2017 - clean.zip")
    problem = mine_problem(log)
    problem.save_generator("../temp/BPI Challenge 2017 - generator.pickle")


# Load a mined problem from a file, generate a problem instance
def try_generate_mined_problem_instance():
    problem = MinedProblem.generator_from_file("../temp/BPI Challenge 2017 - generator.pickle")
    problem_instance = problem.from_generator(24*30*13)  # Running for longer than the simulation time, so we do not run out of tasks
    problem_instance.save_instance("../temp/BPI Challenge 2017 - instance.pickle")


# Load a mined problem from file, simulating it and saving the log
def try_simulate_mined_problem():
    problem_instance = MinedProblem.from_file("../temp/BPI Challenge 2017 - instance.pickle")
    reporter = Reporter(warmup=0, reporter_elements=[EventLogReporterElement("../temp/BPI Challenge 2017 - simulated.csv", TimeUnit.HOURS)])
    simulator = Simulator(problem_instance, reporter, PredictiveHeuristicPlanner(MeanPredicter(), 10, 0.1))
    simulator.simulate(24*30*12)


def main():
    # try_mmc()
    # try_several_planners()
    # try_comparison()
    # try_multiple_comparison()
    # try_execution_traces()
    try_mine_problem_generator()
    try_generate_mined_problem_instance()
    try_simulate_mined_problem()


if __name__ == "__main__":
    main()
