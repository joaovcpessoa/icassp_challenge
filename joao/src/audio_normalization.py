
import os
import librosa
import numpy as np
import soundfile as sf
import pandas as pd

# Diretórios raiz dos arquivos de áudio e resultados da análise
output_dir = "./audio_analysis_results"
normalized_audio_dir = "./normalized_audio"
os.makedirs(normalized_audio_dir, exist_ok=True)

def load_audio_characteristics(filepath):
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame()

df_train_audio = load_audio_characteristics(os.path.join(output_dir, "train_audio_characteristics.csv"))
df_test_audio = load_audio_characteristics(os.path.join(output_dir, "test_audio_characteristics.csv"))

# Definir uma duração alvo para normalização (ex: mediana ou média da duração)
# Para este exemplo, vamos usar uma duração fixa de 5 segundos para ilustrar.
# Em um cenário real, isso seria determinado por análise exploratória ou requisitos do modelo.
TARGET_DURATION = 5.0 # segundos

def normalize_audio(filepath, target_duration, target_rms=0.01):
    try:
        y, sr = librosa.load(filepath, sr=None)

        # 1. Normalização de Duração
        # Se a duração for maior que a alvo, trunca.
        # Se for menor, preenche com silêncio.
        current_duration = librosa.get_duration(y=y, sr=sr)
        if current_duration > target_duration:
            # Truncamento
            y_normalized_duration = y[:int(target_duration * sr)]
        else:
            # Preenchimento com silêncio
            padding_length = int(target_duration * sr) - len(y)
            y_normalized_duration = np.pad(y, (0, padding_length), mode='constant')
        
        # 2. Normalização de Energia (RMS)
        # Calcula o RMS atual e ajusta para o RMS alvo
        current_rms = np.sqrt(np.mean(y_normalized_duration**2))
        if current_rms > 0:
            y_normalized_energy = y_normalized_duration * (target_rms / current_rms)
        else:
            y_normalized_energy = y_normalized_duration # Evita divisão por zero

        return y_normalized_energy, sr
    except Exception as e:
        print(f"Erro ao normalizar {filepath}: {e}")
        return None, None

# Processar e salvar áudios normalizados para o conjunto de treinamento
print("Iniciando normalização dos arquivos de áudio de treinamento...")
normalized_train_audio_paths = []
if not df_train_audio.empty:
    for index, row in df_train_audio.iterrows():
        original_filepath = row["filepath"]
        task_type = row["task_type"]
        filename = row["filename"]
        
        # Criar subdiretório para o task_type se não existir
        task_type_dir = os.path.join(normalized_audio_dir, "train", task_type)
        os.makedirs(task_type_dir, exist_ok=True)
        
        output_filepath = os.path.join(task_type_dir, filename)
        
        normalized_y, sr = normalize_audio(original_filepath, TARGET_DURATION)
        if normalized_y is not None:
            sf.write(output_filepath, normalized_y, sr)
            normalized_train_audio_paths.append(output_filepath)
print(f"Normalização de {len(normalized_train_audio_paths)} arquivos de treinamento concluída.")

# Processar e salvar áudios normalizados para o conjunto de teste
print("Iniciando normalização dos arquivos de áudio de teste...")
normalized_test_audio_paths = []
if not df_test_audio.empty:
    for index, row in df_test_audio.iterrows():
        original_filepath = row["filepath"]
        task_type = row["task_type"]
        filename = row["filename"]
        
        # Criar subdiretório para o task_type se não existir
        task_type_dir = os.path.join(normalized_audio_dir, "test", task_type)
        os.makedirs(task_type_dir, exist_ok=True)
        
        output_filepath = os.path.join(task_type_dir, filename)
        
        normalized_y, sr = normalize_audio(original_filepath, TARGET_DURATION)
        if normalized_y is not None:
            sf.write(output_filepath, normalized_y, sr)
            normalized_test_audio_paths.append(output_filepath)
print(f"Normalização de {len(normalized_test_audio_paths)} arquivos de teste concluída.")

print(f"Arquivos de áudio normalizados salvos em: {normalized_audio_dir}")
