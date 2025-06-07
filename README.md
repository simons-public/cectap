## cectap

This project includes a patch for LibCEC that writes cec events to a log (/tmp/cec.log) and a library for parsing the log file and running callback functions.

### libcec_patch 
There are two patches. `ceclog.patch` which can be applied to the libcec project directly, and `archlinux-libcec-pkgbuild.patch` which can be applied to the PKGBUILD for libcec with `git apply archlinux-libcec-pkgbuild.patch` in the directory (with ceclog.patch in the same directory). The log path can be changed in the patch, but keep in mind permissions of the user running the program using libcec.

### cectap library
The `examples` directory has an example for using the cectap library, as well as an example systemd service. 

```python
from cectap import CECMonitor, CECMessage
from cectap.helpers import HyperHDRController

cec_monitor = CECMonitor(log_path="/tmp/cec.log")
hyper_hdr = HyperHDRController(host="localhost", port=8090)
debug_print = print if os.getenv("DEBUG") == "1" else lambda *a, **k: None

@cec_monitor.on("VENDOR_COMMAND_WITH_ID")
def handle_vendor_command(msg: CECMessage):
    """ handle sony avamp specific codes """
    if msg.params == [8, 0, 70, 0, 9, 0, 1]:
        print("TV Powered off")
        hyper_hdr.leds_off()
```

### example setup with a virtual environment
``` shell
python -m venv --system-site-packages cectap_venv
./cectap_venv/bin/pip install git+https://github.com/simons-public/cectap
./cectap_venv/bin/python cectap_example.py
````