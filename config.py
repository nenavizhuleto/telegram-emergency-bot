import os
import sys
import tomli
from dotenv import load_dotenv

MODES = ["ip", "script"]

class Router:
    def __init__(self, addr, user, passwd, command):
        self.address = addr
        self.user = user
        self.password = passwd
        self.command = command

class Config:
    def __init__(self):
        # Reading .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

        with open("config.toml", mode="rb") as fp:
            config = tomli.load(fp)

        if not config:
            raise ValueError("Config file not found")

        # TODO: Validate config schema
        print(config)

        def check_var(name, val, typ):
            if not val or not type(val) is typ:
                print(f"{name} is invalid: required and must be of type {typ}", file=sys.stderr)
                exit(1)
                

        check_var("telegram", config.get("telegram"), dict)
        check_var("security", config.get("security"), dict)
        check_var("routers", config.get("routers"), dict)


        self.TELEGRAM_TOKEN = config["telegram"].get("token")
        check_var("telegram.token", self.TELEGRAM_TOKEN, str)

        self.TELEGRAM_ALLOWED_USERS = config["telegram"].get("users")
        check_var("telegram.users", self.TELEGRAM_ALLOWED_USERS, list)

        self.CONFIRMATION_CODE = config["security"].get("password")
        check_var("security.password", self.CONFIRMATION_CODE, str)


        routers = config["routers"]
        self.ROUTERS = []
        for name in routers:
            r = routers[name]

            addr = r.get("address")
            check_var(f"{name}.address", addr, str)

            user = r.get("user")
            check_var(f"{name}.user", user, str)

            passwd = r.get("password")
            check_var(f"{name}.password", passwd, str)

            cmd = r.get("command")
            check_var(f"{name}.command", cmd, dict)

            cmd_mode = cmd.get("mode")
            check_var(f"{name}.command.mode", cmd_mode, str)

            if cmd_mode not in MODES:
                print(f"command mode must be either ip or script, but {cmd_mode} provided", file=sys.stderr)
                exit(1)

            if cmd_mode == "ip":
                addresses = cmd.get("addresses")
                check_var(f"{name}.command.addresses", addresses, list)

            if cmd_mode == "script":
                name_ = cmd.get("name")
                check_var(f"{name}.command.name", name_, str)

            self.ROUTERS.append(Router(addr, user, passwd, cmd))

config = Config()
