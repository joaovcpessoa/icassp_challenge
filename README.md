# ICASSP

## Pipeline

### 0. Data Collection

**Objetivo:** Obtenção dos dados brutos que serão usados para treinar e testar o modelo.<br>
**Status:** Finalizado<br>
**Comentários:** As bases de dados foram fornecidas pelo desafiante.

### 1. Exploratory Data Analysis (EDA)

**Objetivo:** Entender os dados antes de qualquer modelagem para identificar padrões, distribuições, outliers, correlações, e qualidade dos dados.<br>
**Status**: Pendente<br>
**Comentários:** 

Estatísticas descritivas (média, mediana, desvio padrão);
Visualizações (histogramas, boxplots, heatmaps);
Identificação de valores ausentes e inconsistências;
Entendimento das variáveis-alvo e preditoras.

### 2. Data Preprocessing

**Objetivo:** Limpeza e preparação dos dados para que possam ser usados pelo modelo.<br>
**Status**: Pendente<br>
**Comentários:** 

Contempla situações como tratamento de valores ausentes (imputação ou remoção); remoção de duplicatas; normalização ou padronização de variáveis;
codificação de variáveis categóricas (One-Hot, Label Encoding); redução de dimensionalidade (PCA, feature selection); balanceamento de classes (SMOTE, undersampling/oversampling).


### 3. Data Splitting

**Objetivo:** Separar os dados em conjuntos de treinamento, validação e teste. Importante para evitar overfitting e avaliar o desempenho de forma justa.<br>
**Status**: Pendente<br>
**Comentários:** 

### 4. Treinamento do Modelo (Model Training)

**Objetivo:** O modelo aprende padrões a partir dos dados de treino.<br>
**Status**: Pendente<br>
**Comentários:** 

Escolha de algoritmos: regressão, árvores, redes neurais, SVM etc.
Ajuste de hiperparâmetros iniciais.

### 5. Validação e Ajuste de Hiperparâmetros (Model Validation / Tuning)

**Objetivo:** Otimizar o modelo com base em métricas no conjunto de validação.<br>
**Status**: Pendente<br>
**Comentários:** 

Técnicas:
- Grid Search / Random Search / Bayesian Optimization
- Cross-validation (k-fold)
- Métricas comuns: Acurácia, F1-score, RMSE, AUC, dependendo do problema.

### 6. Model Evaluation

**Objetivo:** Teste final no conjunto de teste, nunca usado antes. Verificar o desempenho real do modelo em dados “novos”. Comparar modelos diferentes e selecionar o melhor.<br>
**Status**: Pendente<br>
**Comentários:**