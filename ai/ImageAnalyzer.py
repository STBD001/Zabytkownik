import os
import logging
import time
import numpy as np
from PIL import Image
import cv2
import torch
from torchvision.models import efficientnet_b0
import torchvision.transforms as transforms
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import albumentations as A
from database.repositories.user_building_repository import UserBuildingRepository

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ImageAnalyzer:
    def __init__(self,
                 model_name='efficientnet_b0',
                 similarity_threshold=0.7,
                 reference_dir='assets/references'):
        self.logger = logging.getLogger('ImageAnalyzer')
        self.similarity_threshold = similarity_threshold
        self.reference_dir = reference_dir
        self.reference_embeddings = {}
        self.all_embeddings = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.logger.info(f"Inicjalizacja modelu {model_name} na urządzeniu {self.device}")
        try:
            # Inicjalizacja modelu EfficientNet
            self.model = efficientnet_b0(pretrained=True).eval().to(self.device)
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

            # Augmentacja dla referencji
            self.augment = A.Compose([
                A.RandomBrightnessContrast(p=0.5),
                A.Rotate(limit=30, p=0.5),
                A.GaussianBlur(p=0.3),
                A.RandomCrop(height=200, width=200, p=0.3),
            ])

            # Upewnij się, że katalogi istnieją
            from setup_reference_dirs import setup_reference_directories
            setup_reference_directories()

            self._preload_references()
            self.logger.info("Model zainicjalizowany pomyślnie")
        except Exception as e:
            self.logger.error(f"Błąd podczas inicjalizacji modelu: {e}")
            raise

    def _preload_references(self):
        self.logger.info(f"Ładowanie referencyjnych obrazów z {self.reference_dir}")
        cache_file = "reference_embeddings.pkl"

        # Sprawdź cache
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    self.reference_embeddings = pickle.load(f)
                    self.all_embeddings = self.reference_embeddings.copy()
                self.logger.info("Załadowano embeddingi z cache")
                return
            except Exception as e:
                self.logger.warning(f"Błąd ładowania cache: {e}. Obliczanie embeddingów od nowa.")

        # Próba pobrania zabytków z bazy danych
        try:
            monuments = UserBuildingRepository.get_all_monuments()
        except AttributeError:
            self.logger.warning("Metoda get_all_monuments nie istnieje w UserBuildingRepository. Używam domyślnej listy zabytków.")
            # Fallback: Hardcoded lista zabytków
            monuments = [
                {'building_id': 1, 'directory_name': 'hala_stulecia', 'main_image_path': 'assets/Hala.jpeg'},
                {'building_id': 2, 'directory_name': 'katedra', 'main_image_path': 'assets/Katedra.jpg'},
                {'building_id': 3, 'directory_name': 'sky_tower', 'main_image_path': 'assets/SkyTower.jpg'}
            ]

        for monument in monuments:
            building_id = monument['building_id']
            directory = os.path.join(self.reference_dir, monument['directory_name'])
            if os.path.exists(directory):
                self.reference_embeddings[building_id] = []
                self.all_embeddings[building_id] = []

                for filename in os.listdir(directory):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                        try:
                            img_path = os.path.join(directory, filename)
                            if not self._is_image_blurry(img_path):
                                embedding = self._get_embedding(img_path)
                                self.reference_embeddings[building_id].append(embedding)
                                self.all_embeddings[building_id].append(embedding)
                                self.logger.info(f"Załadowano referencję: {img_path}")

                                # Augmentacja: generuj dodatkowe wersje obrazu
                                img = cv2.imread(img_path)
                                for _ in range(2):  # Generuj 2 augmentowane wersje
                                    augmented = self.augment(image=img)['image']
                                    temp_path = f"temp_aug_{time.time()}.jpg"
                                    cv2.imwrite(temp_path, augmented)
                                    embedding = self._get_embedding(temp_path)
                                    self.reference_embeddings[building_id].append(embedding)
                                    self.all_embeddings[building_id].append(embedding)
                                    os.remove(temp_path)
                            else:
                                self.logger.warning(f"Pomijanie rozmytego obrazu: {img_path}")
                        except Exception as e:
                            self.logger.error(f"Błąd podczas ładowania referencji {img_path}: {e}")

                self.logger.info(f"Załadowano {len(self.reference_embeddings[building_id])} "
                                 f"referencji dla zabytku ID {building_id}")
            else:
                self.logger.warning(f"Katalog dla zabytku ID {building_id} nie istnieje: {directory}")
                os.makedirs(directory, exist_ok=True)

                # Fallback: kopiowanie głównego zdjęcia
                main_image = monument.get('main_image_path')
                if main_image and os.path.exists(main_image):
                    import shutil
                    dest_path = os.path.join(directory, "main.jpg")
                    shutil.copy2(main_image, dest_path)
                    embedding = self._get_embedding(dest_path)
                    self.reference_embeddings[building_id] = [embedding]
                    self.all_embeddings[building_id] = [embedding]
                    self.logger.info(f"Skopiowano główne zdjęcie dla ID {building_id}")

        # Zapisz embeddingi do cache
        with open(cache_file, 'wb') as f:
            pickle.dump(self.reference_embeddings, f)

    def _is_image_blurry(self, image_path, threshold=100):
        """Sprawdza, czy obraz jest rozmyty na podstawie wariancji Laplasa."""
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
            return laplacian_var < threshold
        except:
            return True  # Jeśli nie można wczytać, traktuj jako rozmyty

    def _get_embedding(self, image_path):
        """Generuje embedding obrazu za pomocą EfficientNet."""
        try:
            img = Image.open(image_path).convert('RGB')
            img = self.transform(img).unsqueeze(0).to(self.device)
            with torch.no_grad():
                embedding = self.model(img).cpu().numpy().flatten()
            embedding = embedding / (np.linalg.norm(embedding) + 1e-10)
            return embedding
        except Exception as e:
            self.logger.error(f"Błąd generowania embeddingu dla {image_path}: {e}")
            # Fallback: podstawowe cechy histogramu
            img = cv2.imread(image_path)
            if img is None:
                img = cv2.cvtColor(np.array(Image.open(image_path).convert('RGB')), cv2.COLOR_RGB2BGR)
            return self._get_basic_features(img)

    def _get_basic_features(self, img):
        """Zapasowa metoda generowania cech histogramu."""
        try:
            img = cv2.resize(img, (64, 64))
            hist_features = []
            for i in range(3):
                hist = cv2.calcHist([img], [i], None, [16], [0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                hist_features.extend(hist)
            features = np.array(hist_features, dtype=np.float32)
            norm = np.linalg.norm(features)
            return features / norm if norm > 0 else np.random.rand(48)
        except Exception as e:
            self.logger.error(f"Błąd generowania podstawowych cech: {e}")
            return np.random.rand(48)

    def verify_monument(self, image_path, monument_id):
        try:
            start_time = time.time()
            self.logger.info(f"Weryfikacja zdjęcia: {image_path} dla ID: {monument_id}")

            if monument_id not in self.reference_embeddings or not self.reference_embeddings[monument_id]:
                self._preload_references()
                if monument_id not in self.reference_embeddings or not self.reference_embeddings[monument_id]:
                    return {
                        'success': False,
                        'confidence': 0,
                        'message': "Brak referencji dla tego zabytku."
                    }

            user_embedding = self._get_embedding(image_path)

            # Podobieństwo do docelowego zabytku
            target_similarities = [
                cosine_similarity([user_embedding], [ref])[0][0]
                for ref in self.reference_embeddings[monument_id]
            ]
            target_max_similarity = max(target_similarities)
            target_avg_similarity = np.mean(target_similarities)

            # Weryfikacja krzyżowa
            other_max_similarities = []
            for other_id in self.all_embeddings:
                if other_id == monument_id:
                    continue
                if other_id in self.reference_embeddings and self.reference_embeddings[other_id]:
                    other_similarities = [
                        cosine_similarity([user_embedding], [ref])[0][0]
                        for ref in self.reference_embeddings[other_id]
                    ]
                    other_max_similarities.append(max(other_similarities))

            cross_check_passed = True
            cross_validation_message = ""
            if other_max_similarities:
                highest_other_similarity = max(other_max_similarities)
                if highest_other_similarity > target_max_similarity:
                    cross_check_passed = False
                    cross_validation_message = f"Zdjęcie bardziej przypomina inny zabytek (pewność: {highest_other_similarity:.2f})."
                elif highest_other_similarity > target_max_similarity - 0.1:
                    cross_validation_message = "Zdjęcie wykazuje podobieństwo do innych zabytków."

            # Dynamiczny próg
            dynamic_threshold = self.similarity_threshold
            if len(self.reference_embeddings[monument_id]) > 5:
                dynamic_threshold = min(0.85, self.similarity_threshold + 0.1)

            final_similarity = target_max_similarity
            if not cross_check_passed:
                final_similarity *= 0.7

            if final_similarity >= dynamic_threshold and cross_check_passed:
                message = "Gratulacje! Zdjęcie przedstawia ten zabytek."
                if cross_validation_message:
                    message += f" {cross_validation_message}"
                result = {
                    'success': True,
                    'confidence': float(final_similarity),
                    'message': message
                }
            else:
                message = cross_validation_message or "Zdjęcie nie przedstawia tego zabytku. Spróbuj zrobić wyraźniejsze zdjęcie."
                if self._is_image_blurry(image_path):
                    message += " Zdjęcie może być zbyt rozmyte."
                result = {
                    'success': False,
                    'confidence': float(final_similarity),
                    'message': message
                }

            # Logowanie wyniku
            self._log_verification_result(image_path, monument_id, result)

            self.logger.info(f"Weryfikacja zakończona w {time.time() - start_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Błąd weryfikacji: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'confidence': 0,
                'message': f"Błąd analizy: {str(e)}"
            }

    def _log_verification_result(self, image_path, monument_id, result):
        """Loguje wyniki weryfikacji do pliku CSV."""
        with open('verification_log.csv', 'a', newline='') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow([image_path, monument_id, result['success'], result['confidence'], result['message'], time.time()])