import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, classification_report
from sklearn.preprocessing import LabelEncoder
import joblib

# Carregar os dados processados
df_train_merged = pd.read_csv("processed_train_data.csv")
df_test_merged = pd.read_csv("processed_test_data.csv")

# Preparar os dados
X_train = df_train_merged.drop(["ID", "ALSFRS--R_end"], axis=1)
y_train = df_train_merged["ALSFRS--R_end"]
X_test = df_test_merged.drop(["ID", "ALSFRS--R_end"], axis=1)

# Codificar a coluna "Sex" (gênero)
le = LabelEncoder()
X_train["Sex"] = le.fit_transform(X_train["Sex"])
X_test["Sex"] = le.transform(X_test["Sex"])

# Converter o tipo de dado da coluna "ID" para string no df_test_merged
df_test_merged["ID"] = df_test_merged["ID"].astype(str)

# Treinar o modelo (RandomForestClassifier como ponto de partida)
# O problema é de classificação multiclasse, então RandomForest é uma boa escolha.
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Salvar o modelo treinado
joblib.dump(model, "random_forest_model.pkl")
print("Modelo RandomForest treinado e salvo como random_forest_model.pkl")

# Prever no conjunto de treinamento para verificar o desempenho
y_train_pred = model.predict(X_train)
print("\nRelatório de Classificação no conjunto de treinamento:")
print(classification_report(y_train, y_train_pred))
print(f"F1-Score (macro avg) no treinamento: {f1_score(y_train, y_train_pred, average='macro')}")

# Gerar previsões para o conjunto de teste
y_test_pred = model.predict(X_test)

# Criar um DataFrame com os IDs e as previsões
predictions_df = pd.DataFrame({"ID": df_test_merged["ID"], "ALSFRS--R_end_Predicted": y_test_pred})

# Salvar as previsões em um arquivo CSV
predictions_df.to_csv("task2_predictions.csv", index=False)
print("Previsões para o conjunto de teste salvas em task2_predictions.csv")

print("\nModelo treinado e previsões geradas com sucesso.")