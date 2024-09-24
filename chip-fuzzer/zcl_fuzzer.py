import json
import os
import random
from config import Config, DeviceCfg, DeviceType
from chip_utils.chip_tool_exec import ChipToolExec
import xml.etree.ElementTree as Et


def get_fuzzed_type(orig_type):
    fuzz_type = orig_type
    if orig_type == 'int16u':
        fuzz_type = 'int32u'
    return fuzz_type


class ZclFuzzer:
    def __init__(self, device_id: str, cfg: Config):
        self.device_id = device_id
        self.cfg = cfg
        self.chip = ChipToolExec(chip_home=cfg.chip_home, chip_out=cfg.chip_output_dir)

        for name, cfg in self.cfg.devices.items():
            if cfg.id == self.device_id:
                self.device: DeviceCfg = cfg
        if self.device is None:
            raise Exception("Device with provided id was not found")

    def update_zcl(self):
        zcl_files = self.get_zcl_files()
        for zcl_file in zcl_files:
            self.modify_cmd_zcl_file(zcl_file)

    def perform_fuzz(self):
        zcl_filepath = os.path.join(self.cfg.chip_home,
                                    'src/app/zap-templates/zcl/data-model/chip',
                                    'onoff-cluster.xml')
        for i in range(0, 40):
            payload = json.dumps({
                "0x0": random.randint(0, 21312312312312),
                "0x1": random.randint(0, 21312312312312),
                "0x2": random.randint(0, 21312312312312)
            })

            self.chip.exec(['onoff', 'OnWithTimedOff', '\'' + payload + '\'', '5', '2'])

    def modify_cmd_zcl_file(self, zcl_filename):
        zcl_filepath = os.path.join(self.cfg.chip_home, 'src/app/zap-templates/zcl/data-model/chip', zcl_filename)
        tree = Et.parse(zcl_filepath)
        root = tree.getroot()
        cmds = root.findall('./cluster/command')
        for cmd in cmds:
            if cmd.attrib['source'] == 'server':
                continue
            if cmd.attrib['code'] == '0x42':
                args = cmd.findall('./arg')
                if not args:
                    continue
                for arg in args:
                    arg.attrib['type'] = get_fuzzed_type(arg.attrib['type'])
        if zcl_filename == 'onoff-cluster.xml':
            tree.write(zcl_filepath, encoding='utf-8', xml_declaration=True)

    def get_commands(self, zcl_filename):
        tree = Et.parse(os.path.join(self.cfg.chip_home, 'src/app/zap-templates/zcl/data-model/chip', zcl_filename))
        root = tree.getroot()
        return root.findall('./cluster/command')

    def get_zcl_files(self):
        if DeviceType.BULB == DeviceType.from_str(self.device.type):
            return ['onoff-cluster.xml', 'level-control-cluster.xml']
        elif DeviceType.LOCK == DeviceType.from_str(self.device.type):
            return ['door-lock-cluster.xml']
        else:
            return []
