# Chia-Tea Quick Start

This guide is for getting started using Chia-Tea.

## Table of Contents

- [What can I do with Chia-Tea?](#what-can-i-do-with-chia-tea)
- [How to install Chia-Tea?](#how-to-install-chia-tea)
- [How to configure Chia-Tea?](#how-to-configure-chia-tea)
- [How to start the copy tool?](#how-to-start-the-copy-tool)
- [How to monitor my farm?](#how-to-monitor-my-farm)

## What can I do with Chia-Tea?

There are currently three major use-cases:

- Copy plots between drives
- Monitoring of a single or multi-machine chia farm
- Discord bot to give notifications and allow interaction

## How to install Chia-Tea?

You can install it as usualy by using the python package manager:

```bash
python -m pip install chia-tea
```

Alternatively you can also clone the repo and install the code manually:

```bash
git clone https://github.com/Tea-n-Tech/chia-tea.git
python -m pip install poetry
python -m poetry install
python -m poetry build
python -m pip install dist/*.whl
```

## How to configure Chia-Tea?

To create a config simply run:

```
chia-tea config init
```

All configurations are stored in a `config.yml` file.
Every cli tools uses this config and searches by default for
a file `~/.chia_tea/config/config.yml`.
You can get the path to the config by running

```
chia-tea config location
```

If you create the config in another location, you can also specify the path to
the config by using the `--config` option for every start command.

After creating the config and possibly adapting it, you can start processes as
listed below.

## How to start the copy tool?

You can start the copy tool with:

```
chia-tea start copy
```

It will then copy plots between the `copy.source_folders` drives to the
`copy.target_folders` drives as specified in the `config.yml`.

## How to monitor my farm?

You initialized already the config but also need certificates to secure the
connection between server and client.
To create the certificates simply run:

```
chia-tea config create-certificates
```

And they will be created next to the config.
The certificates work by default only on your machine!
If you have a setup over a network, you must specify the monitoring server name
with the option `--common-name` or you will get a
`No match found for server name` error on the server when clients try to connect
to it.
The server name can be the ip address or a url.
As a note, the client only requires the `.cert` certificate file and not
the private `.key` file.

The monitoring server receives all monitoring data and stores it in a file
called `monitoring.db`, but this can be changed in the config under
`monitoring.server.db_filepath`.
You can start the server now by running:

```
chia-tea start monitoring-server
```

After starting a server you can connect an arbitrary amount of clients to it.
Clients are programs run on machines you want to monitor.
A client collects data from the hardware, processes and chia and sends it to
the server.
You can control the the data collection frequency in the config under
`monitoring.client` but the default should suffice for the beginning.

Simply run the following command and Chia-Tea will collect and send all data
automatically to the server:

```
chia-tea start monitoring-client
```

We have a discord bot as a user interface to the database.
It will notify you on any important events and provide commands to get further
insights.

Before you can run the bot you will need a
[Discord Bot Token](https://www.writebots.com/discord-bot-token/) and also the
id of your channel.
Specify this once again in the `config.yml` under `discord`.

You can run the bot with:

```
chia-tea start discord-bot
```

And here you go, you are all set up.
