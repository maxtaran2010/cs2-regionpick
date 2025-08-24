import requests
import subprocess
import platform



def block_unblock_ips(ips, block=True):
    for ip in ips:
        rule_name = f"CS2ServerPicker_{ip.replace('.', '_')}"
        if block:
            cmd = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={rule_name}",
                "dir=out", "action=block", "protocol=ANY", f"remoteip={ip}"
            ]
        else:
            cmd = [
                "netsh", "advfirewall", "firewall", "delete", "rule",
                f"name={rule_name}"
            ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to {'block' if block else 'unblock'} {ip}: {result.stderr}")
        else:
            print(f"{'Blocked' if block else 'Unblocked'} {ip}")


def ping(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip]
    try:
        output = subprocess.check_output(command, universal_newlines=True)
        # Parse output for latency
        if platform.system().lower() == 'windows':
            import re
            match = re.search(r'Average = (\d+)ms', output)
            if match:
                return int(match.group(1))
        else:
            import re
            match = re.search(r'time=(\d+\.?\d*) ms', output)
            if match:
                return float(match.group(1))
    except Exception as e:
        return None
    return None


def unblock_all():
    # List all firewall rules and remove those starting with "CS2"
    list_cmd = [
        "netsh", "advfirewall", "firewall", "show", "rule", "name=all"
    ]
    result = subprocess.run(list_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to list firewall rules: {result.stderr}")
        return

    import re
    rule_names = set()
    for line in result.stdout.splitlines():
        match = re.match(r"^Rule Name:\s*(CS2[^\r\n]*)", line)
        if match:
            rule_names.add(match.group(1).strip())

    for rule_name in rule_names:
        del_cmd = [
            "netsh", "advfirewall", "firewall", "delete", "rule",
            f"name={rule_name}"
        ]
        del_result = subprocess.run(del_cmd, capture_output=True, text=True)
        if del_result.returncode == 0:
            print(f"Unblocked rule: {rule_name}")
        else:
            print(f"Failed to unblock rule {rule_name}: {del_result.stderr}")



req = requests.get('https://api.steampowered.com/ISteamApps/GetSDRConfig/v1/?appid=730')
req = req.json()
servers = req['pops']
regions = servers.keys()
blockorunblock = int(input("FORCE REGION OR RESET (1/2): "))
if blockorunblock == 2:
    unblock_all()
    quit()

print("AVALIBLE REGIONS: ")
acutalregions = {}
for rg in servers:
    region = servers[rg]
    tmpx = region["desc"].rfind("(")
    if tmpx != -1:
        country = region["desc"][tmpx+1:-1].split(",")[0]
    else:
        country = region["desc"]

    if "Hong Kong" in country:
        country = "Hong Kong"
    if acutalregions.get(country):
        acutalregions[country].append(rg)
    else:
        acutalregions[country] = [rg]
x = ""
for i in acutalregions.keys():
    x += i + ", "
print(x)
regionpick = input("SELECT REGION: ")
import json


matching_regions = acutalregions[regionpick]
print("Matching regions '{}':".format(regionpick))
for region in matching_regions:
    print(region)
input("Confirm?")

relays = []
for region in regions:
    if region in matching_regions:
        continue
    if servers[region].get('relays'):
        relays.extend(servers[region]['relays'])
ips = []
for relay in relays:
    ips.append(relay['ipv4'])



unblock_all()

block_unblock_ips(ips, block=True)


