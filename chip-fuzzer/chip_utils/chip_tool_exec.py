import os
import subprocess
import logging
import shlex


class ChipToolExec:
    """
    This class wraps the execution of chip-tool command with the provided arguments
    """

    def __init__(self, chip_home, chip_out):
        self.chip_path = os.path.join(chip_home, chip_out, 'chip-tool')

    def exec(self, args: list[str], print_errors=False, timeout=45) -> str:
        logging.debug("Executing chip-tool command with args: %s", args)
        args_str = [self.chip_path] + shlex.split(' '.join(args))
        out = subprocess.run(
            args_str,
            timeout=timeout,
            capture_output=True,
        )

        out_decoded = out.stdout.decode('utf-8')
        err_decoded = out.stderr.decode('utf-8')

        if out.returncode != 0:
            if print_errors:
                logging.error(out_decoded)
                logging.error(err_decoded)

        return out_decoded
