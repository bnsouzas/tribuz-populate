from contextlib import contextmanager
import datetime
from itertools import islice
import time
import unicodedata
from faker import Faker

faker = Faker('pt_BR')

@contextmanager
def record_duration(task_name):
    start_time = time.time()
    try:
        yield task_name
    finally:
        elapsed_time = time.time() - start_time    
        print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] Finished {task_name} in {elapsed_time} seconds")

def calculate_partitions(qtd, units, *args):
    partition = qtd // units
    remainder = qtd % units
    data = [ (partition + (remainder if i == 0 else 0), *args) for i in range(0, units)]
    return data

def remove_special_characters(text):
    normalized_text = unicodedata.normalize('NFKD', text)
    ascii_text = normalized_text.encode('ASCII', 'ignore').decode('ASCII')
    return ''.join(char for char in ascii_text if char.isalnum() or char.isspace())


def chunks(data, SIZE=10000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}
