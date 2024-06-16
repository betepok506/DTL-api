import torch
from torchvision import transforms
from dtl_siamese_network import SiameseNet, ResNet
import numpy as np

def normalize(image):
    # max_value = 4096
    image = np.log1p(image.astype(np.float32))
    min_value = np.min(image)
    max_value = np.max(image)
    # линейное преобразование для нормирования пикселей
    image = ((image - min_value) / (max_value - min_value)) * 255

    return image.astype(np.uint8)


class ImageVectorizer:
    def __init__(self, path_to_weight, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = torch.device(device)
        self.embedding_net = ResNet()
        self.model = SiameseNet(self.embedding_net)
        self.model.load_state_dict(torch.load(path_to_weight, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def _get_transforms(self, mean=0.1307, std=0.3081):
        transform = transforms.Compose([
            transforms.Resize((256, 256)), # todo: Проверить преобразование
            transforms.ToTensor(),
            transforms.Normalize((mean,), (std,))
        ])
        return transform

    def vectorize(self, image):
        with torch.no_grad():
            feature_vector = self.model.predict(image, device=self.device)
        return feature_vector.cpu().numpy()

# Пример использования
# vectorizer = ImageVectorizer(path_to_weight='path/to/your/weights.pth')
# image_vector = vectorizer.vectorize(image)
