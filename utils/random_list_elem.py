import random


def random_list_elem(list):
    list_len = len(list) - 1
    rand_num = random.randint(0, list_len)
    return rand_num
