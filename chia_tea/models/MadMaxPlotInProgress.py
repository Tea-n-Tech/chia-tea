from datetime import datetime
from dataclasses import dataclass


class MadMaxPercentages:
    """This class contains the "rough" progress percentages for plotting

    In the future these percentages will be dynamically computed
    and estimated.
    """

    # pylint: disable=too-few-public-methods

    phase1 = (
        0.02232820817,
        0.08422978293,
        0.172304759,
        0.2580199571,
        0.3384422125,
        0.4093906676,
        0.4595129564,
    )
    phase2 = (
        0.4671522489,
        0.4938333946,
        0.5033927017,
        0.5267895266,
        0.5361274338,
        0.5582587301,
        0.5674848834,
        0.5905356127,
        0.6002520189,
        0.6219090798,
        0.6310177749,
        0.6531890657,
    )
    phase3 = (
        0.67627183,
        0.7014293004,
        0.7286114592,
        0.755564902,
        0.7815212812,
        0.8093481191,
        0.8359168967,
        0.8643466994,
        0.892014296,
        0.9206682944,
        0.9560488983,
        0.9878807454,
    )
    phase4 = 1


@dataclass
class MadMaxPlotInProgress:
    """This class represents a plot in progress created by the madmax plotter"""

    # pylint: disable=too-few-public-methods, too-many-instance-attributes

    process_id: int
    public_key: str
    pool_public_key: str
    farmer_public_key: str
    start_time: datetime
    progress: float
    plot_type: int
    state: str
