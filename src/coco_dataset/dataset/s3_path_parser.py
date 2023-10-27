from typing import List, Dict

import boto3


class ImageS3PathParser:
    def __init__(
        self,
        frames: Dict[str, int],
        bucket_name: str,
        bucket_region: str,
    ) -> None:
        self.frames = frames
        self.bucket_name = bucket_name
        self.bucket_region = bucket_region
        self._s3 = boto3.Session(region_name=bucket_region).resource("s3")
        self._bucket = self._s3.Bucket(bucket_name)

    def get_image_url(
        self,
        capture_folder_id: str,
    ) -> List[str]:
        """Get image path."""
        s3_keys = []
        for camera, frame_index in self.frames.items():
            s3_prefix = f"{capture_folder_id}/{camera}/"

            frame_keys = self._list_files_in_bucket(s3_prefix)

            frame_keys.sort()
            frame_keys = self.filter_thumbnails(frame_keys)

            if not frame_keys:
                raise S3PathEmptyError(s3_prefix)

            if len(frame_keys) <= frame_index:
                raise S3MissingFrameError(
                    camera_folder=s3_prefix,
                    frame_id=frame_index,
                    nb_frames=len(frame_keys),
                )

            key = frame_keys[frame_index]
            s3_key = f"{self.bucket_name}/{key}"

            s3_keys.append(s3_key)

        return s3_keys

    def _list_files_in_bucket(self, s3_prefix: str) -> List[str]:
        iterator = self._bucket.objects.filter(Prefix=s3_prefix)

        return [i.key for i in iterator]

    def filter_thumbnails(self, files: List[str]) -> List[str]:
        """Filter thumbnails from files"""

        filtered_failnames = [f for f in files if "thumbnail" not in f]

        return filtered_failnames


class DatasetbuilderError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, msg: str = "DatasetbuilderError", *args, **kwargs):
        super(DatasetbuilderError, self).__init__(*args, **kwargs)
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class S3PathEmptyError(DatasetbuilderError):
    def __init__(self, s3_path: str, *args, **kwargs):
        super(S3PathEmptyError, self).__init__(*args, **kwargs)
        self.s3_path = s3_path
        msg = f"S3 path empty: '{s3_path}'"
        self.msg = msg


class S3MissingFrameError(DatasetbuilderError):
    def __init__(
        self,
        camera_folder: str,
        frame_id: int,
        nb_frames: int,
        *args,
        **kwargs,
    ):
        super(S3MissingFrameError, self).__init__(*args, **kwargs)
        self.camera_folder = camera_folder
        self.frame_id = frame_id
        self.nb_frames = nb_frames

        msg = f"Missing Frame: {frame_id} of {nb_frames} in folder '{camera_folder}'"
        self.msg = msg
