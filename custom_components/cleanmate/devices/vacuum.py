"""A Cleanmate vacuum."""
from enum import Enum
from ..connection import Connection

class WorkMode(Enum):
    """The cleaning intensity."""
    Intensive = 7
    Standard = 1
    Silent = 9

class WorkState(Enum):
    """The work state."""
    Cleaning = 1
    Idle = 2
    Returning = 4
    Charging = 5
    Error = 7
    Problem = 9

class MopMode(Enum):
    """The mop intensity."""
    High = 20
    Medium = 40
    Low = 60

class ErrorCode(Enum):
    PlaceDock = 119

class CleanmateVacuum(Connection):
    """A Cleanmate vacuum."""
    battery_level: int = None
    version: str = None
    work_mode: WorkMode = None
    work_state: WorkState = None
    had_work: bool = False
    mop_mode: MopMode = None
    volume: int = 0
    error_code: int = None

    def get_state_data(self) -> dict:
        """Get state data of the vacuum."""
        data = {
            "state": "",
            "transitCmd": "98"
        }
        self.send_request(data)
        state_data = self.read_data()
        return state_data

    def update_state(self) -> None:
        """Get and update state of the vacuum."""
        state_value = self.get_state_data()["value"]
        self.battery_level = state_value["battery"]
        self.version = state_value["version"]
        self.work_mode = state_value["workMode"]
        self.work_state = state_value["workState"]
        self.had_work = state_value["extParam"]["hadWork"]
        self.mop_mode = state_value["waterTank"]
        self.error_code = state_value["error"]

    def get_map_data(self) -> dict:
        """Get map data of the vacuum."""
        data = {
            "mapWidth": "0",
            "centerPoint": "0",
            "mapHeight": "0",
            "trackNum": "AAA=",
            "mapSign": "AAA=",
            "transitCmd": "133",
        }
        self.send_request(data)
        map_data = self.read_data()
        return map_data

    def start(self, work_mode: WorkMode = None) -> None:
        """Start cleaning."""
        if(work_mode == None):
            data = {
                "start": "1",
                "transitCmd": "100",
            }
        else:
            data = {
                "mode": str(work_mode.value),
                "transitCmd": "106",
            }
        self.send_request(data)
    
    def stop(self):
        """Stop cleaning."""
        data = {
            "stop": "1",
            "isStop": "1",
            "transitCmd": "102",
        }
        self.send_request(data)

    def pause(self) -> None:
        """Pause cleaning."""
        data = {
            "pause": "1",
            "isStop": "0",
            "transitCmd": "102",
        }
        self.send_request(data)

    def charge(self) -> None:
        """Go to charging station."""
        data = {
            "charge": "1",
            "transitCmd": "104",
        }
        self.send_request(data)

    def set_mop_mode(self, mop_mode: MopMode) -> None:
        """Set mop mode of the vacuum."""
        data = {
            "waterTank": str(mop_mode.value),
            "transitCmd": "145",
        }
        self.send_request(data)

    def set_volume(self, volume: int) -> None:
        """Set volume of the vacuum."""
        vol = 1 + round((volume/100) * 10) / 10
        data = {
            "volume": str(vol),
            "voice": "",
            "transitCmd": "123",
        }
        self.send_request(data)

    def clean_rooms(self, room_ids: list[int]) -> None:
        """Clean specific rooms"""
        unique_sorted_ids = sorted(list(dict.fromkeys(room_ids)))
        clean_blocks = list(map(lambda room_id: {"cleanNum": "1", "blockNum": str(room_id)}, unique_sorted_ids))
        data = {
            'opCmd': "cleanBlocks",
            "cleanBlocks": clean_blocks,
        }
        self.send_request(data)

    def find(self) -> None:
        """Announce vacuum's location"""
        data = {
            "find": "",
            "transitCmd": "143",
        }
        self.send_request(data)
