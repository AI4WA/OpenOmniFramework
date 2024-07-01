from typing import List

import pandas as pd
from django.conf import settings
from datetime import datetime
from authenticate.utils.get_logger import get_logger
from orchestrator.chain.manager import CLUSTER_Q_ETE_CONVERSATION_NAME, CLUSTERS
from orchestrator.models import Task

logger = get_logger(__name__)


class Benchmark:
    """
    For each component, we will generally have two values:
    - model_latency: The time taken by the model to process the data
    - transfer_latency: The time taken to transfer the data to the model
    - overall_latency: The time taken by the model to process the data and transfer the data to the model

    The whole pipeline latency will be the sum of
    - all component start end end ts

    Another way to output the performance is the Timeline
    - start will be 0
    - and average relative time to 0 for each important time point, plot them in the timeline
    """

    def __init__(self, benchmark_cluster: str = CLUSTER_Q_ETE_CONVERSATION_NAME):
        """
        Initialize the benchmark
        Args:
            benchmark_cluster (str): The benchmark cluster
        """
        # if it is a specific name, gather this metric, otherwise, report all existing cluster
        self.benchmark_cluster = benchmark_cluster
        self.benchmark = {}

    def run(self):
        """
        Run the benchmark
        """
        html_content = ""
        if self.benchmark_cluster == "all":
            for cluster_name in CLUSTERS.keys():
                # add a divider
                html_content += "<hr>"
                html_content += f"<h2>Cluster: {cluster_name}</h2>"
                html_content += self.process_cluster(cluster_name)
        else:
            if self.benchmark_cluster not in CLUSTERS:
                raise ValueError(f"Cluster {self.benchmark_cluster} not found")
            html_content += "<hr>"
            html_content += f"<h2>Cluster: {self.benchmark_cluster}</h2>"
            html_content += self.process_cluster(self.benchmark_cluster)
        return html_content

    def process_cluster(self, cluster_name: str):
        """
        Process the cluster
        Args:
            cluster_name (str): The cluster name
        """
        cluster = CLUSTERS.get(cluster_name, None)
        if cluster is None:
            raise ValueError(f"Cluster {cluster_name} not found")

        required_tasks = [
            item for item in cluster.values() if item["component_type"] == "task"
        ]
        required_tasks_count = len(required_tasks)
        logger.info(f"Cluster: {cluster_name}, Required tasks: {required_tasks_count}")
        # get all related tasks, the track_id is like T_{cluster_name}_XXX
        tasks = Task.objects.filter(track_id__startswith=f"T-{cluster_name}-")
        logger.info(f"Cluster: {cluster_name}, Total tasks: {len(tasks)}")
        # group the tasks by the track_id
        task_groups = {}
        for task in tasks:
            track_id = task.track_id
            if track_id not in task_groups:
                task_groups[track_id] = []
            task_groups[track_id].append(task)

        # loop through the task groups, if the success task is not == required_tasks_count, then we will skip
        success_pipeline = 0
        cluster_latency = []
        for track_id, task_group in task_groups.items():
            success_tasks = [
                task for task in task_group if task.result_status == "completed"
            ]
            if len(success_tasks) != required_tasks_count:
                # the pipeline is not completed, so we will skip
                continue
            success_pipeline += 1
            cluster_latency.append(self.process_task_group(task_group))

        logger.info(
            f"""
                Cluster: {cluster_name}, Success Ratio: {success_pipeline}/{len(task_groups)}
                Required tasks: {required_tasks_count}, Total tasks: {len(tasks)}
            """
        )
        # flatten the cluster_latency
        result_df = pd.DataFrame(cluster_latency)
        if len(result_df) != 0:
            logger.info(result_df.describe())
            result_df.to_csv(settings.LOG_DIR / f"{cluster_name}_benchmark.csv")
            # to html and return it
            return result_df.describe().to_html()
        return ""

    @staticmethod
    def process_task_group(task_track: List[Task]):
        """
        This will process each component, and then extract the transfer and model latency total
        Args:
            task_track:

        Returns:
            dict: The benchmark result
        """
        result = {
            "track_id": task_track[0].track_id,
        }
        for task in task_track:
            latency_profile = task.result_json.get("latency_profile", {})
            # NOTE: this will require client side do not log overlap durations
            model_latency = 0
            transfer_latency = 0
            logger.info(latency_profile)
            task_start_time = None
            task_end_time = None
            for key, value in latency_profile.items():
                if key.startswith("model"):
                    print(key, value)
                    model_latency += float(value)
                if key.startswith("transfer"):
                    transfer_latency += float(value)
                if key.startswith("ts"):
                    if key == "ts_start_task":
                        task_start_time = value
                    if key == "ts_end_task":
                        task_end_time = value
            result[f"{task.task_name}_model_latency"] = model_latency
            result[f"{task.task_name}_transfer_latency"] = transfer_latency
            # look for the ts_start_task and ts_end_task, and the overall_latency should be that value
            # process time into datetime object
            # ts_end_trigger_emotion_model 2024-07-01T14:58:36.419352
            if task_start_time and task_end_time:
                task_start_time_dt = Benchmark.str_to_datetime(task_start_time)
                task_end_time_dt = Benchmark.str_to_datetime(task_end_time)
                result[f"{task.task_name}_overall_latency"] = (  # noqa
                    task_end_time_dt - task_start_time_dt
                ).total_seconds()

            else:
                logger.error(f"Task {task.task_name} does not have start and end time")
                result[f"{task.task_name}_overall_latency"] = (
                    model_latency + transfer_latency
                )
        # total_latency should be the sum of all the overall_latency
        total_latency = 0
        for key, value in result.items():
            if key.endswith("overall_latency"):
                total_latency += value
        result["total_latency"] = total_latency
        return result

    @staticmethod
    def str_to_datetime(datetime_str: str) -> datetime:
        """
        Convert the datetime string to datetime object
        Args:
            datetime_str (str): the string datetime, like this: 2024-07-01T14:58:36.419352

        Returns:

        """
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
