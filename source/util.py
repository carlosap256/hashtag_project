from typing import Dict, List
import itertools


def merge_two_dicts(dict1: Dict[str, List[str]], dict2: Dict[str, List[str]]):
    for key, value in dict2.items():
        old_values = dict1.get(key, list())
        old_values.extend(value)
        dict1[key] = old_values
    return dict1


def _loop_first_n_results(iterable, n: int):
    for result in itertools.islice(iterable, n):
        yield result