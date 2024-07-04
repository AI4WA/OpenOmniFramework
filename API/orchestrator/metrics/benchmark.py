from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
import plotly.colors as pcolors
import plotly.graph_objects as go
from django.conf import settings

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
                html_content += self.process_cluster(cluster_name)
        else:
            if self.benchmark_cluster not in CLUSTERS:
                raise ValueError(f"Cluster {self.benchmark_cluster} not found")
            html_content += "<hr>"
            html_content += self.process_cluster(self.benchmark_cluster)
        return html_content

    def run_detail(self) -> str:
        html_content = ""
        if self.benchmark_cluster == "all":
            for cluster_name in CLUSTERS.keys():
                # add a divider
                html_content += "<hr>"
                html_content += self.process_cluster_detail(cluster_name)
        else:
            if self.benchmark_cluster not in CLUSTERS:
                raise ValueError(f"Cluster {self.benchmark_cluster} not found")
            html_content += "<hr>"
            html_content += self.process_cluster_detail(self.benchmark_cluster)
        return html_content

    def process_cluster(self, cluster_name: str):
        """
        Process the cluster
        Args:
            cluster_name (str): The cluster name
        """
        task_groups, required_tasks_count, tasks = self.extract_task_group(cluster_name)

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
                Required Components: {required_tasks_count}, Total tasks: {len(tasks)}
            """
        )

        general_title = f"Cluster: <b>{cluster_name}</b>, Completed Ratio: {success_pipeline}/{len(task_groups)}"
        # flatten the cluster_latency
        result_df = pd.DataFrame(cluster_latency)
        # get the column split with _ from right, and left element is the component name

        if len(result_df) != 0:
            logger.info(result_df.describe())
            result_df.to_csv(settings.LOG_DIR / f"{cluster_name}_benchmark.csv")
            # to html and return it
            logger.info(result_df.describe())
            desc = result_df.describe().transpose()
            desc = desc.round(4)

            # add another column
            # Extract model accuracy from index and add it as a new column
            desc["latency_type"] = desc.index.str.rsplit("_", n=2).str[1]
            # then update the index to two columns, first will be component
            desc.index = desc.index.str.rsplit("_", n=2, expand=True).get_level_values(
                0
            )
            # reset index, get the index to be the column component
            desc = desc.reset_index()
            # rename the index to be component
            desc = desc.rename(columns={"index": "component"})
            desc_html = self.plot_table(desc, title=f" ({general_title})")
            plot_html = self.plot_distribution(result_df, title=f" ({general_title})")

            return desc_html + plot_html
        return ""

    def process_cluster_detail(self, cluster_name: str) -> str:
        """
        Process the cluster in detail
        Even if the track is not finished, we will still plot it and stop status
        Args:
            cluster_name (str): html content

        Returns:

        """
        task_groups, required_tasks_count, tasks = self.extract_task_group(cluster_name)

        # loop through the task groups, if the success task is not == required_tasks_count, then we will skip
        success_pipeline = 0
        cluster_latency = []
        cluster_ts_latency = []
        cluster_tp_latency = []
        for track_id, task_group in task_groups.items():
            success_tasks = [
                task for task in task_group if task.result_status == "completed"
            ]
            if len(success_tasks) == required_tasks_count:
                # the pipeline is not completed, so we will skip
                success_pipeline += 1
            cluster_latency.append(self.process_task_group_detail(task_group))
            cluster_ts_latency.append(
                self.process_task_group_detail_timeline(task_group)
            )
            cluster_tp_latency.append(
                self.process_task_group_detail_timeline(task_group, timeline=True)
            )
        general_title = f"Cluster: <b>{cluster_name}</b>, Completed Ratio: {success_pipeline}/{len(task_groups)}"
        result_df = pd.DataFrame(cluster_latency)
        if len(result_df) == 0:
            return ""

        # only keep the last element in the track_id
        result_df["track_id"] = result_df["track_id"].str.split("-").str[-1]
        # get result into multiple level column, which will split current column into multiple level column name
        # Split the column names into three parts, but only keep the first two
        split_columns = result_df.columns.str.rsplit("_", n=2, expand=True)

        # we only need the first two level, so we will get the first two level
        result_df.columns = [
            split_columns.get_level_values(0),
            split_columns.get_level_values(1),
        ]
        # sort the column
        track_tasks_html = self.plot_table(result_df, title=f" ({general_title})")

        # cluster ts latency
        result_ts_df = pd.DataFrame(cluster_ts_latency)
        result_ts_df.to_csv(settings.LOG_DIR / f"{cluster_name}_ts_benchmark.csv")
        if len(result_ts_df) == 0:
            return track_tasks_html
        # we will plot a bar
        ts_stacked_html = self.plot_stacked_timeline(result_ts_df, title=general_title)

        # grab the time point latency, and try to draw time point html
        result_tp_df = pd.DataFrame(cluster_tp_latency)
        # result_tp_df.to_csv(settings.LOG_DIR / f"{cluster_name}_tp_benchmark.csv")
        ts_timepoint_html = self.plot_timestamp_timeline_depth(
            result_tp_df, title=general_title
        )
        return track_tasks_html + ts_stacked_html + ts_timepoint_html

    @staticmethod
    def process_task_group(task_track: List[Task]):
        """
        This will process each component, and then extract the transfer and model latency total

        Args:
            task_track (List[Task]): The task track

        Returns:
            dict: The benchmark result
        """
        result = {
            "track_id": task_track[0].track_id,
        }
        task_names = Benchmark.get_task_names_order(result["track_id"])
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
        # loop all value, get it to decimal 4
        for key, value in result.items():
            if isinstance(value, float):
                result[key] = round(value, 4)

        ordered_result = {
            "track_id": result["track_id"],
        }
        for task_name in task_names:
            ordered_result[task_name + "_model_latency"] = result[
                task_name + "_model_latency"
            ]
            ordered_result[task_name + "_transfer_latency"] = result[
                task_name + "_transfer_latency"
            ]
            ordered_result[task_name + "_overall_latency"] = result[
                task_name + "_overall_latency"
            ]
        ordered_result["total_latency"] = result["total_latency"]
        return ordered_result

    @staticmethod
    def process_task_group_detail(task_track: List[Task]):
        """
        This will process each component, and then extract the transfer and model latency total

        Args:
            task_track (List[Task]): The task track

        Returns:
            dict: The benchmark result
        """
        result = {
            "track_id": task_track[0].track_id,
        }
        task_names = Benchmark.get_task_names_order(result["track_id"])
        for task in task_track:
            if task.result_status != "completed":
                result[f"{task.task_name}_model_latency"] = task.result_status
                result[f"{task.task_name}_transfer_latency"] = task.result_status
                result[f"{task.task_name}_overall_latency"] = task.result_status
                continue
            latency_profile = task.result_json.get("latency_profile", {})
            # NOTE: this will require client side do not log overlap durations
            model_latency = 0
            transfer_latency = 0
            logger.debug(latency_profile)
            task_start_time = None
            task_end_time = None
            for key, value in latency_profile.items():
                if key.startswith("model"):
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

        # sort the key to be the same as the cluster order, also if missed, fill it with missing
        for task_name in task_names:
            if f"{task_name}_overall_latency" not in result:
                result[task_name + "_model_latency"] = "missing"
                result[task_name + "_transfer_latency"] = "missing"
                result[task_name + "_overall_latency"] = "missing"

        # total_latency should be the sum of all the overall_latency
        total_latency = 0
        for key, value in result.items():
            if key.endswith("overall_latency") and isinstance(value, float):
                total_latency += value
            elif key.endswith("overall_latency") and not isinstance(value, float):
                total_latency = "incomplete"
                break
        result["total_latency"] = total_latency
        # loop all value, get it to decimal 4
        for key, value in result.items():
            if isinstance(value, float):
                result[key] = round(value, 4)

        ordered_result = {
            "track_id": result["track_id"],
        }
        for task_name in task_names:
            ordered_result[task_name + "_model_latency"] = result[
                task_name + "_model_latency"
            ]
            ordered_result[task_name + "_transfer_latency"] = result[
                task_name + "_transfer_latency"
            ]
            ordered_result[task_name + "_overall_latency"] = result[
                task_name + "_overall_latency"
            ]

        ordered_result["total_latency"] = result["total_latency"]
        return ordered_result

    @staticmethod
    def process_task_group_detail_timeline(
        task_track: List[Task], timeline: bool = False
    ):
        """
        Based on the result_json => latency_profile
        We will gather the time point for each, and then change to the relative second value compared to start point

        If timeline is True, we will only grab the timestamp information.
        Otherwise, we will calculate the relative time to the start point

        In the end, we will grab the
        Args:
            task_track (List[Task]): The task track
            timeline (bool): If we want to plot the timeline

        Returns:

        """
        result = {
            "track_id": task_track[0].track_id,
        }

        task_names = Benchmark.get_task_names_order(result["track_id"])

        task_results = {}
        for task in task_track:
            if task.result_status != "completed":
                continue
            latency_profile = task.result_json.get("latency_profile", {})
            task_result = {}
            for key, value in latency_profile.items():
                if key.startswith("ts"):
                    task_result[key] = Benchmark.str_to_datetime(value)

            if timeline is False:
                # sort out the whole task_result based on time timestamp
                # and then calculate the relative time to the previous component
                sorted_task_result = dict(
                    sorted(task_result.items(), key=lambda item: item[1])
                )
                previous_time = None
                task_relative_time = {}
                for key, value in sorted_task_result.items():
                    if previous_time is None:
                        task_relative_time[key] = 0
                    else:
                        task_relative_time[key] = (
                            value - previous_time
                        ).total_seconds()
                    previous_time = value
                task_results[task.task_name] = task_relative_time
            else:
                task_results[task.task_name] = task_result

        # sort the key to be the same as the cluster order, calculate the value to add up the previous component
        first_start_task = None
        for task_name in task_names:
            if task_name not in task_results:
                break
            for key, value in task_results[task_name].items():
                new_key = f"{task_name}_{key.split('_', 1)[1]}"
                if key == "ts_start_task":
                    if first_start_task is None:
                        first_start_task = value
                    else:
                        continue
                if new_key not in result:
                    result[new_key] = value

        logger.info(result)
        return result

    @staticmethod
    def plot_table(df: pd.DataFrame, title: str = "") -> str:
        """
        Plot the table
        Args:
            df (pd.DataFrame): The dataframe
            title (str): The title

        Returns:
            str: The plot in HTML
        """
        colors = []
        for col in df.columns:
            col_colors = []
            for val in df[col]:
                if isinstance(val, float) or isinstance(val, int):
                    col_colors.append("lavender")
                else:
                    if val == "missing":
                        col_colors.append("lightcoral")
                    elif val == "started":
                        col_colors.append("lightyellow")
                    elif val == "failed":
                        col_colors.append("lightcoral")
                    elif val == "pending":
                        col_colors.append("lightblue")
                    elif val == "incomplete":
                        col_colors.append("lightgrey")
                    else:
                        col_colors.append("lightgreen")
            colors.append(col_colors)
        # Create a Plotly table
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=[
                            (
                                [f"<b>{c.upper()}</b>" for c in col]
                                if isinstance(col, tuple)
                                else f"<b>{col.upper()}</b>"
                            )
                            for col in df.columns
                        ],
                        fill_color="paleturquoise",
                        align="left",
                    ),
                    cells=dict(
                        values=[df[col] for col in df.columns],
                        fill_color=colors,
                        align="left",
                    ),
                )
            ]
        )
        fig.update_layout(
            title={
                "text": f"Latency Summary: {title}",
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            #     update margin to be 0
            margin=dict(l=10, r=10, b=0),
            # get the height to be whatever it requires
            height=max((len(df) * 35), 300),
        )
        # Update layout for better appearance
        desc_html = fig.to_html(full_html=False)
        return desc_html

    @staticmethod
    def plot_distribution(df: pd.DataFrame, title: str = "") -> str:
        """
        Plot the distribution of the latency
        Args:
            df (pd.DataFrame): The dataframe
            title (str): The title

        Returns:
            str: The plot in HTML
        """
        # plot the distribution for each column
        # Calculate mean and max for each latency column
        mean_latencies = df[df.columns[1:]].mean()
        max_latencies = df[df.columns[1:]].max()
        min_latencies = df[df.columns[1:]].min()

        # Create a Plotly figure
        fig = go.Figure()
        # Add min latencies to the figure
        fig.add_trace(
            go.Bar(x=min_latencies.index, y=min_latencies.values, name="Min Latency")
        )
        # Add mean latencies to the figure
        fig.add_trace(
            go.Bar(x=mean_latencies.index, y=mean_latencies.values, name="Mean Latency")
        )

        # Add max latencies to the figure
        fig.add_trace(
            go.Bar(x=max_latencies.index, y=max_latencies.values, name="Max Latency")
        )

        # Customize the layout
        fig.update_layout(
            title={
                "text": "Latency Distribution" + title,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            xaxis_title="Component and Latency",
            yaxis_title="Latency (s)",
            barmode="group",
            margin=dict(l=10, r=10, b=0),
        )

        # Convert Plotly figure to HTML
        plot_html = fig.to_html(full_html=False)
        return plot_html

    @staticmethod
    def plot_stacked_timeline(df: pd.DataFrame, title: str) -> str:
        """
        Plot the stacked timeline
        Args:
            df (pd.DataFrame): The dataframe
            title (str): The title

        Returns:

        """
        # Create a Plotly figure
        fig = go.Figure()
        # get the track id to be the stacked one
        df["track_id"] = df["track_id"].str.split("-").str[-1]
        # Add a trace for each component
        for col in df.columns[1:]:
            fig.add_trace(
                go.Bar(
                    y=df["track_id"],
                    x=df[col],
                    name=col,
                    orientation="h",
                    hovertemplate="%{x}<br>%{fullData.name}<extra></extra>",
                )
            )

        # Customize the layout
        fig.update_layout(
            title={
                "text": f"Time Interval in Seconds ({title})",
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            xaxis_title="Relative in Seconds to Start Time",
            yaxis_title="Track ID",
            barmode="stack",
            height=max((len(df) * 35), 300),
        )

        # Convert Plotly figure to HTML
        plot_html = fig.to_html(full_html=False)
        return plot_html

    @staticmethod
    def plot_timestamp_timeline_depth(df: pd.DataFrame, title: str) -> str:
        """
        Plot the timestamp timeline
        Args:
            df (pd.DataFrame): The dataframe
            title (str): The title

        Returns:
            str: The plot in HTML
        """
        fig = go.Figure()
        y_values = list(range(len(df)))
        shapes = []
        for y_value in y_values:
            shapes.append(
                dict(
                    type="line",
                    xref="paper",
                    x0=0,
                    x1=1,
                    yref="y",
                    y0=y_value,
                    y1=y_value,
                    line=dict(color="grey", width=1, dash="dot"),
                )
            )
        y_labels = []

        legend_added = {}
        # Use Plotly's qualitative color sequence 'Dark24' to generate a spectrum of colors
        colors = pcolors.qualitative.Dark24

        # Dynamically generate a color map for each column
        column_colors = {
            col: colors[i % len(colors)] for i, col in enumerate(df.columns[1:])
        }
        for i, row in df.iterrows():
            y_value = y_values[i]
            y_labels.append(row["track_id"].split("-")[-1])
            for col in df.columns[1:]:
                logger.info(col)
                if not pd.isna(row[col]):
                    show_legend = False
                    if col not in legend_added:
                        show_legend = True
                        legend_added[col] = True
                    fig.add_trace(
                        go.Scatter(
                            x=[row[col]],
                            y=[y_value],
                            mode="markers",
                            marker=dict(size=10, color=column_colors[col]),
                            name=f"{col}",
                            hovertemplate="%{x}<br>%{fullData.name}<extra></extra>",
                            showlegend=show_legend,
                        )
                    )
        # Customize the layout
        fig.update_layout(
            title={
                "text": f"Timeline of Events ({title})",
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            xaxis_title="Time",
            yaxis=dict(
                showline=False,
                showgrid=True,
                zeroline=False,
                tickvals=y_values,
                ticktext=y_labels,
                title="Track ID",
            ),
            showlegend=True,
            shapes=shapes,
            height=max((len(df) * 35), 300),
        )
        # Convert Plotly figure to HTML
        plot_html = fig.to_html(full_html=False)
        return plot_html

    @staticmethod
    def plot_timestamp_timeline(df: pd.DataFrame) -> str:
        """
        Plot the timestamp timeline
        Args:
            df (pd.DataFrame): The dataframe

        Returns:
            str: The plot in HTML
        """
        fig = go.Figure()
        y_values = range(len(df))

        for i, row in df.iterrows():
            y_value = y_values[i]
            for col in df.columns[1:]:
                if not pd.isna(row[col]):
                    fig.add_trace(
                        go.Scatter(
                            x=[row[col]],
                            y=[y_value],
                            mode="markers",
                            marker=dict(size=10),
                            name=f"{col}",
                            hovertemplate="%{x}<br>%{fullData.name}<extra></extra>",
                        )
                    )
            # break
        # Customize the layout
        fig.update_layout(
            title="Timeline of Time Points",
            xaxis_title="Time",
            # show nothing of y, even the label
            yaxis=dict(
                showticklabels=False, showline=False, showgrid=False, zeroline=True
            ),
            showlegend=True,
        )
        # Convert Plotly figure to HTML
        plot_html = fig.to_html(full_html=False)
        return plot_html

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def str_to_datetime(datetime_str: str) -> datetime:
        """
        Convert the datetime string to datetime object
        Args:
            datetime_str (str): the string datetime, like this: 2024-07-01T14:58:36.419352

        Returns:
            datetime: The datetime object
        """
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
