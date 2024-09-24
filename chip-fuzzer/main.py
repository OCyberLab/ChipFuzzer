import logging

import yaml

from chip_utils.compile_chip_tool import CompileChipTool
from config import Config
from pre_check import PreCheck
from zcl_fuzzer import ZclFuzzer
from basic_fuzzer import BrightnessFuzzer

# Setup logging
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)-2s] %(message)s",
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":
    with open("config.yaml", "r") as cfg_file:
        yml_cfg = yaml.safe_load(cfg_file)

    config = Config(**yml_cfg)
    logging.debug("Loaded configuration")

    c = CompileChipTool(config.chip_home, config.chip_output_dir)
    c.compile_chip_tool()

    if config.pre_check:
        p = PreCheck(config)
        p.perform_pre_check()

    # b = BrightnessFuzzer(config)
    # b.perform_fuzz()
    #
    # zcl_fuzzer = ZclFuzzer('2', config)
    # zcl_fuzzer.update_zcl()
    # c.compile_zcl()
    # c.compile_chip_tool()
    # zcl_fuzzer.perform_fuzz()

