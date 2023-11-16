use serde::{Deserialize, Serialize};
use ssh2::Session;
use std::{
    io::Read,
    net::{SocketAddr, TcpStream},
};

pub struct Router {
    pub address: SocketAddr,
    pub login: String,
    pub password: String,
    pub session: Session,
}

impl Router {
    pub fn new(address: SocketAddr, login: String, password: String) -> Result<Self, ()> {
        let tcp = TcpStream::connect(address).map_err(|err| {
            eprintln!("ERROR: {err}");
        })?;

        let mut session = Session::new().map_err(|err| {
            eprintln!("ERROR: {err}");
        })?;

        session.set_tcp_stream(tcp);
        session.handshake().map_err(|err| {
            eprintln!("ERROR: {err}");
        })?;

        session
            .userauth_password(&login, &password)
            .map_err(|err| {
                eprintln!("ERROR: {err}");
            })?;

        if !session.authenticated() {
            eprintln!("ERROR: invalid login or password");
            return Err(());
        }

        Ok(Router {
            address,
            login,
            password,
            session,
        })
    }

    pub fn exec(&self, command: &str) -> Result<String, ()> {
        let mut channel = self.session.channel_session().map_err(|err| {
            eprintln!("ERROR: {err}");
        })?;

        channel.exec(command).map_err(|err| {
            eprintln!("ERROR: {err}");
        })?;

        let mut output = String::new();
        channel.read_to_string(&mut output).map_err(|err| {
            eprintln!("ERROR: {err}");
        })?;

        _ = channel.wait_close();
        Ok(output)
    }

    pub fn command<C: Command>(&self, command: C) -> Result<C::Output, ()> {
        if let Ok(stdin) = self.exec(&command.get_cmd()) {
            return command.parse(&stdin);
        } else {
            Err(())
        }
    }
}

pub trait Command {
    type Output;
    fn parse(&self, input: &str) -> Result<Self::Output, ()>;
    fn get_cmd(&self) -> String;
}

pub struct ScriptCmd {
    pub name: String,
}

impl ScriptCmd {
    pub fn new(name: &str) -> Self {
        return ScriptCmd {
            name: name.to_string(),
        };
    }
}

impl Command for ScriptCmd {
    type Output = String;

    fn get_cmd(&self) -> String {
        let cmd = format!("/system script run {}", self.name);
        return cmd;
    }

    fn parse(&self, input: &str) -> Result<Self::Output, ()> {
        return Ok(input.to_string());
    }
}

pub struct ToggleAddressCmd {
    id: i64,
    value: bool,
}

impl ToggleAddressCmd {
    pub fn new(id: i64, value: bool) -> Self {
        return ToggleAddressCmd { id, value };
    }
}

impl Command for ToggleAddressCmd {
    type Output = String;

    fn parse(&self, input: &str) -> Result<Self::Output, ()> {
        return Ok(input.to_string());
    }

    fn get_cmd(&self) -> String {
        let cmd: String;
        if self.value {
            cmd = format!("/ip/address/enable numbers={}", self.id);
        } else {
            cmd = format!("/ip/address/disable numbers={}", self.id);
        }

        return cmd;
    }
}

pub struct IpAddressesCmd {}

impl IpAddressesCmd {
    pub fn new() -> Self {
        return IpAddressesCmd {};
    }
}

impl Command for IpAddressesCmd {
    type Output = Vec<IpAddress>;

    fn get_cmd(&self) -> String {
        return "/ip/address/print terse".to_string();
    }

    fn parse(&self, input: &str) -> Result<Self::Output, ()> {
        let mut output = Vec::new();
        for line in input.trim().lines() {
            let mut id = 0;
            let mut address = String::new();
            let mut network = String::new();
            let mut interface = String::new();
            for (index, slice) in line.split(" ").enumerate() {
                let data = slice.trim();
                match index {
                    0 => id = data.parse().unwrap_or_default(),
                    _ => {
                        let field = data.split("=").nth(0).unwrap_or_default();
                        let value = data.split("=").nth(1).unwrap_or_default();
                        match field {
                            "address" => {
                                address =
                                    value.split("/").take(1).next().unwrap_or(value).to_string()
                            }
                            "network" => network = value.to_string(),
                            "interface" => interface = value.to_string(),
                            _ => {}
                        }
                    }
                }
            }

            output.push(IpAddress {
                id,
                address,
                network,
                interface,
            });
        }

        Ok(output)
    }
}

// Example output
// 0 D address=172.16.229.13/26 network=172.16.229.0 interface=bridge1 actual-interface=bridge1
// 1   address=172.16.229.14/26 network=172.16.229.0 interface=bridge1 actual-interface=bridge1
#[derive(Debug, Serialize, Deserialize)]
pub struct IpAddress {
    pub id: i64,
    pub address: String,
    pub network: String,
    pub interface: String,
}
