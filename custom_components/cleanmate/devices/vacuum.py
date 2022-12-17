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
    """The error code"""

    LocalizationFailed = 119
    Stuck = 106


class CleanmateVacuum(Connection):
    """A Cleanmate vacuum."""

    battery_level: int = None
    version: str = None
    work_mode: WorkMode = None
    work_state: WorkState = None
    had_work: bool = False
    mop_mode: MopMode = None
    volume: int = None
    error_code: int = None

    async def get_state_data(self) -> dict:
        """Get state data of the vacuum."""
        data = {"state": "", "transitCmd": "98"}
        await self.send_request(data)
        state_data = await self.get_response()
        return state_data

    async def update_state(self) -> None:
        """Get and update state of the vacuum."""
        state_value = (await self.get_state_data())["value"]
        self.battery_level = state_value["battery"]
        self.version = state_value["version"]
        self.work_mode = state_value["workMode"]
        self.work_state = state_value["workState"]
        self.had_work = state_value["extParam"]["hadWork"]
        self.mop_mode = state_value["waterTank"]
        self.error_code = state_value["error"]

    async def get_map_data(self) -> dict:
        """Get map data of the vacuum."""
        data = {
            "mapWidth": "0",
            "centerPoint": "0",
            "mapHeight": "0",
            "trackNum": "AAA=",
            "mapSign": "AAA=",
            "transitCmd": "133",
        }
        await self.send_request(data)
        map_data = await self.get_response()
        return map_data

    async def start(self, work_mode: WorkMode = None) -> None:
        """Start cleaning."""
        if work_mode is None:
            data = {
                "start": "1",
                "transitCmd": "100",
            }
        else:
            data = {
                "mode": str(work_mode.value),
                "transitCmd": "106",
            }
        await self.send_request(data)

    async def stop(self):
        """Stop cleaning."""
        data = {
            "stop": "1",
            "isStop": "1",
            "transitCmd": "102",
        }
        await self.send_request(data)

    async def pause(self) -> None:
        """Pause cleaning."""
        data = {
            "pause": "1",
            "isStop": "0",
            "transitCmd": "102",
        }
        await self.send_request(data)

    async def charge(self) -> None:
        """Go to charging station."""
        data = {
            "charge": "1",
            "transitCmd": "104",
        }
        await self.send_request(data)

    async def set_mop_mode(self, mop_mode: MopMode) -> None:
        """Set mop mode of the vacuum."""
        data = {
            "waterTank": str(mop_mode.value),
            "transitCmd": "145",
        }
        await self.send_request(data)

    async def set_volume(self, volume: int) -> None:
        """Set volume of the vacuum."""
        vol = 1 + round((volume / 100) * 10) / 10
        data = {
            "volume": str(vol),
            "voice": "",
            "transitCmd": "123",
        }
        await self.send_request(data)

    async def clean_rooms(self, room_ids: list[int]) -> None:
        """Clean specific rooms"""
        unique_sorted_ids = sorted(list(dict.fromkeys(room_ids)))
        clean_blocks = list(
            map(
                lambda room_id: {"cleanNum": "1", "blockNum": str(room_id)},
                unique_sorted_ids,
            )
        )
        data = {
            "opCmd": "cleanBlocks",
            "cleanBlocks": clean_blocks,
        }
        await self.send_request(data)

    async def find(self) -> None:
        """Announce vacuum's location"""
        data = {
            "find": "",
            "transitCmd": "143",
        }
        await self.send_request(data)
