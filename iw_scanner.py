import psutil
from settings import SUDO_PW

import re
import subprocess

cellNumberRe = re.compile(r"^Cell\s+(?P<cellnumber>.+)\s+-\s+Address:\s(?P<mac>.+)$")
regexps = [
    re.compile(r"^ESSID:\"(?P<essid>.*)\"$"),
    re.compile(r"^Protocol:(?P<protocol>.+)$"),
    re.compile(r"^Frequency:(?P<frequency>[\d.]+) (?P<frequency_units>.+) \(Channel (?P<channel>\d+)\)$"),
    re.compile(r"^Quality=(?P<signal_quality>\d+)/(?P<signal_total>\d+)\s+Signal level=(?P<signal_level_dBm>.+) d.+$"),
    re.compile(r"^Signal level=(?P<signal_quality>\d+)/(?P<signal_total>\d+).*$"),
]

# Must run as super user.
def scan(interface='wlan0'):
    cmd = ["sudo", "-S", "iwlist", interface, "scan"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate(SUDO_PW.encode())
    points = out.decode()
    return points

def parse(content):
    cells = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        cellNumber = cellNumberRe.search(line)
        if cellNumber is not None:
            cells.append(cellNumber.groupdict())
            continue
        for expression in regexps:
            result = expression.search(line)
            if result is not None:
                cells[-1].update(result.groupdict())
                continue
    return cells

def scanAndParse(interface):
    content = scan(interface)
    return parse(content)

def determinePacketCount(interface='wlan0'):
    multiplier = 50 #scan all networks approximately this many times
    parsed_content = scanAndParse(interface)
    networks_count = len(parsed_content)
    return networks_count * multiplier

def doMultipleScans(interface):
    ssid_dict = {}
    signal_str_min_dict = {}
    signal_str_max_dict = {}
    signal_str = None
    bssid = None
    ssid = None
    for i in range(10):
        data = scanAndParse(interface)
        for cell in data:
            if 'mac' in cell:
                bssid = cell['mac']
            if 'essid' in cell:
                if cell['essid'] == '':
                    ssid = 'Unknown name'
                else:
                    ssid = cell['essid']
            if 'signal_level_dBm' in cell:
                signal_str = int(cell['signal_level_dBm'])

            if not bssid in ssid_dict:
                ssid_dict[bssid] = ssid

            if bssid in signal_str_min_dict:
                if signal_str < signal_str_min_dict[bssid]:
                    signal_str_min_dict[bssid] = signal_str
            else:
                signal_str_min_dict[bssid] = signal_str

            if bssid in signal_str_max_dict:
                if signal_str > signal_str_max_dict[bssid]:
                    signal_str_max_dict[bssid] = signal_str
            else:
                signal_str_max_dict[bssid] = signal_str

            signal_str = None
            bssid = None
            ssid = None

    return ssid_dict, signal_str_min_dict, signal_str_max_dict

### for future use - to figure out which interface to scan on automatically
#addrs = psutil.net_if_addrs()
#for interface in addrs.keys():
#    print(interface)