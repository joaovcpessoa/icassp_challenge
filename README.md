# ICASSP

## Análise exploratória

Definição das classes:
- Classe 1: ELA com disartria grave
- Classe 2: ELA com disartria moderada
- Classe 3: ELA com disartria leve
- Classe 4: ELA sem disartria
- Classe 5: Saudável

Distribuição das classes no dataset de treinamento:
- Class 1: 2.2%
- Class 2: 9.55%
- Class 3: 20.95%
- Class 4: 27.94%
- Class 5: 39.33%

### Baseline

Usando Visual Transformer (ViT) -> Averaged F1-score = 0.606 na validação do dataset de treino

- <b>Estrutura dos Dados:</b> Consistem em arquivos de áudio (.wav) e metadados (.xlsx)

- <b>Metadados:</b> A análise dos arquivos .xlsx mostrou as características demográficas dos participantes, como idade e sexo. Para o conjunto de treino, há 272 amostras com uma idade média de aproximadamente 63,5 anos. O conjunto de teste possui 67 amostras.

- <b>Dados de Áudio:</b> Usei uma função que extraiu características básicas dos áudios, como duração, energia e taxa de amostragem (sr). Notou-se que todos os áudios possuem uma taxa de amostragem de 8000 Hz, o que é ótimo para a consistência do modelo.

- <b>Variação da Duração:</b> Sua análise, especialmente os histogramas e boxplots, confirmou uma das suas principais dificuldades: os áudios têm durações variadas, tanto no conjunto de treino (média de 13,8s) quanto no de teste (média de 12,8s).

Como nem tudo são flores, vamos falar sobre os problemas, mas vale lembrar que não fui convidado para apontar problemas e sim propor soluções, então tentarei realizar algumas ações que considero ao alcance do meu nível de conhecimento para solucionar/minimizar.

<b>Problema 1:</b> Os áudios possuem durações diferentes

Pelo que andei me estudando sobre o assunto, modelos como CNNs esperam vetores de características de tamanho fixo para cada amostra.

Discutindo com a equipe pensamos em duas abordagens para resolver isso:

1 - <b>Padronizar o Tamanho do Áudio (Padding/Truncating)</b>

Basta definir um comprimento fixo (em número de amostras). Áudios mais curtos são preenchidos com silêncio (zeros) no final (padding), e áudios mais longos são cortados (truncating). Então se definirmos um comprimento de 15 segundos (15 * 8000 = 120.000 amostras), um áudio de 12 segundos será preenchido com 3 segundos de silêncio, e um de 17 segundos terá os 2 últimos segundos descartados.

2 - <b>Extrair Features com Agregação Temporal (Feature Aggregation)</b>:

Em vez de usar o áudio bruto, basta extrair características (features) de pequenas janelas de tempo (frames) ao longo de todo o áudio. Depois, calcular estatísticas sobre essas características (média, desvio padrão, mínimo, máximo, etc.). O resultado é um vetor de features de tamanho fixo, independentemente da duração do áudio.
Para um áudio, podemos calcular os Coeficientes Cepstrais de Frequência Mel (MFCCs) para cada frame de 25ms. Em seguida, calcular a média e o desvio padrão de cada coeficiente ao longo de todos os frames e gerar um vetor de tamanho fixo.

<b>Problema 2:</b> Que diabo de feature contribui para o que buscamos?

As features fonéticas que o aplicativo captura são: Frequência Fundamental (F0), Jitter, Shimmer e HNR

São características acústicas específicas da produção de voz, frequentemente usadas para detectar patologias vocais.

- Frequência Fundamental (F0): A frequência mais baixa da vibração das cordas vocais, percebida como o "tom" da voz.
- Jitter: Mede a variação da frequência fundamental entre ciclos vibratórios consecutivos (instabilidade na frequência).
- Shimmer: Mede a variação da amplitude entre ciclos consecutivos (instabilidade na amplitude/volume).
- HNR (Harmonics-to-Noise Ratio): Relação harmônico-ruído, que quantifica a proporção de energia harmônica (voz) em relação à energia de ruído (sopro, aspereza).

Já temos conhecimento das bibliotecas <code>librosa</code>, da <code>tsfresh</code> (Valeu Rafael ;-;) e mavegando pelos confins da internet encontrei uma tal de <code>parselmouth</code> (Bruxaria das brabas). Depois podemos confirmar com algum mago do aúdio se ela vale algo.

Podemos gerar imagens dos espectrogramas e tentar usar uma CNN...

## Extração das features

- Fo(Hz): A frequência fundamental, que representa a altura média da voz.
- Fhi(Hz): A frequência fundamental máxima, que indica a altura mais alta do sinal de voz.
- Flo(Hz): A frequência fundamental mínima, que representa a altura mais baixa do sinal de voz.

- Jitter:
    - Jitter(%): Representa a porcentagem de variação de frequência (jitter) na voz, indicando irregularidades na altura.
    - Jitter(Abs): Jitter absoluto, que mede a quantidade bruta de perturbação de frequência.
    - RAP, PPQ, DDP: Métricas de jitter específicas adicionais que ajudam a quantificar as variações de frequência ao longo do tempo, oferecendo diferentes maneiras de calcular irregularidades na altura.

