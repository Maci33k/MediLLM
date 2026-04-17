import os
import pandas as pd

folder_path = os.path.join("..", "results", "eksperyment1")

file1 = os.path.join(folder_path, "baseline.csv")
file2 = os.path.join(folder_path, "chain_and_fewshot.csv")
file3 = os.path.join(folder_path, "role-playing.csv")

print("Wczytywanie plików...")
try:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    df3 = pd.read_csv(file3)
except FileNotFoundError as e:
    print(f"❌ Błąd: Nie znaleziono pliku. Upewnij się, że uruchamiasz skrypt z odpowiedniego miejsca. Szczegóły: {e}")
    exit()

df_final = pd.concat([df1, df2, df3], ignore_index=True)
output_path = os.path.join(folder_path, "merged_results.csv")
df_final.to_csv(output_path, index=False)

print(f"✅ Sukces! Połączono pliki. Nowy plik zapisano jako:")
print(f"📁 {output_path}")
print(f"📊 Łączna liczba wierszy: {len(df_final)}")