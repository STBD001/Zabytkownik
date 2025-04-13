import os
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ImageAnalyzer:
    def __init__(self,
                 model_name='resnet50',
                 similarity_threshold=0.7,
                 reference_dir='assets/references'):

        self.logger = logging.getLogger('ImageAnalyzer')
        self.similarity_threshold = similarity_threshold
        self.reference_dir = reference_dir
        self.reference_embeddings = {}

        self.logger.info(f"Inicjalizacja modelu {model_name}")
        try:
            if model_name == 'resnet18':
                self.model = models.resnet18(pretrained=True)
            elif model_name == 'resnet50':
                self.model = models.resnet50(pretrained=True)
            elif model_name == 'mobilenet_v2':
                self.model = models.mobilenet_v2(pretrained=True)
            elif model_name == 'efficientnet_b0':
                self.model = models.efficientnet_b0(pretrained=True)
            else:
                self.model = models.resnet50(pretrained=True)
                self.logger.warning(f"Nieznany model: {model_name}, używam domyślnego resnet50")

            self.model = torch.nn.Sequential(*(list(self.model.children())[:-1]))
            self.model.eval()

            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            self._preload_references()

        except Exception as e:
            self.logger.error(f"Błąd podczas inicjalizacji modelu: {e}")
            raise

    def _preload_references(self):
        self.logger.info(f"Ładowanie referencyjnych obrazów z {self.reference_dir}")

        building_dirs = {
            1: os.path.join(self.reference_dir, "hala_stulecia"),
            2: os.path.join(self.reference_dir, "katedra"),
            3: os.path.join(self.reference_dir, "sky_tower")
        }

        for building_id, directory in building_dirs.items():
            if os.path.exists(directory):
                self.reference_embeddings[building_id] = []

                for filename in os.listdir(directory):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                        try:
                            img_path = os.path.join(directory, filename)
                            embedding = self._get_embedding(img_path)
                            self.reference_embeddings[building_id].append(embedding)
                            self.logger.info(f"Załadowano referencję: {img_path}")
                        except Exception as e:
                            self.logger.error(f"Błąd podczas ładowania referencji {img_path}: {e}")

                self.logger.info(f"Załadowano {len(self.reference_embeddings[building_id])} "
                                 f"referencji dla zabytku ID {building_id}")
            else:
                self.logger.warning(f"Katalog referencyjny dla zabytku ID {building_id} nie istnieje: {directory}")

    def _get_embedding(self, image_path):

        try:
            img = Image.open(image_path).convert('RGB')
            img_t = self.transform(img).unsqueeze(0)  # batch size = 1

            with torch.no_grad():
                embedding = self.model(img_t)

            embedding_np = embedding.view(-1).numpy()
            norm = np.linalg.norm(embedding_np)
            if norm > 0:
                embedding_np = embedding_np / norm

            return embedding_np

        except Exception as e:
            self.logger.error(f"Błąd podczas generowania embeddingu dla {image_path}: {e}")
            raise

    def verify_monument(self, image_path, monument_id):
        try:
            start_time = time.time()
            self.logger.info(f"Rozpoczynam weryfikację zdjęcia: {image_path} dla zabytku ID: {monument_id}")

            if monument_id not in self.reference_embeddings or not self.reference_embeddings[monument_id]:
                self.logger.warning(f"Brak zdjęć referencyjnych dla zabytku ID: {monument_id}")
                return {
                    'success': False,
                    'confidence': 0,
                    'message': "Nie znaleziono referencji dla tego zabytku. Spróbuj ponownie później."
                }

            user_embedding = self._get_embedding(image_path)

            similarities = []
            for ref_embedding in self.reference_embeddings[monument_id]:
                similarity = cosine_similarity([user_embedding], [ref_embedding])[0][0]
                similarities.append(similarity)

            max_similarity = max(similarities)

            self.logger.info(f"Najlepsze podobieństwo dla zabytku ID {monument_id}: {max_similarity:.4f}")

            if max_similarity >= self.similarity_threshold:
                result = {
                    'success': True,
                    'confidence': float(max_similarity),
                    'message': "Gratulacje! Zdjęcie przedstawia ten zabytek."
                }
            else:
                result = {
                    'success': False,
                    'confidence': float(max_similarity),
                    'message': "Zdjęcie prawdopodobnie nie przedstawia tego zabytku. Spróbuj jeszcze raz."
                }

            end_time = time.time()
            self.logger.info(f"Weryfikacja zakończona w {end_time - start_time:.2f}s z wynikiem: {result['success']}")

            return result

        except Exception as e:
            self.logger.error(f"Błąd podczas weryfikacji zdjęcia: {e}")
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'confidence': 0,
                'message': f"Wystąpił błąd podczas analizy zdjęcia: {str(e)}"
            }

    def preprocess_image(self, image_path):

        img = Image.open(image_path).convert('RGB')
        return self.transform(img)