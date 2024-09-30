
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

def tuples_overlap(t1, t2):
    return t1[0] <= t2[0] <= t1[1] or t2[0] <= t1[0] <= t2[1]

def contains_each_other(t1, t2):
    return t1[0] <= t2[0] and t1[1] >= t2[1] or t2[0] <= t1[0] and t2[1] >= t1[1]

def detect_overlapping_tuples(tuple_list):
    for i in range(len(tuple_list)):
        for j in range(i + 1, len(tuple_list)):
            if tuples_overlap(tuple_list[i], tuple_list[j]) or contains_each_other(tuple_list[i], tuple_list[j]):
                return True
    return False


def classify_tuples(tuples_list):
    for _, example in enumerate(tuples_list, 1):
        result = detect_overlapping_tuples(example)
        return result







def is_all_zeros(array):
    return all(value == 0 for value in array)


def getrandomDuration(duration, length):
    start = round(random.uniform(0, duration-length), 1)
    end = start + length
    return start, end

# examples = [
#     [(142.4, 147.4), (71.8, 76.8), (3.4, 8.4), (4.8, 9.8)],
#     [(64.3, 69.3), (164.3, 169.3), (124.0, 129.0), (12.6, 17.6)],
#     [(59.0, 64.0), (94.9, 99.9), (32.1, 37.1), (156.5, 161.5)],
#     [(102.4, 107.4), (83.0, 88.0), (57.3, 62.3), (138.7, 143.7)],
#     [(39.6, 44.6), (108.6, 113.6), (85.9, 90.9), (167.7, 172.7)],
#     [(133.9, 138.9), (1.6, 6.6), (154.0, 159.0), (130.9, 135.9)],
#     [(28.5, 33.5), (130.3, 135.3), (60.4, 65.4), (166.6, 171.6)],
#     [(60.8, 65.8), (45.5, 50.5), (28.1, 33.1), (12.4, 17.4)],
#     [(200.1, 205.1), (49.1, 54.1), (15.5, 20.5), (132.4, 137.4)],
#     [(171.9, 176.9), (42.4, 47.4), (126.7, 131.7), (125.8, 130.8)],
#     [(156.3, 161.3), (10.8, 15.8), (50.1, 55.1), (32.6, 37.6)],
#     [(192.1, 197.1), (83.3, 88.3), (119.9, 124.9), (65.0, 70.0)],
#     [(84.5, 89.5), (5.7, 10.7), (80.7, 85.7), (110.2, 115.2)],
#     [(204.9, 209.9), (165.7, 170.7), (167.9, 172.9), (86.6, 91.6)],
# ]
#
# for example in examples:
#     output = classify_tuples(example)
#     print(f"{example},{'R' if any(output) else 'U'}")
#
