import json
import logging
import math

from chip_utils.chip_tool_exec import ChipToolExec
from chip_utils.log_parser import LogParser
from config import Config


def is_float(element: any) -> bool:
    # If you expect None to be passed:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False


class BrightnessFuzzer:
    """
    This class provides basic mechanism to fuzz the brightness cluster.
    """

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.chip = ChipToolExec(chip_home=cfg.chip_home, chip_out=cfg.chip_output_dir)
        pass

    def perform_fuzz(self):
        with open("blns.txt", "r") as f:
            lines = f.read().splitlines()

        for line in lines[80:100]:
            try:
                val = int(line)
            except ValueError:
                if is_float(line):
                    val = float(line)
                    if math.isnan(val) or math.isinf(val):
                        val = line
                else:
                    val = line

            payload = json.dumps({
                "0x0": val
            })

            payload = payload.replace("'", "")
            out = self.chip.exec(['any', 'command-by-id', '8', '0', '\'' + payload + '\'', '3', '1'],
                                 print_errors=False)
            if not LogParser.validate_cmd_failure(out):
                logging.error(out)
                raise Exception("Unexpected return from device")

            out = self.chip.exec(
                ['any', 'command-by-id', '8', '0', '\'' + payload + '\'', '5', '2'],
                print_errors=False)
            if not LogParser.validate_cmd_failure(out):
                logging.error(out)
                raise Exception("Unexpected return from device")


class BasicFuzzer:
    def __init__(self):
        self.setup = ''
