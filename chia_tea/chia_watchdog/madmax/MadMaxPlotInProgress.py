from datetime import datetime


class MadMaxPlotInProgress:
    def __init__(
        self,
        public_key: str,
        pool_public_key: str,
        start_time: datetime,
        end_time: datetime,
        progress: float,
        end_time_copy: datetime,
    ) -> None:
        """
        Parameters
        ----------
        public_key: str
            public key of the plot
        pool_public_key: str
            public key of the pool
        start_time: datetime
            time plotting started
        end_time: datetime
            time plotting finished
        progress: float
            precentage of progress
        end_time_copy : datetime
            time copying finished
        """
        self.public_key = public_key
        self.pool_public_key = pool_public_key
        self.start_time = start_time
        self.end_time = end_time
        self.progress = progress
        self.end_time_copy = end_time_copy

    def copy(self) -> "MadMaxPlotInProgress":
        """Get a copy of the instance

        Returns
        -------
        plot : MadMaxPlotInProgress
            copy of this instance
        """
        return MadMaxPlotInProgress(
            public_key=self.public_key,
            pool_public_key=self.pool_public_key,
            start_time=self.start_time,
            end_time=self.end_time,
            progress=self.progress,
            end_time_copy=self.end_time_copy,
        )
