# Modulo 01: Ditto Core e Espaco Latente de Movimento (LivePortrait)

Este modulo implementa e valida os fundamentos algebricos e geometricos do espaco latente de deformacao facial canonica 3D, baseado na arquitetura do LivePortrait (Guo et al., 2024).

---

## 1. Fundamentacao Teorica

O modelo desacopla a representacao de um rosto humano em duas entidades matematicas distintas:
1. **Volume de Aparencia e Identidade ($x_s$):** Representado por features neurais volumétricas tridimensionais extraidas do retrato de referencia neutro;
2. **Trajetoria Motora ($x_d$):** Representada por rotacoes rigidas $\mathbf{R} \in \mathrm{SO}(3)$, translacao tridimensional $\mathbf{t} \in \mathbb{R}^3$ e deslocamentos de expressao nao-rigida $\boldsymbol{\delta}_{exp} \in \mathbb{R}^{21 \times 3}$.

### A Equacao de Deformacao Canonica
Para cada um dos 21 keypoints tridimensionais implicitos $\mathbf{x}_{c, i} \in \mathbb{R}^3$ ($i \in \{1, \dots, 21\}$), a coordenada deformada $\mathbf{x}_i$ em um frame e computada por:

$$\mathbf{x}_i = \mathbf{R} \mathbf{x}_{c, i} + \mathbf{t} + \boldsymbol{\delta}_{exp, i}$$

onde:
- $\mathbf{R} \in \mathbb{R}^{3 \times 3}$ e a matriz ortogonal de rotacao gerada a partir dos angulos de Euler $(\theta_{pitch}, \theta_{yaw}, \theta_{roll})$;
- $\mathbf{t} \in \mathbb{R}^3$ representa a translacao global da cabeca nos eixos $(X, Y, Z)$;
- $\boldsymbol{\delta}_{exp, i} \in \mathbb{R}^3$ e o deslocamento de deformacao facial relativo a pose neutra canonica.

---

## 2. Conversao de Bins para Graus e Matriz SO(3)

O espaco de orientacao da cabeca e predito pela rede como uma distribuicao de classificacao sobre 66 bins continuos cobrindo o intervalo $[-90^\circ, +90^\circ]$. 

### Conversao 66 Bins para Graus:
Dado o indice ponderado de classificacao $b \in [0, 65]$:

$$\theta_{deg} = \left(\frac{b}{65} \times 180\right) - 90$$

### Sintese da Matriz Ortogonal de Rotacao:
A partir dos angulos de Tait-Bryan $(\theta_x, \theta_y, \theta_z) = (\text{pitch}, \text{yaw}, \text{roll})$, a matriz de rotacao tridimensional e obtida pelo produto:

$$\mathbf{R} = \mathbf{R}_z(\theta_z) \, \mathbf{R}_y(\theta_y) \, \mathbf{R}_x(\theta_x)$$

Propriedade formal de validacao:
- $\mathbf{R}^T \mathbf{R} = \mathbf{I}_3$
- $\det(\mathbf{R}) = 1.000000$

---

## 3. Decodificacao Neural Foto-Realista

A deformacao dos keypoints governa o campo de fluxo tridimensional:
1. **WarpF3D:** O volume tridimensional de features de aparencia e amostrado via grid sampling tridimensional governado pela diferenca $\Delta \mathbf{x} = \mathbf{x}_d - \mathbf{x}_s$;
2. **Decodificador SPADE:** O volume deformado e projetado bidimensionalmente e decodificado por camadas SPADE (Spatially-Adaptive Denormalization) com discriminadores multi-escala para sintetizar os pixels RGB em resolucao 1024x1024.

---

## 4. Experimentos e Resultados

O script `01_espaco_latente.py` valida algebricamente:
- A ortogonalidade estrita da matriz $\mathbf{R}$ com erro numérico inferior a $10^{-7}$;
- O mapeamento continuo e biunivoco entre o espaco de bins e o espaco angular em graus;
- A invariancia da identidade canonica perante variacoes de pose e expressao.

### Como Reproduzir:
```bash
python Implementacoes/01_ditto_core/01_espaco_latente.py
```
