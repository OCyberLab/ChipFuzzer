import logging
import time

from chip_utils.chip_tool_exec import ChipToolExec
from chip_utils.log_parser import LogParser
from config import Config, DeviceType
from detector.ping_detector import PingDetector


class PreCheck:
    def __init__(self, cfg: Config):
        self.devices = cfg.devices
        self.ping_detector = PingDetector()
        self.chip = ChipToolExec(chip_home=cfg.chip_home, chip_out=cfg.chip_output_dir)

    def pre_check_bulb(self, device_id: str, endpoint_id: str = '1'):
        out = self.chip.exec(['onoff', 'on', device_id, endpoint_id], print_errors=True)
        if not LogParser.check_cmd_success(out):
            raise Exception("Pre check failed")
        time.sleep(0.2)
        out = self.chip.exec(['onoff', 'off', device_id, endpoint_id], print_errors=True)
        if not LogParser.check_cmd_success(out):
            raise Exception("Pre check failed")

    def pre_check_window_cover(self, device_id: str, endpoint_id: str = '1'):
        out = self.chip.exec(['windowcovering', 'go-to-lift-value', '100', device_id, endpoint_id], print_errors=True)
        if not LogParser.check_cmd_success(out):
            raise Exception("Pre check failed")
        time.sleep(0.2)
        out = self.chip.exec(['windowcovering', 'go-to-lift-value', '0', device_id, endpoint_id], print_errors=True)
        if not LogParser.check_cmd_success(out):
            raise Exception("Pre check failed")

    def pre_check_lock(self, device_id: str, endpoint_id: str = '1'):
        out = self.chip.exec(['doorlock', 'lock-door', device_id, endpoint_id, '--timedInteractionTimeoutMs', '500'],
                             print_errors=True)
        if not LogParser.check_cmd_success(out):
            raise Exception("Pre check failed")
        time.sleep(0.2)
        out = self.chip.exec(['doorlock', 'unlock-door', device_id, endpoint_id, '--timedInteractionTimeoutMs', '500'],
                             print_errors=True)
        if not LogParser.check_cmd_success(out):
            raise Exception("Pre check failed")

    def pre_check_default(self, device_id: str, endpoint_id: str = '1'):
        out = self.chip.exec(['identify', 'read', 'identify-time', device_id, endpoint_id],
                             print_errors=True)
        if not LogParser.cmd_identify_time(out):
            raise Exception("Pre check failed")

    def perform_pre_check(self):
        for name, cfg in self.devices.items():

            logging.debug("Performing pre check for device '%s'", name)

            device_id = cfg.id
            device_ep = '1'
            device_ip = cfg.ip
            if cfg.bridged:
                device_id = cfg.bridge.id
                device_ep = cfg.id
                device_ip = cfg.bridge.ip

            self.ping_detector.start_monitoring(device_id, device_ip)

            try:
                if DeviceType.BULB == DeviceType.from_str(cfg.type):
                    self.pre_check_bulb(device_id=device_id, endpoint_id=device_ep)
                    continue

                if DeviceType.LOCK == DeviceType.from_str(cfg.type):
                    self.pre_check_lock(device_id=device_id, endpoint_id=device_ep)
                    continue

                if DeviceType.WINDOW_COVER == DeviceType.from_str(cfg.type):
                    self.pre_check_window_cover(device_id=device_id, endpoint_id=device_ep)
                    continue

                self.pre_check_default(device_id, device_ep)
            except Exception as ex:
                raise ex
            finally:
                time.sleep(3)
                result = self.ping_detector.reset_monitoring(device_id, False)

            if not result:
                raise Exception("Pre check failed due to ping error")

        logging.info("Pre check completed successfully")
