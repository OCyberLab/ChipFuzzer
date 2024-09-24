from dataclasses import dataclass
from enum import Enum

from pydantic.v1 import validate_arguments


class DeviceType(Enum):
    BULB = 1
    LOCK = 2
    WINDOW_COVER = 3
    SWITCH = 4
    OTHER = 99

    @staticmethod
    def from_str(lbl: str):
        lbl_lower = lbl.lower()
        if lbl_lower == 'bulb':
            return DeviceType.BULB
        elif lbl_lower == 'lock':
            return DeviceType.LOCK
        elif lbl_lower == 'window_cover':
            return DeviceType.WINDOW_COVER
        elif lbl_lower == 'switch':
            return DeviceType.SWITCH

        return DeviceType.OTHER


@dataclass
class BridgeCfg:
    id: str
    ip: str = ''


@dataclass
class DeviceCfg:
    id: str
    type: str
    ip: str = ''
    bridge: BridgeCfg = None
    bridged: bool = False


@validate_arguments
@dataclass
class Config:
    devices: dict[str, DeviceCfg]
    pre_check: bool = True
    chip_home: str = ''
    chip_output_dir: str = ''
