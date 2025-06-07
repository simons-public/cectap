""" cec.log parsing """
import os
import re
import time
from typing import Callable, Optional
from collections import defaultdict
import cec

OPCODE_PFX = "CEC_OPCODE_"
TYPE_PFX = "CEC_DEVICE_TYPE_"
OPCODE_MAP = {
    v: k.removeprefix(OPCODE_PFX) for k, v in vars(cec).items()
    if k.startswith(OPCODE_PFX) and isinstance(v, int)
}
REVERSE_OPCODE_MAP = {
    k.removeprefix(OPCODE_PFX): v for v, k in OPCODE_MAP.items()
}
DEVICE_TYPE_MAP = {
    v: k.removeprefix(TYPE_PFX) for k, v in vars(cec).items()
    if k.startswith(TYPE_PFX)
}
LOG_LINE_REGEX = re.compile(
    r"CEC: ([0-9a-f]) -> ([0-9a-f])  opcode: 0x([0-9a-f]{2})(?: params:(.*))?",
    re.IGNORECASE
)

debug_print = print if os.getenv("DEBUG") == "1" else lambda *a, **k: None

class CECMessage:
    """ represents a parsed cec message """
    def __init__(self, initiator, destination, opcode, params) -> None:
        self.initiator = initiator
        self.destination = destination
        self.opcode = opcode
        self.params = params

    @property
    def opcode_name(self) -> str:
        """ formatted opcode name if known """
        return OPCODE_MAP.get(self.opcode, f"UNKNOWN_0x{self.opcode:02X}")

    @property
    def src_name(self) -> str:
        """ formatted source name or Device_X """
        return DEVICE_TYPE_MAP.get(self.initiator, f"Device_{self.initiator}")

    @property
    def dst_name(self) -> str:
        """ formatted destination name or Device_X """
        return DEVICE_TYPE_MAP.get(self.destination, f"Device_{self.destination}")

    def __str__(self) -> str:
        return f"{self.src_name} -> {self.dst_name} | {self.opcode_name} | params: {self.params}"

class CECMonitor:
    """ class that reads and parses log messages to CECMessages """
    def __init__(self, log_path="/tmp/cec.log") -> None:
        self.log_path = log_path
        self.callbacks = defaultdict(list)

    def on(self, opcode) -> Callable:
        """ register a callback for a specific opcode (name or int)"""
        if isinstance(opcode, str):
            opcode = REVERSE_OPCODE_MAP.get(opcode.upper())
        if opcode is None:
            raise ValueError("Unknown opcode")
        def decorator(func):
            self.callbacks[opcode].append(func)
            return func
        return decorator

    def parse_line(self, line) -> Optional[CECMessage]:
        """ parse a line read from cec.log """
        if not line:
            return None

        match = LOG_LINE_REGEX.match(line)
        if not match:
            debug_print(f"Unparsed line: {line.strip()}")
            return None

        initiator = int(match.group(1), 16)
        destination = int(match.group(2), 16)
        opcode = int(match.group(3), 16)
        params_match = match.group(4) or ""
        params = [int(x, 16) for x in (params_match.strip().split() or [])]
        return CECMessage(initiator, destination, opcode, params)

    def run(self) -> None:
        """ continuously parse log_path file """
        debug_print(f"Following {self.log_path}... Ctrl+C to exit.")
        with open(self.log_path, "r", encoding="utf-8") as f:
            f.seek(0, os.SEEK_END)
            while True:
                msg = self.parse_line(f.readline())
                if not msg:
                    time.sleep(0.1)
                    continue

                debug_print(msg)
                for cb in self.callbacks.get(msg.opcode, []):
                    cb(msg)
