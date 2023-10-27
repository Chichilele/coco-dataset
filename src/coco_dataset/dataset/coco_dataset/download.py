import os
from tqdm import tqdm
from sclearn.dataset.coco_dataset import CocoDataset


class CocoDownloader:
    def __init__(self, dataset: CocoDataset, s3_resource) -> None:
        self.dataset = dataset
        self.s3 = s3_resource

    def download(self, output_folder: str) -> None:
        os.makedirs(output_folder, exist_ok=True)
        for image in tqdm(self.dataset.images):
            url_components = image.coco_url.split("/")
            bucket_name = url_components[0]
            object_key = "/".join(url_components[1:])
            local_path = os.path.join(output_folder, image.file_name)
            tqdm.write(f"Downloading {image.file_name}...")
            self.s3.Object(bucket_name, object_key).download_file(local_path)
