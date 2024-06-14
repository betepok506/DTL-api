import torch
from dtl_siamese_network import SiameseNet, ResNet

class ImageVectorizer:
    def __init__(self, path_to_weight, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = torch.device(device)
        self.embedding_net = ResNet()
        self.model = SiameseNet(self.embedding_net)
        self.model.load_state_dict(torch.load(path_to_weight, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def vectorize(self, image):
        with torch.no_grad():
            image = image.to(self.device)
            feature_vector = self.model(image)
        return feature_vector.cpu().numpy()

# Пример использования
# vectorizer = ImageVectorizer(path_to_weight='path/to/your/weights.pth')
# image_vector = vectorizer.vectorize(image)
