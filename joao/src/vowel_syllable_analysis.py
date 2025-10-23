
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Diretórios de áudio normalizados e resultados da análise
normalized_audio_dir = "./normalized_audio"
output_dir = "./audio_analysis_results"
os.makedirs(output_dir, exist_ok=True)

def analyze_vowel_syllable_features(root_dir):
    feature_data = []
    print(f"Iniciando análise de vogais e sílabas em: {root_dir}")
    for dataset_type in ["train", "test"]:
        dataset_path = os.path.join(root_dir, dataset_type)
        if not os.path.exists(dataset_path): continue

        for task_type_dir in os.listdir(dataset_path):
            task_type_path = os.path.join(dataset_path, task_type_dir)
            if not os.path.isdir(task_type_path): continue

            task_type = os.path.basename(task_type_path)
            print(f"Processando {dataset_type} - task_type: {task_type}")

            # Classificar como vogal ou sílaba com base no nome da tarefa
            category = "Vogal" if "phonation" in task_type.lower() else "Sílaba"

            for filename in os.listdir(task_type_path):
                if filename.endswith(".wav"):
                    filepath = os.path.join(task_type_path, filename)
                    try:
                        y, sr = librosa.load(filepath, sr=None)

                        # Características mais simples e rápidas de calcular
                        duration = librosa.get_duration(y=y, sr=sr)
                        energy = np.sum(y**2) / len(y) # Energia média
                        rms = librosa.feature.rms(y=y).mean() # RMS médio

                        # Zero Crossing Rate (ZCR) - útil para diferenciar sons vozeados/não vozeados e ruído
                        zcr = librosa.feature.zero_crossing_rate(y).mean()

                        # Spectral Centroid - centro de massa do espectro, relacionado ao brilho do som
                        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean()

                        row_data = {
                            "filename": filename,
                            "task_type": task_type,
                            "category": category,
                            "duration": duration,
                            "energy": energy,
                            "rms": rms,
                            "zcr": zcr,
                            "spectral_centroid": spectral_centroid,
                        }
                        feature_data.append(row_data)

                    except Exception as e:
                        print(f"Erro ao processar {filepath}: {e}")
    return pd.DataFrame(feature_data)

df_vowel_syllable_features = analyze_vowel_syllable_features(normalized_audio_dir)

if not df_vowel_syllable_features.empty:
    df_vowel_syllable_features.to_csv(os.path.join(output_dir, "vowel_syllable_features_simplified.csv"), index=False)
    print("\n### Resumo das Características de Vogais e Sílabas (Simplificado)\n")
    print(df_vowel_syllable_features.groupby("category").describe())

    # Visualizações para comparar vogais e sílabas
    # Duração
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="category", y="duration", data=df_vowel_syllable_features)
    plt.title("Duração dos Áudios por Categoria (Vogal vs. Sílaba)")
    plt.xlabel("Categoria")
    plt.ylabel("Duração (segundos)")
    plt.savefig(os.path.join(output_dir, "duration_by_category_simplified.png"))
    plt.close()

    # Energia
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="category", y="energy", data=df_vowel_syllable_features)
    plt.title("Energia Média dos Áudios por Categoria (Vogal vs. Sílaba)")
    plt.xlabel("Categoria")
    plt.ylabel("Energia Média")
    plt.savefig(os.path.join(output_dir, "energy_by_category_simplified.png"))
    plt.close()

    # RMS
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="category", y="rms", data=df_vowel_syllable_features)
    plt.title("RMS dos Áudios por Categoria (Vogal vs. Sílaba)")
    plt.xlabel("Categoria")
    plt.ylabel("RMS")
    plt.savefig(os.path.join(output_dir, "rms_by_category_simplified.png"))
    plt.close()

    # Zero Crossing Rate
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="category", y="zcr", data=df_vowel_syllable_features)
    plt.title("Zero Crossing Rate por Categoria (Vogal vs. Sílaba)")
    plt.xlabel("Categoria")
    plt.ylabel("ZCR")
    plt.savefig(os.path.join(output_dir, "zcr_by_category_simplified.png"))
    plt.close()

    # Spectral Centroid
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="category", y="spectral_centroid", data=df_vowel_syllable_features)
    plt.title("Centroide Espectral por Categoria (Vogal vs. Sílaba)")
    plt.xlabel("Categoria")
    plt.ylabel("Centroide Espectral")
    plt.savefig(os.path.join(output_dir, "spectral_centroid_by_category_simplified.png"))
    plt.close()

    print("Análise de vogais e sílabas e visualizações concluídas e salvas em: ", output_dir)
else:
    print("DataFrame de características de vogais e sílabas está vazio. Nenhuma análise ou visualização gerada.")

