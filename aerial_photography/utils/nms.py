import torch
import torchvision.ops as ops
from shapely import wkt


def apply_nms(bounding_boxes, scores, iou_threshold=0.5):
    boxes = torch.tensor(bounding_boxes)
    scores = torch.tensor(scores)
    keep = ops.nms(boxes, scores, iou_threshold)
    selected_scores = scores[keep]
    max_score_index = torch.argmax(selected_scores)

    # filtered_results = [bounding_boxes[i] for i in keep]
    return bounding_boxes[max_score_index]
