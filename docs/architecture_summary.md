# Architecture Guide

## Disclaimer

The codebase has evolved very drastically over the last months.
This caused side-effects such as unneccesary functions, complex logic here or
there or obscure classes, which haven't been refactored yet.
Also testing is quite low, since the software architecure changed so much all
the time, that it was too much effort to keep it up in the unstable parts of
the code.
On the road to our first stable release, we will take care of these aspects step
by step.

## Copy-Plots

This module contains code to copy plots from multiple source directories to
multiple target directories.
When choosing a disk it takes multiple factors into account such as how mandy
plots are already being copied onto that drive.
Also the entire process is quite fault-tolerant to disconnects or other issues.
While it is not perfect, it does it's job very well for us.

## Monitoring

### Chia Watchdog

The chia watchdog is the source of chia of data collection.
It is also the oldest part of the code from a time before the monitoring layer
was added.
It consists of a single class `ChiaWatchdog` with additional class members.
These classes are permanently modified by:

- logfile changes
- fetching data directly from chia via API calls
- self-checks run periodically

This information is partially converted into protobuf messages and sent to the
server.
We don't send everything since some data is just for computations.
For example we keep the signage point timestamps to check if a harvester missed
a challenge but sending all that data is a waste.
It makes more sense to simply send the amount of missed challenges and that's
it.

### Protobuf Protocol

The collected chia data needs to be sent from the monitoring clients to the
monitoring server.
The glue for this task is the communication protocol written in
[Protobuf][protobuf].
This protocol defines two things: which data is sent from the monitored machines
to the server but also what data is stored in the database.
The protocol can be found in the folder `protocol` and the generated source
code can be found under `chia_tea.protobuf.generated`.
There is also a [GRPC][grpc] service definition, which defines the communication
functions between server and client.

The module `chia_tea.monitoring.data_collection` converts the `ChiaWatchdog`
data into protobuf messages.
It also contains the code to collect hardware information but this will be
seperated in the future.

### Data Storage

The library uses [`sqlite3`](https://docs.python.org/3/library/sqlite3.html) to
store monitoring data on disk.
There are two types of tables:

There are two important tables:

- Update Event Table
- State Table

The update event table stores all update events ever received for a topic.
For example the `CpuInfoEvents` table contains all cpu data for all machines.
To get a fast and easy overview over the current status there is also a state
table.
In case of the cpu this is `CpuInfo`.
The state table is modified according to the update events, thus if a DELETE
event for example is received an entry will be deleted.

### Table Schema

The state table uses solely `machine_id` as primary key to distinguish entries
whereas events also use `timestamp` and `event_type`.
In case an entry is `repeatable` in protobuf such as a harvester reporting
multiple plots for a single machine, then an additional field `id` is used as
part of the primary key to distinguish data entries.

### Sqlite Schema Generation

The module `chia_tea.protobuf.to_sqlite` is the bridge between protobuf and
sqlite.
It generically defines functions to store or retrieve protobuf messages from
sqlite.
The code is generic so that almost all changes made to the proto files are
automatically handled.
While the code works well, it requires severe refactoring to be more
understandable and usable.

Limitations are at the moment that enums as well as nested messages cannot be
dealt with.

### Throttling

The client only sends data if any changes occured.
This is always the case for strongly varying metrics such as CPU usage.
To avoid spamming the server and thus the database, the submission of such data
is throttled in the client config under `monitoring.client.send_update_every`.
We recommend to transmit such data no faster than once per minute.
Important data such as harvester connectivity is not throttled at all and the
event is transmitted once being captured.

### Connection Security

The connection is secured by two certificates (.key and .cert).
The filepaths are specified in the `config.yml` under `monitoring.auth`.
While the monitoring server requires both files '.key' and '.cert', a client
uses solely '.cert' to authenticate against the server.

### Database Version Compatability

Since the database is generated from protobuf, changing the protocol may
require to delete the old database since the tables are inconsistent.
This will be addressed in the future.
