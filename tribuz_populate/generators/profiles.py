import datetime
from typing import Dict
from tribuz_populate.structs import Multiverse, Profile
from multiprocessing.managers import DictProxy
import random
import uuid
from tribuz_populate.commons import calculate_partitions, chunks, remove_special_characters, faker

def process_profiles_isolated(username_created: DictProxy[str, Profile], multiverses: Dict[str, Multiverse], max_profiles: int, spawn_units: int, pool):
    data = calculate_partitions(max_profiles, spawn_units, multiverses)
    results = pool.starmap(profiles_generator_concurrent, data)
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Profiles generated merge data")
    merge_data = [ (username_created, result) for result in results ]
    pool.starmap(prepare_username_created, merge_data)

def process_profiles(multiverses, max_profiles, spawn_units, pool, manager, queue = None, done = None):
    username_created = manager.dict()
    process_profiles_isolated(username_created, multiverses, max_profiles, spawn_units, pool)
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generate {len(username_created)} unique usernames")
    while len(username_created) < max_profiles:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generate shared context remains: {max_profiles - len(username_created)}")
        data = calculate_partitions(max_profiles - len(username_created), spawn_units, multiverses, username_created)
        processes = pool.starmap_async(profiles_generator, data)
        processes.wait()
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generation Process done")
    
    if queue:
        partitions = int(max_profiles / 2 ** 4)
        producer_chunks = [ (item, queue) for item in chunks(username_created, partitions) ]
        producer_processes = pool.starmap_async(produce, producer_chunks)
        producer_processes.wait()
    
    if done:
        done.set(True)
    if queue:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Publish all profiles")
        return {}
    return username_created

def produce(messages, queue):
    [queue.put(v) for _, v in messages.items()]

def profiles_generator_concurrent(qtd: int, multiverses: Dict[str, Multiverse]):
    id = uuid.uuid4()
    profiles = {}
    multiverse_keys = list(multiverses.keys())
    for _ in range(qtd):
        while True:
            username, p, multiverse = gen_fake_profile(multiverse_keys, profiles)
            if username not in profiles:
                profiles[p['username']] = ({
                    'multiverse': multiverse,
                    'multiverse_id': multiverses[multiverse]['id'],
                    'produced_by': id
                } | p)
                break
            else:
                current = len(profiles)
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{id}] Colision: {username} | current: {current}")
    return profiles

def profiles_generator(qtd, multiverses, username_created: DictProxy[str, Profile]):
    id = uuid.uuid4()
    multiverse_keys = list(multiverses.keys())
    for _ in range(qtd):
        while True:
            username, p, multiverse = gen_fake_profile(multiverse_keys, username_created)
            if username not in username_created:
                username_created[p['username']] = ({
                    'multiverse': multiverse,
                    'multiverse_id': multiverses[multiverse]['id'],
                    'produced_by': id
                } | p)
                break
            else:
                current = len(username_created)
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{id}] Colision: {username} produced by {str(username_created[username]['produced_by'])} | current: {current}")

def gen_fake_profile(multiverse_keys: list[str], username_created: Dict[str, Profile]) -> (str | Profile | str):
    profile = faker.profile()
    username_max = profile['username'] + '_' + generate_without_abbrev(profile['name'])
    username = None
    if generate_username_from_name(profile['name']) not in username_created:
        username = generate_username_from_name(profile['name'])
    elif generate_without_abbrev(profile['name']) not in username_created:
        username = generate_without_abbrev(profile['name'])
    elif both_from_name(profile['name']) not in username_created:
        username = both_from_name(profile['name'])
    elif generate_username_from_name(profile['name']) + '.' + profile['username'] not in username_created:
        username = generate_username_from_name(profile['name']) + '.' + profile['username']
    elif profile['username'] + '.' + generate_username_from_name(profile['name']) not in username_created:
        username = profile['username'] + '.' + generate_username_from_name(profile['name'])
    elif profile['username'] not in username_created:
        username = profile['username']
    else:
        username = username_max
    p = {
        'username': username,
        'fullname': profile['name'] + ' ' + faker.last_name(),
        'nickname': profile['name'],
        'sex': profile['sex'],
        'birthdate': profile['birthdate']
    }
    multiverse = random.choice(multiverse_keys)
    return username,p,multiverse

def generate_without_abbrev(name) -> str:
    return remove_special_characters(name.replace(' ', '').lower())

def generate_username_from_name(name) -> str:
    parts = name.split()
    if len(parts) == 1:
        return parts[0].lower()
    last_name = parts[-1].lower()
    initials = ''.join([part[0].lower() for part in parts[:-1]])
    return remove_special_characters(initials + last_name)

def both_from_name(name) -> str:
    return generate_username_from_name(name) + '.' + generate_without_abbrev(name)

def prepare_username_created(profiles_created: Dict[str, Profile], profiles: Dict[str, Profile]):
    profiles_created.update(profiles)
