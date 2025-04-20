import os
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


def setup_reference_directories():
    try:
        base_dir = "assets/references"
        buildings = {
            "hala_stulecia": 1,
            "katedra": 2,
            "sky_tower": 3
        }

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            logger.info(f"Utworzono katalog bazowy: {base_dir}")

        for building_name in buildings:
            building_dir = f"{base_dir}/{building_name}"
            if not os.path.exists(building_dir):
                os.makedirs(building_dir)
                logger.info(f"Utworzono katalog dla zabytku: {building_dir}")

        assets_dir = "assets"
        if os.path.exists(assets_dir):
            file_mappings = {
                "Hala.jpeg": f"{base_dir}/hala_stulecia/main.jpeg",
                "Katedra.jpg": f"{base_dir}/katedra/main.jpg",
                "SkyTower.jpg": f"{base_dir}/sky_tower/main.jpg"
            }

            for src_filename, dest_path in file_mappings.items():
                src_path = f"{assets_dir}/{src_filename}"
                if os.path.exists(src_path) and not os.path.exists(dest_path):
                    # Upewnij się, że katalog docelowy istnieje
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    logger.info(f"Skopiowano zdjęcie {src_path} jako referencję: {dest_path}")
                elif not os.path.exists(src_path):
                    logger.warning(f"Źródłowy plik {src_path} nie istnieje")
                elif os.path.exists(dest_path):
                    logger.info(f"Docelowy plik {dest_path} już istnieje")

        # Weryfikacja - upewnij się, że każdy zabytek ma co najmniej jedno zdjęcie referencyjne
        for building_name in buildings:
            building_dir = f"{base_dir}/{building_name}"
            if os.path.exists(building_dir):
                image_files = [f for f in os.listdir(building_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if not image_files:
                    logger.warning(f"Katalog {building_dir} nie zawiera zdjęć referencyjnych!")
                else:
                    logger.info(f"Katalog {building_dir} zawiera {len(image_files)} zdjęć referencyjnych")

        logger.info("Struktura katalogów dla zdjęć referencyjnych została przygotowana")
        return True

    except Exception as e:
        logger.error(f"Błąd podczas tworzenia struktury katalogów: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    setup_reference_directories()