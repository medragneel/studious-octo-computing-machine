
import random


# def classify_tuples(arr):
#     # Sort the array of tuples based on the start of each interval
#     sorted_arr = sorted(arr, key=lambda x: x[0])
#
#     # Initialize a result list to store the classification
#     result = [0] * len(arr)
#
#     for i in range(len(sorted_arr) - 1):
#         current_tuple = sorted_arr[i]
#         for j in range(i + 1, len(sorted_arr)):
#             next_tuple = sorted_arr[j]
#
#             # Check if the next tuple is completely contained within the current tuple
#             if current_tuple[0] <= next_tuple[0] and current_tuple[1] >= next_tuple[1]:
#                 result[arr.index(next_tuple)] = 1
#
#     return result


def classify_tuples(arr):
    # Create a list of events, each represented as a tuple (start, end, index, type)
    events = []
    for i, (start, end) in enumerate(arr):
        events.append((start, i, "start"))
        events.append((end, i, "end"))

    # Sort the events based on their position on the sweep line
    events.sort()

    # Initialize a result list to store the classification
    result = [0] * len(arr)

    # Keep track of the active intervals using a set
    active_intervals = set()

    # Use a dictionary to map tuple indices to their corresponding result indices
    tuple_index_to_result_index = {i: idx for idx, i in enumerate(arr)}

    for position, index, event_type in events:
        if event_type == "start":
            active_intervals.add(index)
        elif event_type == "end":
            active_intervals.remove(index)
            # Check if the index is in the dictionary before performing the lookup
            if index in tuple_index_to_result_index:
                result[tuple_index_to_result_index[index]
                       ] = 1 if active_intervals else 0

    return result


def is_all_zeros(array):
    return all(value == 0 for value in array)


def getrandomDuration(duration, length):
    start = round(random.uniform(0, duration-length), 1)
    end = start + length
    return start, end
