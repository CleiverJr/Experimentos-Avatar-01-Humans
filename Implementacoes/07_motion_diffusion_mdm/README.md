# Modulo 07: Motion Diffusion Model (MDM / DDPM) — Difusao Cinematica Estocastica

Este modulo implementa o paradigma de difusao generativa estocastica para sintese cinematica de avatares, superando o problema do colapso para a media conforme formalizado pelos papers:
- **Human Motion Diffusion Model (MDM)** (Guy Tevet et al., ICLR 2023);
- **Denoising Diffusion Probabilistic Models (DDPM)** (Jonathan Ho et al., NeurIPS 2020).

---

## 1. Video Demonstrativo Gerado

![Motion Diffusion Model](demo_mdm.gif)

- **Video com Audio HD:** [video_mdm.mp4](video_mdm.mp4)

- **Arquivo:** `video_mdm.mp4`
- **Duracao:** 12.48 segundos (312 frames)
- **Resolucao:** 1024x1024 @ 25 FPS
- **Conteudo:** Discurso explicativo com telemetria cinemática comparando o dilema da regressao deterministica contra a sintese estocastica por difusao.

---

## 2. O Problema da Regressao a Media (*Regression to the Mean*)

Em geracao de movimento guiada por audio ou texto, o mapeamento e inerentemente **1-para-Muitos**:
- Para a mesma frase ("*Modelos de regressao colapsam para a media*"), existem infinitas trajetorias plausiveis de aceno, inclinacao de cabeca e ritmo expressivo;
- Modelos neurais deterministicos treinados com perda de erro quadratico medio ($L_2$ / MSE) convergem para a solucao analitica otima:

$$f_\theta(c) = \mathbb{E}[x \mid c]$$

Como variacoes opostas de movimento se anulam na media estatistica, o avatar gerado por regressao MSE apresenta cabeca paralisada e olhar congelado (*uncanny valley*).

---

## 3. A Formulacao do MDM

O MDM resolve esse colapso modelando a distribuicao estocastica completa $p(x_0 \mid c)$ atraves de um processo de difusao reversa.

### A. Processo Direto de Difusao Gaussiana (Forward Process):
Dado um movimento limpo $x_0 \in \mathbb{R}^{N \times D}$, adiciona-se ruido gaussiano progressivo sob um schedule de variancias $\beta_1, \dots, \beta_T$:

$$q(x_t \mid x_0) = \mathcal{N}\left(x_t; \, \sqrt{\bar{\alpha}_t} x_0, \, (1 - \bar{\alpha}_t) \mathbf{I}\right)$$

onde $\alpha_t = 1 - \beta_t$ e $\bar{\alpha}_t = \prod_{s=1}^t \alpha_s$.

### B. Decisao de Projeto: Predicao Direta de $x_0$ vs Ruido $\epsilon$:
Diferente dos modelos de imagem que preveem o ruido $\epsilon_t$, o MDM estima **diretamente o sinal limpo**:

$$\hat{x}_0 = \mathcal{G}_\theta(x_t, t, c)$$

Essa escolha viabiliza a aplicacao de perdas geometricas e cinematicas fisicas em cada passo de treino:

$$\mathcal{L} = \mathcal{L}_{simple} + \lambda_{vel} \mathcal{L}_{vel}$$

$$\mathcal{L}_{vel} = \frac{1}{N-1} \sum_{i=1}^{N-1} \big\|(x_0^{i+1} - x_0^i) - (\hat{x}_0^{i+1} - \hat{x}_0^i)\big\|^2$$

---

## 4. Metricas e Validacao Experimental Multi-Seed

Para comprovar empiricamente a eliminacao do colapso a media, o script `mdm_difusao_cinematica.py` realizou amostragem estocastica para **duas sementes independentes de ruido** ($\epsilon_{42}$ vs $\epsilon_{101}$) utilizando exatamente o mesmo sinal de audio condicional:

```
================================================================================
METRICAS DE DIVERSIDADE & PRESERVACAO FONETICA DO MDM:
================================================================================
  • Diversidade Angular da Cabeca (Diversity):     3.720°
    (Sementes distintas exploram modos dinamicos variados de aceno e inclinacao)
  • Variacao Facial Restrita (Lip-sync fidelity):   0.0045
    (Abertura labial sincronizada com os mesmos fonemas acusticos)
  • Aceleracao Angular Media (Kinematic Smoothness): 0.0537°/frame²
    (Fluidez fisica continua sem tremores ou oscilacoes de alta frequencia)
================================================================================
```

### Conclusao Experimental:
1. **Preservacao Fonetica:** A boca articula com fidelidade milimetrica os mesmos fonemas do audio nas duas sementes;
2. **Diversidade de Cabeca:** Enquanto a boca fala a mesma frase, cada semente sintetiza um padrao unico de atitude postural, eliminando o congelamento da cabeca.

---

## 5. Como Reproduzir

```bash
# 1. Executar o scheduler DDPM, o Transformer e a analise multi-seed (.npz)
python Implementacoes/07_motion_diffusion_mdm/mdm_difusao_cinematica.py

# 2. Renderizar o video final com telemetria de difusao (.mp4) na GPU MPS
python Implementacoes/07_motion_diffusion_mdm/renderizar_video_mdm.py
```
