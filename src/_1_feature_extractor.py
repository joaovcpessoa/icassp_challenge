
import os
import librosa
import numpy as np
import pandas as pd

def extract_features(file_path, sr=8000, n_mfcc=13):
    try:
        y, sr = librosa.load(file_path, sr=sr)
        mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc).T, axis=0)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y=y))
        chroma_stft = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
        
        features = np.hstack([mfccs, spectral_centroid, spectral_rolloff, zero_crossing_rate, chroma_stft])
        return features
    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")
        return None

def process_audio_data(dataframe, audio_root_path, data_type):
    features_list = []
    ids_with_features = []
    
    audio_types = [f'phonation{vowel}' for vowel in 'AEIOU'] + \
                  [f'rhythm{consonant}' for consonant in ['KA', 'PA', 'TA']]

    for index, row in dataframe.iterrows():
        subject_id = row["ID"]
        subject_features = []
        
        if isinstance(subject_id, int):
            formatted_id = f'ID{subject_id:03d}'
        else:
            formatted_id = subject_id

        for audio_type in audio_types:
            audio_file_name = f'{formatted_id}_{audio_type}.wav'
            
            file_path = os.path.join(audio_root_path, data_type, audio_type, audio_file_name)

            if not os.path.exists(file_path):
                 print(f"Arquivo de áudio não encontrado para {formatted_id} e tipo {audio_type} em {file_path}")
                 continue

            features = extract_features(file_path)
            if features is not None:
                subject_features.append(features)
        
        if subject_features:
            features_list.append(np.hstack(subject_features))
            ids_with_features.append(subject_id)
    
    if features_list:
        num_mfcc_features = 13
        num_other_features = 4
        total_features_per_audio_type = num_mfcc_features + num_other_features
        
        feature_names = []
        for audio_type in audio_types:
            for i in range(num_mfcc_features):
                feature_names.append(f'{audio_type}_mfcc_{i}')
            feature_names.append(f'{audio_type}_spectral_centroid')
            feature_names.append(f'{audio_type}_spectral_rolloff')
            feature_names.append(f'{audio_type}_zero_crossing_rate')
            feature_names.append(f'{audio_type}_chroma_stft')

        features_df = pd.DataFrame(features_list, index=ids_with_features, columns=feature_names)
        features_df.index.name = 'ID'
        return features_df
    else:
        return pd.DataFrame()


if __name__ == '__main__':
    train_file_path = '/dataset/data.xlsx'
    test_file_path = '/dataset/test.xlsx'
    audio_root_path = '/dataset/'

    df_train = pd.read_excel(train_file_path, sheet_name='SAND - TRAINING set - Task 2')
    df_test = pd.read_excel(test_file_path, sheet_name='SAND - TESTING set - Task 2')

    print("Processando dados de treinamento...")
    train_audio_features = process_audio_data(df_train, audio_root_path, 'data')
    print(f"Shape das características de áudio de treinamento: {train_audio_features.shape}")
    print(train_audio_features.head())

    print("\nProcessando dados de teste...")
    test_audio_features = process_audio_data(df_test, audio_root_path, 'test')
    print(f"Shape das características de áudio de teste: {test_audio_features.shape}")
    print(test_audio_features.head())

    df_train['ID'] = df_train['ID'].astype(str)
    df_test['ID'] = df_test['ID'].astype(str)
    train_audio_features.index = train_audio_features.index.astype(str)
    test_audio_features.index = test_audio_features.index.astype(str)

    df_train_merged = pd.merge(df_train, train_audio_features, left_on='ID', right_index=True, how='inner')
    df_test_merged = pd.merge(df_test, test_audio_features, left_on='ID', right_index=True, how='inner')

    print("\nDataFrame de treinamento mesclado:")
    print(df_train_merged.head())
    print(df_train_merged.info())

    print("\nDataFrame de teste mesclado:")
    print(df_test_merged.head())
    print(df_test_merged.info())

    df_train_merged.to_csv('processed_train_data.csv', index=False)
    df_test_merged.to_csv('processed_test_data.csv', index=False)
    print("Dados processados salvos em processed_train_data.csv e processed_test_data.csv")