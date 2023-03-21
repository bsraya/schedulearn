from datetime import datetime

# makespan is the time between the first job starting and the last job completing
def makespan_in_seconds(start_time, end_time):
    start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
    end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f')
    return (end - start).total_seconds()

# turnaround time is the time between the job starting and the job completing
def turnaround_in_seconds(start_time, end_time):
    start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
    end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f')
    return (end - start).total_seconds()