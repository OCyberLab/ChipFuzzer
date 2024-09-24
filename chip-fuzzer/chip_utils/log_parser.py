import logging


class LogParser:

    @staticmethod
    def check_cmd_success(output: str):
        """
        Parse output of chip-tool when a command is invoked to check if the command has completed successfully.
        :param output: the output from chip-tool
        :return: true if successful, false otherwise
        """
        result_token = 'Received Command Response Status for Endpoint='
        for line in output.splitlines():
            if result_token not in line:
                continue
            try:
                return '0x0' == line[line.find('Status='):].split('=')[1]
            except Exception as ex:
                logging.error(ex)
                return False
        return False

    @staticmethod
    def cmd_identify_time(output: str) -> bool:
        result_token = 'CHIP:TOO:   IdentifyTime: '
        for line in output.splitlines():
            if result_token not in line:
                continue
            logging.debug("Found identify time: " + line)
            return True
        return False

    @staticmethod
    def validate_cmd_failure(output: str) -> bool:
        result_token = 'Run command failure: IM Error 0x00000585: General error: 0x85 (INVALID_COMMAND)'
        for line in reversed(output.splitlines()):
            if LogParser.check_cmd_success(line):
                return True
            if result_token not in line:
                continue
            return True
        logging.error(output)
        return False
