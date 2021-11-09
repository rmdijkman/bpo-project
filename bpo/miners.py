import pandas
from problems import MinedProblem


def mine_problem(log, task_type_filter=None, datetime_format="%Y/%m/%d %H:%M:%S", min_resource_count=2):
    """
    Mines a problem and returns it as a :class:`.Problem` that can be simulated.
    The log from which the model is mined must at least have the columns
    Case ID, Activity, Resource, Start Timestamp, Complete Timestamp,
    which identify the corresponding event log information. Activity labels
    are the same as Task Types for the purposes of the problem definition.

    :param log: a pandas dataframe from which the problem must be mined.
    :param task_type_filter: a function that takes the name of a task type/ activity
                             and returns if it should be included, or None to include all task types.
    :param datetime_format: the datetime format the Start Timestamp and Complete Timestamp columns use.
    :param min_resource_count: the minimum number of times a resource must have executed a task
                               of a particular type, for it to be considered in the pool of resources for
                               the task type. This must be greater than 1, otherwise the standard deviation
                               of the processing time cannot be computed.
    :return: a :class:`.Problem`.
    """

    # Mine the task types
    # Mine the resources
    # Mine the initial task type distribution
    # Mine the next task type distribution per task type
    # Mine the interarrival time
    # Mine the resource pool per task type
    # Mine the processing time distribution per task_type/resource combination
    # TODO: Data distribution is empty for now, future work

    df = log.copy()
    task_types = df['Activity'].unique()
    df['Start Timestamp'] = pandas.to_datetime(df['Start Timestamp'], format=datetime_format)
    df['Complete Timestamp'] = pandas.to_datetime(df['Complete Timestamp'], format=datetime_format)
    df['Duration'] = df[['Start Timestamp', 'Complete Timestamp']].apply(lambda x: (x[1]-x[0]).total_seconds()/3600, axis=1)
    if task_type_filter is not None:
        task_types = [tt for tt in task_types if task_type_filter(tt)]
    resources = df['Resource'].unique()
    df_cases = df.groupby('Case ID').agg({'Start Timestamp': 'min', 'Activity': lambda x: list(x)})
    df_cases = df_cases.rename(columns={'Activity': 'Trace'})
    df_cases = df_cases.sort_values(by='Start Timestamp')
    initial_tasks = dict()
    following_task = dict()
    interarrival_times = []
    last_arrival_time = None
    for index, row in df_cases.iterrows():
        if last_arrival_time is not None:
            interarrival_times.append((row['Start Timestamp'] - last_arrival_time).total_seconds()/3600)
        last_arrival_time = row['Start Timestamp']
        if not row['Trace'][0] in initial_tasks.keys():
            initial_tasks[row['Trace'][0]] = 0
        initial_tasks[row['Trace'][0]] += 1
        for i in range(len(row['Trace'])):
            predecessor = row['Trace'][i]
            if i+1 >= len(row['Trace']):
                successor = None
            else:
                successor = row['Trace'][i+1]
            if not (predecessor, successor) in following_task:
                following_task[(predecessor, successor)] = 0
            following_task[(predecessor, successor)] += 1
    mean_interarrival_time = sum(interarrival_times)/len(interarrival_times)  # Assuming exponential distribution, so we only need the mean
    initial_task_distribution = []
    for it in initial_tasks:
        initial_task_distribution.append((initial_tasks[it]/len(df_cases), it))        
    next_task_distribution = dict()
    task_occurrences = dict()
    for (predecessor, successor) in following_task:
        if predecessor not in next_task_distribution.keys():
            next_task_distribution[predecessor] = dict()
            task_occurrences[predecessor] = 0
        if successor not in next_task_distribution[predecessor].keys():
            next_task_distribution[predecessor][successor] = 0
        next_task_distribution[predecessor][successor] += 1
        task_occurrences[predecessor] += 1
    for predecessor in next_task_distribution:
        successors = []
        for successor in next_task_distribution[predecessor]:
            successors.append((next_task_distribution[predecessor][successor]/task_occurrences[predecessor], successor))
        next_task_distribution[predecessor] = successors
    df_resources = df.groupby(['Activity', 'Resource']).agg(Duration_mean=('Duration', 'mean'), Duration_std=('Duration', 'std'), Resource_count=('Resource', 'count'))
    resource_pool = dict()
    processing_time_distribution = dict()
    for tt in task_types:
        resource_pool[tt] = []
    for index, row in df_resources.iterrows():
        if row["Resource_count"] > min_resource_count:
            resource_pool[row['Activity']].append(row['Resource'])
            processing_time_distribution[(row['Activity'], row['Resource'])] = (row['Duration_mean'], row['Duration_std'])

    # Now create the problem and return it
    result = MinedProblem()
    result.task_types = list(task_types)  # The task types
    result.resources = list(resources)  # The resources
    result.initial_task_distribution = initial_task_distribution  # The initial task type distribution
    result.next_task_distribution = next_task_distribution # The next task type distribution per task type
    result.mean_interarrival_time = mean_interarrival_time  # The interarrival time
    result.resource_pool = resource_pool  # The resource pool per task type
    result.processing_time_distribution = processing_time_distribution # The processing time distribution per task_type/resource combination

    return result
