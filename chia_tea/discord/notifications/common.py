
from ...protobuf.generated.machine_info_pb2 import MachineInfo


def get_machine_info_name(machine: MachineInfo) -> str:
    """ Get a nicely formatted name for a machine info

    Parameters
    ----------
    machine : MachineInfo
        machine info to get a name of

    Returns
    -------
    name : str
        nicely formatted name of the machine info
    """

    return "{name} {id} ({ip})".format(
        name=f"{machine.name} -" if machine.name else "",
        id=str(machine.machine_id)[:10],
        ip=machine.ip_address,
    )
