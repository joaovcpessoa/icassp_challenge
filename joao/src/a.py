df = pd.read_csv(r'C:\Users\joaov_zm1q2wh\python\icassp_challenge\joao\data\features_all.csv')

X = df.drop(columns=["ID", "Class"])
y = df["Class"]

cols_com_nan = X.columns[X.isna().any()]
print("Colunas com NaN:", cols_com_nan)

linhas_com_nan = X[X["NHRPA"].isna()].index
print("Linhas com NaN em NHRPA:", linhas_com_nan)
print("Valores problemáticos em NHRPA:\n", X.loc[linhas_com_nan, "NHRPA"])

X = X.dropna(subset=["NHRPA"])
y = y[X.index]

X = X.astype(float)

X_normalized = normalize(X, axis=1)
X_normalized = pd.DataFrame(X_normalized, columns=X.columns, index=X.index)

print("X_normalized dtypes:\n", X_normalized.dtypes)
print("X_normalized shape:", X_normalized.shape)

X_train, X_test, y_train, y_test = train_test_split(
    X_normalized, y, test_size=0.2, random_state=42, stratify=y
)

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_leaf=5,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)

y_train_pred = rf.predict(X_train)
y_test_pred = rf.predict(X_test)

print("Acurácia treino:", accuracy_score(y_train, y_train_pred))
print("Acurácia teste:", accuracy_score(y_test, y_test_pred))
print("\nRelatório de classificação (teste):\n", classification_report(y_test, y_test_pred))
print("\nMatriz de confusão (teste):\n", confusion_matrix(y_test, y_test_pred))