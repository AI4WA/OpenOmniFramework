import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
from uuid import uuid4

import imageio
from moviepy.editor import VideoFileClip

from api import API
from constants import DATA_DIR
from utils import get_logger

logger = get_logger(__name__)


class DataMock:
    """
    We will first extract the audio and video from the video file.
    And then treat it as current time + any time in the future.

    Then save them into the data folder as other did

    - audio
        - /audio/uuid/0-datetime.wav
    - video
        - /videos/uuid/datetime.mp4
        - /video/uuid/frames/date-time/xx.jpg
    """

    def __init__(
        self, api_domain: str, token: str, home_id: str = "", track_cluster: str = None
    ):
        self.api = API(
            domain=api_domain, token=token, home_id=home_id, track_cluster=track_cluster
        )
        self.uid = str(uuid4())

        self.audio_dir = DATA_DIR / "audio" / self.uid
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.video_dir = DATA_DIR / "videos" / self.uid
        self.frames_dir = self.video_dir / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.mock_dir = DATA_DIR / "mock" / "output"
        self.mock_dir.mkdir(parents=True, exist_ok=True)

        self.current_time = datetime.now()

    def replay(self, time_ranges: List[Tuple[int, int]], input_video_path: str):
        """
        Replays the audio and video from the specified time
        Args:
            time_ranges (List[int, int]): List of time ranges in seconds.
            input_video_path (str): Path to the input video file.

        Returns:

        """
        for index, time_range in enumerate(time_ranges):
            start_second, end_second = time_range
            start_time = self.current_time + timedelta(seconds=start_second)
            end_time = self.current_time + timedelta(seconds=end_second)

            self.extract_audio_and_video(
                input_video_path=input_video_path,
                start_second=start_second,
                end_second=end_second,
                start_time=start_time,
                end_time=end_time,
                output_audio_path=self.audio_dir
                / f"{index}-{end_time.strftime('%Y%m%d%H%M%S')}.wav",
            )

            track_id = self.api.queue_speech_to_text(
                uid=self.uid,
                audio_index=str(index),
                start_time=start_time,
                end_time=end_time,
            )
            self.api.post_audio(
                uid=self.uid,
                sequence_index=index,
                audio_file=f"{index}-{end_time.strftime('%Y%m%d%H%M%S')}.wav",
                start_time=start_time,
                end_time=end_time,
                track_id=track_id,
            )

    def extract_audio_and_video(
        self,
        input_video_path: str,
        start_second: int,
        end_second: int,
        start_time: datetime,
        end_time: datetime,
        output_audio_path: str,
    ):
        """
        Extracts the audio and video from a specified segment of a video file.

        Args:
            input_video_path (str): Path to the input video file.
            start_second (int): Start time in seconds.
            end_second (int): End time in seconds.
            output_audio_path (str): Path to save the extracted audio file.
        """
        output_video_path = (
            self.mock_dir
            / f"{input_video_path.split('/')[-1]}-{start_second}-{end_second}.mp4"
        ).as_posix()
        # Load the video file
        video_clip = VideoFileClip(input_video_path)

        # Cut the video clip from start_time to end_time
        sub_clip = video_clip.subclip(start_second, end_second)

        # Write the video clip to the output path
        sub_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

        # Extract the audio from the sub clip
        audio_clip = sub_clip.audio

        # Write the audio clip to the output path
        audio_clip.write_audiofile(output_audio_path)

        # Close the clips
        # video_clip.close()
        sub_clip.close()
        audio_clip.close()
        video_clip.close()
        # then I want ot split the video by minutes, each minute will have 1 mp4 file
        # and the frames
        start_minute = start_time.replace(second=0, microsecond=0)
        end_minute = end_time.replace(second=0, microsecond=0) + timedelta(minutes=1)

        for i in range((end_minute - start_minute).seconds // 60):
            logger.info(f"Processing minute {i}")
            video_clip = VideoFileClip(input_video_path)
            the_minute_start_time = start_minute + timedelta(minutes=i)
            the_minute_end_time = start_minute + timedelta(minutes=i + 1)
            the_minute_output_video_path = (
                Path(self.video_dir)
                / (the_minute_start_time.strftime("%Y-%m-%d_%H-%M-%S") + ".mp4")
            ).as_posix()
            # recover the seconds range for each minute
            the_minute_start_second = (
                the_minute_start_time - self.current_time
            ).seconds
            the_minute_end_second = (the_minute_end_time - self.current_time).seconds
            logger.info(f"{the_minute_start_second}-{the_minute_end_second}")
            minute_clip = video_clip.subclip(
                the_minute_start_second, the_minute_end_second
            )
            minute_clip.write_videofile(
                the_minute_output_video_path, codec="libx264", audio_codec="aac"
            )
            minute_clip.close()

            # frames_folder
            frames_folder = self.frames_dir / the_minute_start_time.strftime(
                "%Y-%m-%d_%H-%M"
            )
            frames_folder.mkdir(parents=True, exist_ok=True)
            self.split_video_in_minutes(
                the_minute_output_video_path, frames_folder.as_posix()
            )
            self.api.post_video(
                self.uid,
                the_minute_output_video_path.split("/")[-1],
                start_time=the_minute_start_time,
                end_time=the_minute_end_time,
            )

            video_clip.close()

    @staticmethod
    def split_video_in_minutes(video_path, output_folder, fps=1):
        """
        Splits a video into images.

        Args:
            video_path (str): Path to the video file.
            output_folder (str): Folder to save the extracted images.
            fps (int): Frames per second to extract. Defaults to 1.
        """
        # Load the video file
        the_video_clip = VideoFileClip(video_path)

        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Extract frames
        for i, frame in enumerate(the_video_clip.iter_frames(fps=fps)):
            # Save each frame as an image
            frame_path = os.path.join(output_folder, f"{i}.png")
            imageio.imwrite(frame_path, frame)

        # Close the video clip
        the_video_clip.close()


# Example usage
if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--api_domain", type=str, required=True)
    args.add_argument("--token", type=str, required=True)
    args.add_argument("--home_id", type=str, default=None)
    args.add_argument("--track_cluster", type=str, default="")

    args.add_argument("--input_video_path", type=str, required=True)
    args.add_argument(
        "--time_points",
        type=str,
        required=True,
        help="start,end,start,end, it will be in format of 03:20,03:30,03:40,03:50",
    )

    args = args.parse_args()

    timepoints = args.time_points.split(",")

    if len(timepoints) % 2 != 0:
        raise ValueError("Time points must be in pairs")

    time_ranges = []
    for i in range(0, len(timepoints), 2):
        start_minute, start_second = timepoints[i].split(":")
        end_minute, end_second = timepoints[i + 1].split(":")
        time_ranges.append(
            (
                int(start_minute) * 60 + int(start_second),
                int(end_minute) * 60 + int(end_second),
            )
        )

    mock = DataMock(
        api_domain=args.api_domain,
        token=args.token,
        home_id=args.home_id,
        track_cluster=args.track_cluster,
    )

    mock.replay(
        time_ranges=time_ranges,
        input_video_path=args.input_video_path,
    )
