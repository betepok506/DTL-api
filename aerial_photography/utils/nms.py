import torch
import torchvision.ops as ops


def apply_nms(results, iou_threshold=0.5):
    boxes = []
    scores = []
    for res in results:
        boxes.append(res.bbox)
        scores.append(res.score)

    boxes = torch.tensor(boxes)
    scores = torch.tensor(scores)
    keep = ops.nms(boxes, scores, iou_threshold)

    filtered_results = [results[i] for i in keep]
    return filtered_results
