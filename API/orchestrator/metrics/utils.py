from datetime import datetime
from typing import Dict, List, Tuple

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.manager import CLUSTERS
from orchestrator.models import Task

logger = get_logger(__name__)


def extract_task_group(
    cluster_name: str,
) -> Tuple[Dict[str, List[Task]], int, List[Task]]:
    """
    Extract the task group
    Args:
        cluster_name (str): The cluster name

    Returns:

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

    # sort the task groups by the first task created time
    task_groups = dict(
        sorted(
            task_groups.items(),
            key=lambda x: x[1][0].created_at if len(x[1]) > 0 else None,
        )
    )
    return task_groups, required_tasks_count, tasks


def get_task_names_order(track_id: str) -> List[str]:
    """
    Get the task names order
    Args:
        track_id (str): The track ID

    Returns:
        str: The task names order

    """
    cluster_name = track_id.split("-")[1]
    cluster = CLUSTERS.get(cluster_name)
    task_name_order = [
        item for item in cluster.values() if item["component_type"] == "task"
    ]
    task_name_order = sorted(task_name_order, key=lambda x: x["order"])
    task_names = [item["task_name"] for item in task_name_order]
    return task_names


def str_to_datetime(datetime_str: str) -> datetime:
    """
    Convert the datetime string to datetime object
    Args:
        datetime_str (str): the string datetime, like this: 2024-07-01T14:58:36.419352

    Returns:
        datetime: The datetime object
    """
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
