import os
import random
import xml.etree.ElementTree as ET
from typing import List, Tuple

import numpy as np
import torch.utils.data
from PIL import Image, ImageOps
from torch import Tensor

from bbox import BBox
from dataset.base import Base
from voc_eval import voc_eval


class jun_voc(Base):

    class Annotation(object):
        class Object(object):
            def __init__(self, name: str, difficult: bool, bbox: BBox):
                super().__init__()
                self.name = name
                self.difficult = difficult
                self.bbox = bbox

            def __repr__(self) -> str:
                return 'Object[name={:s}, difficult={!s}, bbox={!s}]'.format(
                    self.name, self.difficult, self.bbox)

        def __init__(self, filename: str, objects: List[Object]):
            super().__init__()
            self.filename = filename
            self.objects = objects

    CATEGORY_TO_LABEL_DICT = {
        'background': 0,
        'raccoon': 1, 'fennec_fox': 2, 'Long-tailed_tit': 3, 'Rhinoceros': 4, 'pangolin': 5, 'seal': 6, 'bat': 7, 'dolphine': 8,
        'tuna': 9, 'hawk': 10, 'parrot': 11, 'octopus': 12, 'reindeer': 13, 'alpaca': 14, 'Sunfish': 15, 'mosquito': 16, 'Goat': 17,
        'Tarsier': 18, 'margay': 19, 'cuscus_animal': 20,
    }

    LABEL_TO_CATEGORY_DICT = {v: k for k, v in CATEGORY_TO_LABEL_DICT.items()}

    def __init__(self, path_to_data_dir: str, mode: Base.Mode, image_min_side: float, image_max_side: float):
        super().__init__(path_to_data_dir, mode, image_min_side, image_max_side)

        path_to_jun_voc_dir = os.path.join(self._path_to_data_dir, 'VOCdevkit', 'jun_voc')
        path_to_imagesets_main_dir = os.path.join(path_to_jun_voc_dir, 'ImageSets', 'Main')
        path_to_annotations_dir = os.path.join(path_to_jun_voc_dir, 'Annotations')
        self._path_to_jpeg_images_dir = os.path.join(path_to_jun_voc_dir, 'JPEGImages')

        if self._mode == jun_voc.Mode.TRAIN:
            path_to_image_ids_txt = os.path.join(path_to_imagesets_main_dir, 'trainval.txt')
        elif self._mode == jun_voc.Mode.EVAL:
            path_to_image_ids_txt = os.path.join(path_to_imagesets_main_dir, 'test.txt')
        else:
            raise ValueError('invalid mode')

        with open(path_to_image_ids_txt, 'r') as f:
            lines = f.readlines()
            self._image_ids = [line.rstrip() for line in lines]

        self._image_id_to_annotation_dict = {}
        self._image_ratios = []
        for image_id in self._image_ids:
            path_to_annotation_xml = os.path.join(path_to_annotations_dir, f'{image_id}.xml')
            tree = ET.ElementTree(file=path_to_annotation_xml)
            root = tree.getroot()

            self._image_id_to_annotation_dict[image_id] = jun_voc.Annotation(
                filename=root.find('filename').text,
                objects=[jun_voc.Annotation.Object(
                    name=next(tag_object.iterfind('name')).text,
                    difficult=next(tag_object.iterfind('difficult')).text == '1',
                    bbox=BBox(  # convert to 0-based pixel index
                        left=float(next(tag_object.iterfind('bndbox/xmin')).text) - 1,
                        top=float(next(tag_object.iterfind('bndbox/ymin')).text) - 1,
                        right=float(next(tag_object.iterfind('bndbox/xmax')).text) - 1,
                        bottom=float(next(tag_object.iterfind('bndbox/ymax')).text) - 1
                    )
                ) for tag_object in root.iterfind('object')]
            )

            width = int(root.find('size/width').text)
            height = int(root.find('size/height').text)
            ratio = float(width / height)
            self._image_ratios.append(ratio)

    def __len__(self) -> int:
        return len(self._image_id_to_annotation_dict)

    def __getitem__(self, index: int) -> Tuple[str, Tensor, Tensor, Tensor, Tensor]:
        image_id = self._image_ids[index]
        annotation = self._image_id_to_annotation_dict[image_id]

        bboxes = [obj.bbox.tolist() for obj in annotation.objects if not obj.difficult]
        labels = [jun_voc.CATEGORY_TO_LABEL_DICT[obj.name] for obj in annotation.objects if not obj.difficult]

        bboxes = torch.tensor(bboxes, dtype=torch.float)
        labels = torch.tensor(labels, dtype=torch.long)

        image = Image.open(os.path.join(self._path_to_jpeg_images_dir, annotation.filename)).convert('RGB')

        # random flip on only training mode
        if self._mode == jun_voc.Mode.TRAIN and random.random() > 0.5:
            image = ImageOps.mirror(image)
            bboxes[:, [0, 2]] = image.width - bboxes[:, [2, 0]]  # index 0 and 2 represent `left` and `right` respectively

        image, scale = jun_voc.preprocess(image, self._image_min_side, self._image_max_side)
        scale = torch.tensor(scale, dtype=torch.float)
        bboxes *= scale

        return image_id, image, scale, bboxes, labels

    def evaluate(self, path_to_results_dir: str, image_ids: List[str], bboxes: List[List[float]], classes: List[int], probs: List[float]) -> Tuple[float, str]:
        self._write_results(path_to_results_dir, image_ids, bboxes, classes, probs)

        path_to_jun_voc_dir = os.path.join(self._path_to_data_dir, 'VOCdevkit', 'jun_voc')
        path_to_main_dir = os.path.join(path_to_jun_voc_dir, 'ImageSets', 'Main')
        path_to_annotations_dir = os.path.join(path_to_jun_voc_dir, 'Annotations')

        class_to_ap_dict = {}
        for c in range(1, jun_voc.num_classes()):
            category = jun_voc.LABEL_TO_CATEGORY_DICT[c]
            try:
                path_to_cache_dir = os.path.join('caches', 'jun_voc')
                os.makedirs(path_to_cache_dir, exist_ok=True)
                _, _, ap = voc_eval(detpath=os.path.join(path_to_results_dir, 'comp3_det_test_{:s}.txt'.format(category)),
                                    annopath=os.path.join(path_to_annotations_dir, '{:s}.xml'),
                                    imagesetfile=os.path.join(path_to_main_dir, 'test.txt'),
                                    classname=category,
                                    cachedir=path_to_cache_dir,
                                    ovthresh=0.5,
                                    use_07_metric=True)
            except IndexError:
                ap = 0

            class_to_ap_dict[c] = ap

        mean_ap = np.mean([v for k, v in class_to_ap_dict.items()]).item()

        detail = ''
        for c in range(1, jun_voc.num_classes()):
            detail += '{:d}: {:s} AP = {:.4f}\n'.format(c, jun_voc.LABEL_TO_CATEGORY_DICT[c], class_to_ap_dict[c])

        return mean_ap, detail

    def _write_results(self, path_to_results_dir: str, image_ids: List[str], bboxes: List[List[float]], classes: List[int], probs: List[float]):
        class_to_txt_files_dict = {}
        for c in range(1, jun_voc.num_classes()):
            class_to_txt_files_dict[c] = open(os.path.join(path_to_results_dir, 'comp3_det_test_{:s}.txt'.format(jun_voc.LABEL_TO_CATEGORY_DICT[c])), 'w')

        for image_id, bbox, cls, prob in zip(image_ids, bboxes, classes, probs):
            class_to_txt_files_dict[cls].write('{:s} {:f} {:f} {:f} {:f} {:f}\n'.format(image_id, prob,
                                                                                        bbox[0], bbox[1], bbox[2], bbox[3]))

        for _, f in class_to_txt_files_dict.items():
            f.close()

    @property
    def image_ratios(self) -> List[float]:
        return self._image_ratios

    @staticmethod
    def num_classes() -> int:
        return 21
