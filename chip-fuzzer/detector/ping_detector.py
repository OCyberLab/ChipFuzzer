import ipaddress
import logging
import multiprocessing as mp
import os
from datetime import datetime
from multiprocessing.connection import Connection


class PingResult:
    """
    This class represents a result from performing a ping.
    """
    status: bool
    failure_time: [datetime]
    error: str

    def __init__(self):
        self.status = False
        self.failure_time = []
        self.error = ''


class PingProc:
    """
    Class that represents a process that is performing pings.
    """
    proc: mp.Process
    conn: Connection
    addr: str

    def __init__(self, addr: str, proc: mp.Process, conn: Connection):
        self.addr = addr
        self.proc = proc
        self.conn = conn


def run_ping(addr: str, conn: Connection):
    """
    This function executes ping for the given IP address.
    :param addr: IPv4 or IPv6 address that is to be pinged
    :param conn: connection from multiprocess pipe
    """
    ping_result = PingResult()
    # Validate IP Address
    try:
        ip = ipaddress.ip_address(addr)
        if ip.version == 6:
            ping_cmd = 'ping -6 '
        elif ip.version == 4:
            ping_cmd = 'ping '
        else:
            raise Exception("Could not recognize IP address")
    except Exception as ex:
        logging.error("Invalid IP address %s", addr)
        logging.exception(ex)
        ping_result.error = str(ex)
        conn.send(ping_result)
        return

    ping_cmd = ping_cmd + "-c 1 -w2 " + addr + " > /dev/null 2>&1"
    while not conn.poll(0.25):
        response = os.system(ping_cmd)
        if response != 0:
            ping_result.status = False
            ping_result.failure_time.append(datetime.now())
            continue

        ping_result.status = True

    conn.recv()
    conn.send(ping_result)
    conn.close()


class PingDetector:
    """
    Checks status of a device using ping for provided address.
    """

    def __init__(self):
        self.procs: dict[str, PingProc] = dict()

    def start_monitoring(self, device_id: str, addr: str):
        p_conn, c_conn = mp.Pipe()
        self.procs[device_id] = PingProc(
            addr=addr,
            proc=mp.Process(target=run_ping, args=(addr, c_conn,)),
            conn=p_conn
        )
        self.procs[device_id].proc.start()

    def reset_monitoring(self, device_id: str, restart: bool = True) -> PingResult:
        p = self.procs[device_id]
        p.conn.send("STOP")
        ping_result = p.conn.recv()
        p.conn.close()
        p.proc.join()
        if restart:
            self.start_monitoring(device_id, p.addr)
        else:
            del self.procs[device_id]
        logging.debug("Stopped ping monitor for device id %s", device_id)
        return ping_result

    def stop_all(self) -> dict[str, PingResult]:
        results: dict[str, PingResult] = {}
        ids = list(self.procs.keys())
        for device_id in ids:
            logging.debug("Stopping ping for device id %s", device_id)
            p_res = self.reset_monitoring(device_id, False)
            results[device_id] = p_res
        return results
