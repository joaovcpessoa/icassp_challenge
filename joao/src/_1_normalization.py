import librosa
import numpy as np
import pandas as pd
import parselmouth
from parselmouth.praat import call
from scipy.stats import skew, kurtosis
from tsfresh.feature_extraction import feature_calculators

def extract_features(file_path, sr=8000):
    """
    Extrai uma variedade de features de um arquivo de áudio usando feature aggregation.
    As features são extraídas de frames curtos e depois agregadas (média, std, etc.)
    para criar um vetor de features de tamanho fixo.

    Args:
        file_path (str): Caminho para o arquivo de áudio.
        sr (int): Taxa de amostragem a ser usada. O padrão é 8000 Hz.

    Returns:
        dict: Um dicionário com os nomes das features como chaves e seus valores.
    """
    try:
        # Carregar o áudio com librosa
        y, sr = librosa.load(file_path, sr=sr)

        #--- Features do Librosa (baseadas em frames) ---
        features = {}

        # Funções de agregação
        agg_funcs = {
            'mean': np.mean,
            'std': np.std,
            'median': np.median,
            'min': np.min,
            'max': np.max,
            'skew': skew,
            'kurt': kurtosis
        }

        def aggregate_feature(feature_matrix, name):
            """Aplica funções de agregação a uma matriz de features."""
            for stat_name, func in agg_funcs.items():
                # Agrega ao longo do tempo (axis=1)
                aggregated_values = func(feature_matrix, axis=1)
                # Para features multidimensionais (como MFCC), salva cada coeficiente
                if aggregated_values.ndim > 0:
                    for i, val in enumerate(aggregated_values):
                        features[f"{name}_{i+1}_{stat_name}"] = val
                else:
                    features[f"{name}_{stat_name}"] = aggregated_values

        # 1. MFCC (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        aggregate_feature(mfccs, 'mfcc')

        # 2. Delta MFCC
        delta_mfccs = librosa.feature.delta(mfccs)
        aggregate_feature(delta_mfccs, 'delta_mfcc')

        # 3. Delta-Delta MFCC
        delta2_mfccs = librosa.feature.delta(mfccs, order=2)
        aggregate_feature(delta2_mfccs, 'delta2_mfcc')

        # 4. Chroma Features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        aggregate_feature(chroma, 'chroma')

        # 5. Mel Spectrogram
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
        aggregate_feature(librosa.power_to_db(mel_spec), 'mel_spec_db')

        # 6. Spectral Contrast
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        aggregate_feature(spectral_contrast, 'spectral_contrast')

        # 7. Tonal Centroid Features (Tonnetz)
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        aggregate_feature(tonnetz, 'tonnetz')
        
        # 8. Zero-Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y)
        aggregate_feature(zcr, 'zcr')

        # 9. RMS Energy
        rms = librosa.feature.rms(y=y)
        aggregate_feature(rms, 'rms')

        #--- Features do Parselmouth (fonética) ---
        sound = parselmouth.Sound(file_path)
        
        # 10. Frequência Fundamental (Pitch - F0)
        pitch = sound.to_pitch()
        pitch_values = pitch.selected_array['frequency']
        pitch_values = pitch_values[pitch_values > 0] # Filtra valores não vocalizados (zeros)
        
        if len(pitch_values) > 0:
            features['f0_mean'] = np.mean(pitch_values)
            features['f0_std'] = np.std(pitch_values)
            features['f0_min'] = np.min(pitch_values)
            features['f0_max'] = np.max(pitch_values)
        else: # Caso não detecte pitch
            features['f0_mean'] = 0
            features['f0_std'] = 0
            features['f0_min'] = 0
            features['f0_max'] = 0

        # 11. Jitter e Shimmer
        point_process = call(sound, "To PointProcess (periodic, cc)", pitch.tmin, pitch.tmax)
        features['jitter_local'] = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        features['shimmer_local'] = call(point_process, "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)

        # 12. Harmonics-to-Noise Ratio (HNR)
        harmonicity = sound.to_harmonicity()
        hnr_values = call(harmonicity, "Get mean", 0, 0)
        features['hnr_mean'] = hnr_values if not np.isnan(hnr_values) else 0

        #--- Features do tsfresh (características de séries temporais) ---
        # Aplicado ao áudio bruto para capturar características adicionais
        
        # 13. Autocorrelation
        features['autocorrelation_lag1'] = feature_calculators.autocorrelation(y, lag=1)
        
        # 14. Complexity
        features['cid_ce'] = feature_calculators.cid_ce(y, normalize=True)

        # 15. Flutuações
        features['friedrich_coefficient'] = feature_calculators.friedrich_coefficient(y, m=3, r=30)

        # 16. Entropia
        features['spectral_entropy'] = feature_calculators.spectral_entropy(y, sf=sr, method='fft')
        features['sample_entropy'] = feature_calculators.sample_entropy(y)

        return features

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")
        return None

# --- Exemplo de Uso ---
if __name__ == '__main__':
    # Crie um arquivo de áudio de exemplo para testar
    # (ou substitua pelo caminho de um arquivo .wav existente)
    example_sr = 8000
    duration = 5 # segundos
    frequency = 250 # Hz
    t = np.linspace(0., duration, int(example_sr * duration))
    amplitude = np.iinfo(np.int16).max * 0.5
    data = amplitude * np.sin(2. * np.pi * frequency * t)
    
    # Adicionando um pouco de ruído
    noise = np.random.normal(0, amplitude * 0.1, len(data))
    data += noise
    
    example_file = "example_audio.wav"
    import soundfile as sf
    sf.write(example_file, data, example_sr)

    # Extrair as features do arquivo de exemplo
    extracted_features = extract_features(example_file)

    if extracted_features:
        # Criar um DataFrame para melhor visualização
        df_features = pd.DataFrame([extracted_features])
        
        # Configurar pandas para mostrar todas as colunas
        pd.set_option('display.max_columns', None)
        
        print("Vetor de Features Extraídas (DataFrame):")
        print(df_features)
        
        print(f"\nTotal de features extraídas: {len(df_features.columns)}")