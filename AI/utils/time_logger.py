from datetime import datetime

"""
For the latency

If it is model, the name will start with model_xx, and it is a duration
If it is transfer time, the name will start with transfer_xx, and it is a duration
If it is just to log the timestamp, the name will start with ts_xx, and it is a timestamp
"""


class TimeLogger:

    @staticmethod
    def log(profile: dict, name: str):
        """
        Log the time taken to execute a block of code
        Args:
            profile (dict): The profile to store the time
            name (str): The name of the block

        Returns:

        """
        profile[f"ts_{name}"] = datetime.now()
