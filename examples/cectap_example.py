""" example script """
import os
from cectap import CECMonitor, CECMessage
from cectap.helpers import HyperHDRController

cec_monitor = CECMonitor()
hyper_hdr = HyperHDRController()
debug_print = print if os.getenv("DEBUG") == "1" else lambda *a, **k: None

@cec_monitor.on("VENDOR_COMMAND_WITH_ID")
def handle_vendor_command(msg: CECMessage):
    """ handle sony avamp specific codes """
    if msg.params == [8, 0, 70, 0, 9, 0, 1]:
        print("TV Powered off")
        hyper_hdr.leds_off()

    if msg.params == [8, 0, 70, 0, 12, 0, 255]:
        print("TV Powered on")
        hyper_hdr.leds_on()

@cec_monitor.on("ROUTING_CHANGE")
def handle_routing_change(msg: CECMessage) -> bool:
    """ handle sony avamp input changes """
    destination = msg.params[2] if len(msg.params) == 4 else None
    if destination == 18:
        print("Switched to Kodi input")
        ret = os.system("DISPLAY=:0 /usr/bin/xrandr --output DP2 --mode 1920x1080 --rate 59.94")
        if ret > 0:
            debug_print("xrandr command failed")
        return not bool(ret)

    if destination == 17:
        print("Switched to Steam input")

    return True

@cec_monitor.on("SET_STREAM_PATH")
def handle_stream_path(msg: CECMessage) -> None:
    """ print stream path updates to stdout """
    print(f"Stream path updated: {msg}")

@cec_monitor.on("USER_CONTROL_PRESSED")
def handle_keypress(msg: CECMessage) -> None:
    """ handle remote button presses """
    if msg.params:
        keycode = msg.params[0]
        print(f"Key press detected: code={keycode:02X}")

if __name__ == "__main__":
    cec_monitor.run()
