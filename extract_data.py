import pandas as pd
import os
import json
from multiprocessing import Pool, cpu_count

def extract_file_name(path: str) -> list[str]:
    """Extrae nombres de archivos en un directorio dado (ignora subdirectorios)."""
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def open_file(path: str) -> dict:
    """Abre un archivo JSON y devuelve su contenido como diccionario."""
    with open(path, "r", encoding='utf-8') as file:
        return json.load(file)

def process_file(name_data: str, path: str, key_name: str) -> pd.DataFrame:
    """Procesa un archivo JSON y devuelve un DataFrame a partir de la clave especificada."""
    try:
        file_data = open_file(os.path.join(path, name_data))
        return pd.json_normalize(file_data[key_name])
    except Exception as e:
        print(f"Error processing file '{name_data}': {e}")
        return pd.DataFrame()


def concat_dict(key_name: str, path: str) -> pd.DataFrame:
    """Procesa en paralelo los archivos del directorio `path` y concatena los datos bajo `key_name`."""
    file_names = extract_file_name(path)
    with Pool(processes=cpu_count()) as pool:
        # Ejecutar procesamiento en paralelo
        results = [
            pool.apply_async(process_file, args=(fname, path, key_name))
            for fname in file_names
        ]
        list_df = [res.get() for res in results]

    # Filtrar DataFrames vacíos
    list_df = [df for df in list_df if not df.empty]

    # Concatenar resultados en un único DataFrame
    return pd.concat(list_df, ignore_index=True) if list_df else pd.DataFrame()
