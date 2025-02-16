from typing import Dict
from tribuz_populate.commons import faker
from tribuz_populate.structs import Multiverse

def multiverse_generator(qtd) -> Dict[str, Multiverse]:
    multiverses: Dict[str, Multiverse] = {}
    nb = 1
    for i in range(qtd):
        while True:
            code = '-'.join(faker.words(nb=nb, unique=True))
            if code not in multiverses:
                multiverse: Multiverse = {
                    'code': code,
                    'name': code.replace('-', ' '),
                    'description': faker.text()
                }
                multiverses[code] = multiverse
                break
            if i // (100 ** nb) >= 1:
                nb += 1
    return multiverses
