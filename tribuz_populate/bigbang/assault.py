import asyncio
import uvloop
import multiprocessing
from typing import Any, Dict
from grpc import Channel, aio
from tribuz_populate.commons import chunks, record_duration

units = multiprocessing.cpu_count()

class Ammo:
    def get_caliber(self) -> str:
        raise 'Ammo.load not implemented'
    
    async def load(channel: Channel) -> Any:
        raise 'Ammo.load not implemented'
    
    async def fire(gun: Any, bullet: Any) -> Any:
        raise 'Ammo.fire not implemented'

def _strategy(*args) -> Any:
    loop = uvloop.new_event_loop()
    result = loop.run_until_complete(
        __aim(*args)
    )
    return result

async def __aim(grpc_url: str, ammo: Ammo, targets: Dict[str, Any]) -> Dict[str, Any]:
        async with aio.insecure_channel(grpc_url) as channel:
            gun = ammo.load(channel)
            response = await asyncio.gather(*[
                ammo.fire(gun, target)
                for target in targets.values()
            ])
            result = {}
            for target in response:
                result[target[ammo.get_caliber()]] = target
            return result

class Assault:
    def __init__(self, grpc_url, ammo: Ammo):
        self.__grpc_url = grpc_url
        self.__ammo = ammo
    
    def ammo(self):
        return self.__ammo
    
    def grpc_url(self):
        return self.__grpc_url

    def attack(self, targets: Dict[str, Any]) -> Dict[str, Any]:
        with record_duration("Attack %s Duration" % self.ammo().__class__.__name__):
            size = len(targets.keys())
            chunk_size = size // units
            targets_chunks = [ (self.__grpc_url, self.__ammo, chunk,) for chunk in chunks(targets, chunk_size) ]
            result: Dict[str, Any] = {}
            
            with multiprocessing.Pool(processes=units) as pool:
                responses = pool.starmap(_strategy, targets_chunks)
                for response in responses:
                    result.update(response)
            return result
