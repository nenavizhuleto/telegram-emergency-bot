import subprocess
from config import config

def RestrictAccess():
    result = subprocess.run(["scripts/restrict_access", config.MT_IP_ADDRESS, config.MT_USER, config.MT_PASSWORD, config.RESTRICT_ADDRESSES], stderr=subprocess.PIPE, text=True)
    print(result.stderr)


