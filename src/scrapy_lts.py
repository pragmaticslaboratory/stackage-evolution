
import os
import argparse
import pandas as pd
import multiprocessing
import subprocess

# Argumentos
parser = argparse.ArgumentParser(description='Generate a CSV file with package catalog')
parser.add_argument(
    "--revised",
    help="Set the PATH to make and save the DataFrames with revised Cabals",
    action='store_true',
    default=False
)
args = parser.parse_args()
isRevisedVersion = args.revised

# Leer lts_list.csv usando ruta absoluta
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LTS_CSV_PATH = os.path.join(SCRIPT_DIR, "lts_list.csv")
data = pd.read_csv(LTS_CSV_PATH)

# Carpeta base del proyecto
FOLDERPATH = os.path.dirname(SCRIPT_DIR)

# Lista de LTS
lts_list = data.columns


# Carpeta scrapy absoluta (ajustar para estructura real)
SCRAPY_DIR = os.path.join(SCRIPT_DIR, "scrapy")
if not os.path.isdir(SCRAPY_DIR):
    # Si no existe, buscar en src/scrapy
    SCRAPY_DIR = os.path.join(FOLDERPATH, "src", "scrapy")
    if not os.path.isdir(SCRAPY_DIR):
        raise NotADirectoryError(f"No se encontró la carpeta scrapy en {SCRIPT_DIR} ni en {FOLDERPATH}/src/")

def run_scrapy(lts):
    # Calcula la ruta de destino
    if isRevisedVersion:
        path = os.path.join(FOLDERPATH, "lts_downloaded", "revised_cabal")
    else:
        path = os.path.join(FOLDERPATH, "lts_downloaded", "tar_package")
    lts_dots = lts.replace("-", ".")
    path = os.path.join(path, f"lts-{lts}")
    # Comando scrapy
    command = [
        "scrapy", "crawl", "stackage",
        "-a", f"LTS={lts_dots}",
        "-s", f"FILES_STORE={path}",
        "-s", f"REVISED={isRevisedVersion}"
    ]
    # Ejecuta el comando en la carpeta scrapy
    subprocess.run(command, cwd=SCRAPY_DIR)

if __name__ == "__main__":
    # Usa multiprocessing para lanzar varios procesos en paralelo
    with multiprocessing.Pool(processes=min(8, len(lts_list))) as pool:
        pool.map(run_scrapy, lts_list)
