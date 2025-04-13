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
                    shutil.copy2(src_path, dest_path)
                    logger.info(f"Skopiowano zdjęcie {src_path} jako referencję: {dest_path}")

        logger.info("Struktura katalogów dla zdjęć referencyjnych została przygotowana")

    except Exception as e:
        logger.error(f"Błąd podczas tworzenia struktury katalogów: {e}")
        raise


if __name__ == "__main__":
    setup_reference_directories()