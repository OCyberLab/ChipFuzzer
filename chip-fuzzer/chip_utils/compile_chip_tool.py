import logging
import os.path
import subprocess


class CompileChipTool:
    def __init__(self, chip_home: str, out_dir: str):
        out_path = os.path.join(chip_home, out_dir)

        if not os.path.exists(chip_home) or not os.path.exists(out_path):
            raise Exception("Invalid path ", chip_home, out_path)

        self.chip_home = chip_home
        self.out_dir = out_dir

    def compile_zcl(self):
        logging.debug("Compiling ZCL, this might take few minutes...")
        out = subprocess.run('source scripts/activate.sh;./scripts/tools/zap_regen_all.py',
                             shell=True,
                             capture_output=True,
                             executable='/bin/bash',
                             cwd=self.chip_home)

        if out.returncode != 0:
            logging.debug("Could not compile ZCL")
            logging.debug(out.stdout.decode('utf-8'))
            raise Exception("Could not compile ZCL")

    def compile_chip_tool(self):
        logging.debug("Compiling chip tool...")
        out = subprocess.run(
            'source scripts/activate.sh; gn gen out/host;./scripts/examples/gn_build_example.sh examples/chip-tool ' + self.out_dir,
            shell=True,
            capture_output=True,
            executable='/bin/bash',
            cwd=self.chip_home)

        if out.returncode != 0:
            logging.debug("Could not compile ZCL")
            logging.debug(out.stdout)
            raise Exception("Could not compile ZCL")
