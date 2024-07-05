from typing import List

import jiwer
import pandas as pd
import plotly.graph_objects as go

from authenticate.utils.get_logger import get_logger
from hardware.forms import (
    MultiModalAnnotationForm,
    MultiModalFKEmotionDetectionAnnotationForm,
)
from hardware.models import ContextEmotionDetection, DataMultiModalConversation
from orchestrator.chain.manager import CLUSTER_Q_ETE_CONVERSATION_NAME, CLUSTERS
from orchestrator.metrics.utils import extract_task_group
from orchestrator.models import Task

logger = get_logger(__name__)


class AccuracyBenchmark:
    def __init__(self, benchmark_cluster: str = CLUSTER_Q_ETE_CONVERSATION_NAME):
        """
        Initialize the benchmark
        Args:
            benchmark_cluster (str): The benchmark cluster
        """
        # if it is a specific name, gather this metric, otherwise, report all existing cluster
        self.benchmark_cluster = benchmark_cluster

    def benchmark_run(self):
        """
        Run the benchmark
        """
        logger.info(f"Running accuracy benchmark for cluster {self.benchmark_cluster}")
        # run the benchmark
        html_content = ""
        if self.benchmark_cluster == "all":
            for cluster_name in CLUSTERS.keys():
                html_content += "<hr>"
                html_content += self.process_cluster_benchmark(
                    cluster_name, detailed=False
                )
        else:
            html_content += self.process_cluster_benchmark(
                self.benchmark_cluster, detailed=False
            )
        return html_content

    def process_cluster_benchmark(
        self, cluster_name: str, detailed: bool = False
    ) -> str:
        """
        Process the benchmark for a specific cluster

        For each cluster, we will need to analyse the conversation model
        And also need to understand what's the else model we need to analyse, for example the emotion_detection
        Args:
             cluster_name (str): The cluster name
            detailed (bool): The detailed flag

        Returns:
            str: The HTML content
        """
        task_groups, required_tasks_count, tasks = extract_task_group(cluster_name)

        required_annotation_task = self.extract_required_annotation_models(cluster_name)
        logger.info(
            f"Cluster: {cluster_name}, Required annotation tasks: {required_annotation_task}"
        )
        conversations = DataMultiModalConversation.objects.filter(
            track_id__startswith=f"T-{cluster_name}-"
        ).order_by("-created_at")

        html_content = f"<h2>Cluster: {cluster_name}</h2>"
        html_content += (
            f"<p>Required tasks each group: {required_tasks_count} ｜ "
            f"Annotation task groups: {len(conversations)}</p>"
        )

        # the emotion and other context results also will be pulled from this one
        # then we will according to this to load the annotation results
        # track id and annotation => flatten the results
        annotations = []
        annotation_expected_keys = MultiModalAnnotationForm.declared_fields.keys()
        annotation_pending_default = {
            key: "pending" for key in annotation_expected_keys
        }

        for conversation in conversations:
            conversation_annotation = conversation.annotations
            annotated = False
            for user_id, annotation in conversation_annotation.items():
                annotations.append(
                    {
                        "track_id": conversation.track_id,
                        "user_id": user_id,
                        "predict_text": conversation.text.text,
                        **annotation_pending_default,
                        **annotation,
                    }
                )
                annotated = True
            if not annotated:
                annotations.append(
                    {
                        "track_id": conversation.track_id,
                        "user_id": "missing",
                        **annotation_pending_default,
                    }
                )

        conversation_annotation_df = pd.DataFrame(annotations)
        if len(conversation_annotation_df) == 0:
            return html_content + "<p>No conversation annotation found</p>"
        # transform the track_id to be the last part
        conversation_annotation_df["track_id"] = (
            conversation_annotation_df["track_id"].str.split("-").str[-1]
        )
        # replace all the column names, remove the annotation prefix
        conversation_annotation_df.columns = [
            col.replace("annotation_", "") for col in conversation_annotation_df.columns
        ]
        # add CER and WER
        conversation_annotation_df = self.calculate_speech2text_accuracy(
            conversation_annotation_df
        )

        if detailed:
            # then we will present them into multiple tables: speech2text, text_generation, text2speech, overall
            if "speech2text" in required_annotation_task:
                speech2text_df = conversation_annotation_df[
                    [
                        "track_id",
                        "user_id",
                        "predict_text",
                        "speech2text",
                        "wer",
                        "cer",
                        "speech2text_score",
                    ]
                ].copy(deep=True)
                html_content += self.plot_table(speech2text_df, "Speech2Text")
            if "text_generation" in required_annotation_task:
                text_generation_df = conversation_annotation_df[
                    ["track_id", "user_id", "text_generation", "text_generation_score"]
                ].copy(deep=True)
                html_content += self.plot_table(text_generation_df, "Text Generation")
            if "text2speech" in required_annotation_task:
                text2speech_df = conversation_annotation_df[
                    ["track_id", "user_id", "text2speech_score"]
                ].copy(deep=True)
                html_content += self.plot_table(text2speech_df, "Text2Speech")

            overall_conversation_df = conversation_annotation_df[
                ["track_id", "user_id", "overall_comment", "overall_score"]
            ].copy(deep=True)
            html_content += self.plot_table(
                overall_conversation_df, "Overall Conversation Quality"
            )
        else:
            #
            # then we will try to calculate the overall accuracy for each annotation task
            conversation_annotation_df = self.annotation_average(
                df=conversation_annotation_df
            )
            if "speech2text" in required_annotation_task:
                desc_df = self.summary_df(
                    conversation_annotation_df[
                        ["track_id", "wer", "cer", "speech2text_score"]
                    ].copy(deep=True)
                )
                html_content += self.plot_table(desc_df, "Speech2Text Overall Quality")
                html_content += self.plot_distribution(
                    conversation_annotation_df[
                        ["track_id", "wer", "cer", "speech2text_score"]
                    ].copy(deep=True),
                    "Speech2Text",
                )
            if "text_generation" in required_annotation_task:
                desc_df = self.summary_df(
                    conversation_annotation_df[
                        ["track_id", "text_generation_score"]
                    ].copy(deep=True)
                )
                html_content += self.plot_table(
                    desc_df, "Text Generation Overall Quality"
                )
                html_content += self.plot_distribution(
                    conversation_annotation_df[
                        ["track_id", "text_generation_score"]
                    ].copy(deep=True),
                    "Text Generation",
                )

            if "text2speech" in required_annotation_task:
                desc_df = self.summary_df(
                    conversation_annotation_df[["track_id", "text2speech_score"]].copy(
                        deep=True
                    )
                )
                html_content += self.plot_table(desc_df, "Text2Speech Overall Quality")
                html_content += self.plot_distribution(
                    conversation_annotation_df[["track_id", "text2speech_score"]].copy(
                        deep=True
                    ),
                    "Text2Speech",
                )

        # summary the emotion detection task
        if "emotion_detection" in required_annotation_task:
            # load the emotion detection results
            emotion_detection_results = ContextEmotionDetection.objects.filter(
                multi_modal_conversation__in=conversations
            ).order_by("-created_at")
            if len(emotion_detection_results) == 0:
                return html_content + "<h4>No emotion detection results found</h4>"

            emotion_detection_expected_keys = (
                MultiModalFKEmotionDetectionAnnotationForm.declared_fields.keys()
            )
            emotion_detection_pending_default = {
                key: "pending" for key in emotion_detection_expected_keys
            }
            emotion_detection_annotations = []
            for emotion_detection in emotion_detection_results:
                emotion_detection_annotation = emotion_detection.annotations
                annotated = False
                for user_id, annotation in emotion_detection_annotation.items():
                    emotion_detection_annotations.append(
                        {
                            "track_id": emotion_detection.multi_modal_conversation.track_id,
                            "user_id": user_id,
                            **emotion_detection_pending_default,
                            **annotation,
                        }
                    )
                    annotated = True
                if not annotated:
                    emotion_detection_annotations.append(
                        {
                            "track_id": emotion_detection.multi_modal_conversation.track_id,
                            "user_id": "missing",
                            **emotion_detection_pending_default,
                        }
                    )

            emotion_detection_df = pd.DataFrame(emotion_detection_annotations)
            emotion_detection_df["track_id"] = (
                emotion_detection_df["track_id"].str.split("-").str[-1]
            )
            emotion_detection_df.columns = [
                col.replace("annotation_", "") for col in emotion_detection_df.columns
            ]
            if detailed:
                html_content += self.plot_table(
                    emotion_detection_df, "Emotion Detection"
                )
                html_content += self.plot_distribution(
                    emotion_detection_df, "Emotion Detection"
                )
            else:
                emotion_detection_df = self.annotation_average(emotion_detection_df)
                desc_df = self.summary_df(emotion_detection_df)
                # logger.info(desc_df)
                html_content += self.plot_table(desc_df, "Emotion Detection")

        return html_content

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
                "text": f"Accuracy: {title}",
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

        mean_accuracies = df[df.columns[1:]].mean()
        max_accuracies = df[df.columns[1:]].max()
        min_accuracies = df[df.columns[1:]].min()

        # Create a Plotly figure
        fig = go.Figure()
        # Add min latencies to the figure
        fig.add_trace(
            go.Bar(x=min_accuracies.index, y=min_accuracies.values, name="Min Accuracy")
        )
        # Add mean latencies to the figure
        fig.add_trace(
            go.Bar(
                x=mean_accuracies.index, y=mean_accuracies.values, name="Mean Accuracy"
            )
        )

        # Add max latencies to the figure
        fig.add_trace(
            go.Bar(x=max_accuracies.index, y=max_accuracies.values, name="Max Accuracy")
        )

        # Customize the layout
        fig.update_layout(
            title={
                "text": "Accuracy Distribution" + title,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            xaxis_title="Evaluation Metrics",
            yaxis_title="Accuracies",
            barmode="group",
            margin=dict(l=10, r=10, b=0),
        )

        # Convert Plotly figure to HTML
        plot_html = fig.to_html(full_html=False)
        return plot_html

    @staticmethod
    def extract_required_annotation_models(cluster_name: str) -> List[str]:
        """
        Extract the required annotation models
        Args:
            cluster_name (str): The cluster name
        """
        cluster = CLUSTERS.get(cluster_name, None)
        if cluster is None:
            raise ValueError(f"Cluster {cluster_name} not found")

        # candidate included: speech2text, text_generation, text2speech, this normally is required
        # other include emotion_detection now
        required_annotation_task = []
        for item in cluster.values():
            if item["component_type"] == "task":
                task_name = item["task_name"]
                required_annotation_task.append(
                    Task.task_ml_task_mapping().get(task_name, None)
                )

        # filter out None
        required_annotation_task = list(filter(None, required_annotation_task))
        # remove the duplicate
        return list(set(required_annotation_task))

    @staticmethod
    def calculate_speech2text_accuracy(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the speech2text accuracy
        Args:
            df (pd.DataFrame): The dataframe

        Returns:
            float: The accuracy
        """
        # both predict_text and speech2text can be null
        # if the predict_text is null, then we will consider it as 0
        # if the speech2text is null, then we will consider it as 0
        df["speech2text"] = df["speech2text"].fillna("")
        df["predict_text"] = df["predict_text"].fillna("")
        # calculate the accuracy
        df["wer"] = df.apply(
            lambda x: (
                round(
                    jiwer.wer(
                        x["speech2text"],
                        x["predict_text"],
                    ),
                    2,
                )
                if len(x["speech2text"]) > 0
                else 0
            ),
            axis=1,
        )

        df["cer"] = df.apply(
            lambda x: (
                round(
                    jiwer.cer(
                        x["speech2text"],
                        x["predict_text"],
                    ),
                    2,
                )
                if len(x["speech2text"]) > 0
                else 0
            ),
            axis=1,
        )

        return df

    @staticmethod
    def annotation_average(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the average of the annotation
        Args:
            df (pd.DataFrame): The dataframe

        Returns:
            pd.DataFrame: The dataframe
        """
        # for each row, if the value is missing or pending, remove the row
        # then calculate the average for each track_id
        df = df.replace("missing", pd.NA)
        df = df.replace("pending", pd.NA)
        df = df.dropna(subset=df.columns[2:], how="any")
        # try to get all columns to float, if not possible, then keep it as it is
        # loop the columns, try to get it to float
        for col in df.columns[2:]:
            try:
                df[col] = df[col].astype(float)
            except ValueError:
                pass
        numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns
        df_mean = df.groupby("track_id")[numeric_columns].mean().reset_index()
        return df_mean

    @staticmethod
    def summary_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Summary the given dataframe

        Args:
            df (pd.DataFrame): The dataframe

        Returns:
            str: The HTML content
        """
        # for the same track_id, aggregate the results into one, and use the mean as the final result
        # df = df.apply(pd.to_numeric, errors='coerce')

        # Group by 'track_id' and calculate the mean for each group
        # df = df.groupby("track_id").mean().reset_index()
        desc_df = df.describe().transpose()
        desc_df = desc_df.reset_index()
        desc_df.rename(columns={"index": "metric"}, inplace=True)
        desc_df = desc_df.round(4)
        return desc_df

    def detail_run(self):
        logger.info(f"Running accuracy benchmark for cluster {self.benchmark_cluster}")
        # run the benchmark
        html_content = ""
        if self.benchmark_cluster == "all":
            for cluster_name in CLUSTERS.keys():
                html_content += "<hr>"
                html_content += self.process_cluster_benchmark(
                    cluster_name, detailed=True
                )
        else:
            html_content += self.process_cluster_benchmark(
                self.benchmark_cluster, detailed=True
            )
        return html_content
