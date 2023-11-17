import subprocess
from config import config

def RestrictAccess():
    for r in config.ROUTERS:
        if r.command["mode"] == "ip":
            result = subprocess.run(["scripts/restrict", r.address, r.user, r.password, r.command["mode"], *r.command["addresses"]], stderr=subprocess.PIPE, text=True)
        elif r.command["mode"] == "script":
            result = subprocess.run(["scripts/restrict", r.address, r.user, r.password, r.command["mode"], r.command["name"]], stderr=subprocess.PIPE, text=True)
        else:
            print("unreachable")
            return
        print(result.stderr)
        

def RestrictAccessOld2():
    if config.COMMAND == "ip":
        result = subprocess.run(["scripts/restrict", config.MT_IP_ADDRESS, config.MT_USER, config.MT_PASSWORD, config.COMMAND, *config.RESTRICT_ADDRESSES], stderr=subprocess.PIPE, text=True)
    elif config.COMMAND == "script":
        result = subprocess.run(["scripts/restrict", config.MT_IP_ADDRESS, config.MT_USER, config.MT_PASSWORD, config.COMMAND, config.SCRIPT], stderr=subprocess.PIPE, text=True)
    else:
        return
    print(result.stderr)

def RestrictAccessOld():
    result = subprocess.run(["scripts/restrict_access", config.MT_IP_ADDRESS, config.MT_USER, config.MT_PASSWORD, config.RESTRICT_ADDRESSES], stderr=subprocess.PIPE, text=True)
    print(result.stderr)

