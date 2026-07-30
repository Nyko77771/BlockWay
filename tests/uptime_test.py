import psutil
import time

def test_uptime():
    seconds = time.time() - psutil.boot_time()
    print(f"Uptime Seconds: {seconds:.0f}")
    minutes = seconds/ 60
    print(f"Uptime Minutes: {int(minutes):.0f}")
