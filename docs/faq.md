# Why Chia-Tea?

First and most important we love tea 🍵 and we are not talking about that
heartless, average stuff.
We talk about tea with full-hearted passion and character in it.
In this way we also love to craft software.

Second, we started the library from a single utility script to maintain our
hobby chia farm.
The project grew over time into a fully fledged chia library.
Since we found it especially hard to keep track of our infrastructure, we
designed a monitoring solution for our farm.

## What are important commands for Chia-Tea?

We have a Command Line Interface (CLI) called chia-tea.
It contains all important commands.
For more information see the
[Quick-Start Guide](https://github.com/Tea-n-Tech/chia-tea/blob/main/docs/quick_start.md).

## What can the discord bot do?

Notify on:

- [x] Farmer: Harvester connection/disconnection
- [x] Harvester timeout
- [x] Harvester looses plots
- [x] Harvester: Notify on reward
- [x] Wallet connects/disconnects
- [x] Wallet syncing or loosing sync
- [x] Computer has full RAM
- [x] Computer looses a disk
- [x] Computer timeouts

Commands:

- [x] `$machines`: info about all machines known to the monitoring
- [x] `$harvesters`: reports the status of all connected harvesters
- [x] `$wallets`: reports the status of all wallets
- [x] `$farmers`: reports the status of all farmers
- [x] `$sql`: execute an arbitrary sql cmd on the database (read only)
- [x] `$plotters`: reports on running plotters and their progress
- [x] `$fullnodes`: reports the status of all full nodes being monitored

## How does the monitoring work?

Reconsider the structure of this repository

![Chia-Tea Infrastructure](Chia_Infrastructure.png?raw=true)

In both use scenarios, you in total need three programs to run:

- client: collects all data on a machine
- server: receives all data from connected machines and stores it
- discord bot: provides interaction with the database

On a single machine setup you will run every task on this particular machine.
If you are running a multiple machine setup you can run the monitoring and
server task on one machine whereas on all other machines you will run the
client task.

### Client

To collect data from a system simply run the client on the very same machine.
It collects data from automatically and send it to the server.
This is a lot of information ranging from down-to-earth ram usage to checks if
e.g. a farmer is running to information about every plot of a harvester.

### Server

The server receives the client data and writes it into a database file.
This database file stores all events which ever happened.
You can use this database to build anything on top, such as a dashboard.

### Discord Bot

Our discord bot watches the database for changes and provides notifications in
case something is up.
For example if you loose a drive with plots on or if the wallet is not synced
anymore.
Also there are commands to check on the status of different things.

## What data is being collected?

Briefly answered, everything relevant.
Hardware information such as CPU, RAM, Disks but also system rsources such as
chia specific processes.
We don't monitor absolutely everything (we value a healthy privacy).
If nothing specific to chia is present on the system the monitoring will simply
omit this data.

- Hardware
  - CPU
    - [x] name
    - [x] n_cores
    - [x] clock_speed
    - [x] usage
    - [x] temperature (depends on machine)
  - RAM
    - [x] total/used ram
    - [x] total/used swap
  - Disks
    - [ ] temperature (cannot get without admin rights)
    - [x] total/used space
    - [ ] read/write activity (cannot get without admin rights)
    - [ ] read/write speed (cannot get without admin rights)
    - [ ] read/write total tbw (cannot get without admin rights)
    - [x] device name
    - [x] mountpoint
    - [x] fstype
    - [x] mount options
- Chia
  - Farmer
    - [x] is running
    - [ ] total challenges
    - [x] connected harvester
      - [x] time of connect
      - [x] time of last msg
      - [x] ip address
      - [x] disconnects
      - [x] missed challenges
      - [x] proofs found
    - [x] number of plots
  - Harvester
    - [x] is running
    - [x] plots with details
      - [x] public key (id)
      - [x] filename
      - [x] filesize
      - [x] pool contract puzzle hash
      - [x] size (e.g. 32 for k32)
      - [x] time modified
      - [x] plot seed
      - [ ] disk id
  - Wallet
    - [x] is running
    - [x] is synced
  - Full Node
    - [x] is running
    - [x] is synced
    - [x] sync node height
    - [x] sync blockchain height
  - Plotters (MadMax)
    - [x] plotting process
    - [x] plots in process
      - [x] public key (id)
      - [x] pool_public_key
      - [x] start time
      - [x] progress in percent
      - [x] plotting stage name
  - Chia-related processes
    - [x] process name, executable, command
    - [x] process id
    - [x] creation time
    - [x] cpu usage
    - [x] ram usage
    - [x] opened files
    - [ ] network connections (quite verbose data)
