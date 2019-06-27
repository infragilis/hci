import json
import time
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, error as socketerr
from ansible.module_utils.pstools.config import Config

def gather_beacons(limit=0):
    """
    Listen to nascent node broadcasts and gather them up
    """
    client = socket(AF_INET, SOCK_DGRAM)
    client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    client.settimeout(3)
    client.bind(('', Config.BEACON_PORT))

    t0 = time.time()
    beaconDict = {}
    while time.time() - t0 < Config.GATHER_WAIT_SEC:
        try:
            msg = client.recv(Config.BUFFER_SIZE)
            if msg:
                obj = json.loads(msg.decode("utf-8"))
                uuid = obj["uuid"]
                if uuid in beaconDict:
                    continue
                del obj["uuid"]
                beaconDict[uuid] = obj
                if limit > 0 and len(beaconDict.keys()) >= limit:
                    break
        except (json.decoder.JSONDecodeError, KeyError):
            continue
        except socketerr:
            continue

    return beaconDict