- Shimmer: Mede a variação de amplitude, indicando a flutuação na intensidade do sinal de voz.
- Shimmer(dB): Uma versão do shimmer baseada em decibéis que quantifica as perturbações de amplitude em unidades logarítmicas.
- Shimmer:APQ3, Shimmer:APQ5, MDVP:APQ, Shimmer:DDA: Várias métricas de shimmer que avaliam diferentes aspectos da instabilidade de amplitude, incluindo variações de curto e longo prazo.

- NHR: Quantifica a quantidade de ruído em relação aos componentes harmônicos da voz, fornecendo informações sobre a qualidade vocal. Um NHR mais alto sugere um sinal de voz mais ruidoso.
- HNR: Mede a proporção entre harmônicos (sinal de voz nítido) e ruído. Um valor mais alto indica melhor clareza do sinal de voz e menos ruído.

- RPDE: Entropia da densidade do período de recorrência, uma medida da complexidade e periodicidade do sinal de voz.
- DFA: Análise de flutuação detendenciada, um método usado para analisar a autossimilaridade do sinal de voz, revelando dependências de longo prazo e comportamento fractal.
- spread1, spread2: Medidas de variações na dispersão do sinal, que ajudam a entender como o sinal flutua ao longo do tempo.
- D2: Dimensão de correlação, uma métrica para medir a complexidade e o número de dimensões no sinal. Ela ajuda a quantificar a complexidade dinâmica do sinal de voz.
- PPE: A entropia do período de altura quantifica a irregularidade ou desordem nos períodos de altura, indicando o nível de imprevisibilidade no sinal de voz.

Acho que a melhor forma de fazer isso é dividir em blocos:
- Extração de F0 e estatísticas básicas (Fo, Fhi, Flo)
- Extração de perturbações de frequência e amplitude (Jitter e Shimmer, com todas as variações)
- Extração de medidas não lineares (RPDE, DFA, D2, spread1, spread2, PPE)

### Qual biblioteca usar?

A primeira pergunta que me fiz é se alguma biblioteca usa essas equações descritas nos artigos para os cálculos de alguns parâmetros. Como por exemplo:

$Jitter(\%) = \frac{(1/(N-1)) \sum_{i=1}^{N-1} |T_i - T_{i+1}|}{(1/N) \sum_{i=1}^{N} T_i}$

$Shimmer(dB) = \frac{1}{N-1} \sum_{i=1}^{N-1} \left| 20 \log\left(\frac{A_{i+1}}{A_i}\right) \right|$

A biblioteca <code>praat-parselmouth</code> não reimplementa esses algoritmos, na verdade ela é um <i>wrapper</i> que chama diretamente o código-fonte original em C++ do Praat, o software de análise fonética (https://www.fon.hum.uva.nl/praat/). No manual oficial do software, a métrica "Jitter (local, %)" é definida exatamente como a média da diferença absoluta entre períodos consecutivos, dividida pelo período médio. Da mesma forma, "Shimmer (local, dB)" é definido como a média do valor absoluto da diferença em decibéis (20 * log10) entre as amplitudes de ciclos consecutivos.

Para a frequência fundamental (pitch), o texto do artigo menciona o algoritmo [YIN](http://audition.ens.fr/adc/pdf/2002_JASA_YIN.pdf). A biblioteca é capaz de usar. O "gênero e idade" pode ser considerado relevante para definir os limites de pitch (pitch_floor e pitch_ceiling). Valores comuns informados na documentação até o momento:
- Homem: pitch_floor=75, pitch_ceiling=300
- Mulher: pitch_floor=100, pitch_ceiling=500

Para o HNR o texto menciona o algoritmo de Krom. Também método padrão de HNR no Praat.

Irei utilizar medidas clássicas usando <code>praat-parselmouth</code> e <code>librosa</code> + métodos numéricos para as medidas não lineares (RPDE, DFA etc)

### Extra

Sinto que o tempo perdido nesse processo ajudou a entender a real profundidade do problema... Partindo para uma nova abordagem com novos dados.

Precisamos de um método que seja eficiente, estatisticamente robusto e capaz de dizer quais colunas realmente importam. Claramente existem várias formas de fazer isso...

Tentei usar um método wrapper. Eles testam subconjuntos de features treinando um modelo para cada subconjunto.

- Sequential Forward Selection (SFS)
- Recursive Feature Elimination (RFE)

Como pode ver nos códigos, fracessei miseravelmente...

Dá para tentar métodos de filtragem estatística, analisando cada feature individualmente, sem treinar modelo.

- Correlação com a classe (mutual_info_classif, f_classif do scikit-learn)
- Correlação entre features (para remover redundantes)
- Variância baixa (descartar colunas quase constantes)

Só que isso não captura interações entre features e eu não creio que seja possível realizar isso no tempo que temos, pois a quantidade de features é massiva

Tem uma classe de métodos que eu apliquei na minha época de TIM, mas considero eles algo próximo da bruxaria.

- Árvores de decisão / Random Forest / XGBoost / LightGBM → feature_importances_
- Modelos lineares com regularização L1 (LASSO)
- Permutation importance / SHAP após o treino

Eu inclusive tentei o random forest no princípio e estava razoável, com bem menos features do que o pessoal conseguiu retirar, talvez seja válido rodar com esse novo conjunto...