extern crate mikrotool;
use mikrotool::{IpAddressesCmd, Router, ScriptCmd, ToggleAddressCmd};

use std::{env::Args, net::SocketAddr};

// ARGS:
// - Mikrotik IP Address and Port: 127.0.0.1:1234
// - Mikrotik User
// - Mikrotik Password
// - Command: "ip" | "script"
//      - ip:
//
//      - script:
//          - Script Name
//
// -----------------------------

fn print_help() {
    println!(
        r#"
     Usage: restrict IP:PORT USER PASSWORD COMMAND [PARAMS]
     COMMAND: ip | script
        Arguments:
            - ip: ADDR/NET ADDR/NET ... ADDR/NET
            - script: NAME
             "#
    )
}

enum Cmd {
    Ip { addrs: Vec<String> },
    Script { name: String },
    Unknown { cmd: String },
}

impl Cmd {
    fn from_args(args: &mut Args) -> Cmd {
        let cmd = args.next().expect("COMMAND is required");
        match cmd.as_str() {
            "ip" => {
                let mut addrs: Vec<String> = vec![];
                while let Some(addr) = args.next() {
                    addrs.push(addr);
                }
                if addrs.len() == 0 {
                    panic!("specify at least one address");
                }
                return Cmd::Ip { addrs };
            }
            "script" => Cmd::Script {
                name: args.next().expect("script name is required"),
            },
            _ => Cmd::Unknown { cmd },
        }
    }
}

fn connect(addr: SocketAddr, user: &str, password: &str) -> Router {
    let r = Router::new(addr, user.to_string(), password.to_string()).expect("Router error");
    return r;
}

fn main() -> Result<(), ()> {
    let mut args = std::env::args();
    if args.len() <= 4 {
        print_help();
        return Err(());
    }

    let _program_name = args.next();

    let addr: SocketAddr = args
        .next()
        .expect("IP:PORT is required")
        .parse()
        .expect("IP:PORT is invalid");

    let user = args.next().expect("USER is required");
    let password = args.next().expect("PASSWORD is required");
    let command = Cmd::from_args(&mut args);

    match command {
        Cmd::Ip { addrs } => {
            let r = connect(addr, &user, &password);
            if let Ok(addresses) = r.command(IpAddressesCmd::new()) {
                for addr in addrs {
                    let address = addresses.iter().find(|&v| v.address == addr);
                    if let Some(addr) = address {
                        // Disable address here
                        let o = r.command(ToggleAddressCmd::new(addr.id, false));
                        println!("{:#?}", o);
                    } else {
                        println!("address not found: {}", addr);
                    }
                }
            }
        }
        Cmd::Script { name } => {
            let r = connect(addr, &user, &password);
            let o = r.command(ScriptCmd::new(&name));
            println!("{:#?}", o);
        }
        Cmd::Unknown { cmd } => {
            println!("Unknown command: {}", cmd);
            return Err(());
        }
    }

    Ok(())
}
