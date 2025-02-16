import datetime
from queue import Empty
import uuid
import multiprocessing
import sys

from tribuz_populate.bigbang.assault import Assault
from tribuz_populate.bigbang.multiverses import MultiverseAmmo
from tribuz_populate.bigbang.profiles import ProfileAmmo
from tribuz_populate.commons import record_duration
from tribuz_populate.generators.multiverses import multiverse_generator
from tribuz_populate.generators.profiles import process_profiles

max_multiverses = 10_000
max_profiles = 1_000_000

def calculate_spawn_units():
    profile_thresholds = [10240000, 1024000, 102400, 10240, 1024, 128]
    unit_values = [32, 16, 8, 4, 2, 1]

    for threshold, units in zip(profile_thresholds, unit_values):
        if max_profiles > threshold:
            return min(units, multiprocessing.cpu_count())

    return multiprocessing.cpu_count()

if __name__ == '__main__':
    with record_duration("Big Bang"):
        manager = multiprocessing.Manager()
        v = sys.version_info
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Python: {v[0]}.{v[1]}.{v[2]}-{v[3]} ({sys.platform})")
        
        with record_duration("multiverses"):
            multiverses = multiverse_generator(max_multiverses)

        multiverse_assault = Assault('localhost:50051', MultiverseAmmo())
        multiverses = multiverse_assault.attack(multiverses)
        
        with record_duration("profiles"):
            spawn_generation_units = calculate_spawn_units()
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Spawn_generation_units: {spawn_generation_units}")
            with multiprocessing.Pool(processes=spawn_generation_units) as pool:
                profiles = process_profiles(multiverses, max_profiles, spawn_generation_units, pool, manager)
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generate profiles: {len(profiles)}")

        profile_assault = Assault('localhost:50051', ProfileAmmo())
        profiles = profile_assault.attack(profiles)
    print('THE END')