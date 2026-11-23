
from book_recommender.loader import load_data

def main():
    # Cargar los cinco archivos
    datos = load_data()

    # Mostrar información de cada DataFrame
    for nombre, df in datos.items():
        print(f"\nDataset: {nombre}")
        print(f"Filas: {df.shape[0]}")
        print(f"Columnas: {df.shape[1]}")
        print(f"Nombres de columnas: {list(df.columns)}")


if __name__ == "__main__":
    main()