# 02. Análise Profunda das Sementes de Pesquisa

Este documento cataloga a arquitetura, representações e estratégias das 6 sementes de estudo da Trilha D.

---

## 1. VASA-1 (Microsoft Research, 2024)
* **Título:** *VASA-1: Lifelike Audio-Driven Talking Faces with Visual Affective Skills*
* **Problema:** A maioria dos modelos falha em reproduzir microexpressões, olhar expressivo e movimentação natural de cabeça simultaneamente em alta resolução e baixa latência.
* **Arquitetura:**
  1. **Disentangled Face Latent Space:** Um autoencoder facial treinado em vídeos divide cada frame em:
     * Vetor de Identidade $z_{id}$ (fixo por sujeito);
     * Vetor de Pose Rígida 3D $z_{pose} = [\mathbf{R}, \mathbf{t}]$;
     * Vetor de Dinâmica Facial Não-Rígida $z_{dyn}$ (expressões, abertura labial, piscar).
  2. **Holistic Diffusion Transformer:** Uma rede temporal processa o áudio $A_{1:T}$ e desruidifica uma trajetória latente conjunta $[z_{pose}, z_{dyn}]_{1:T}$.
  3. **Conditional Control Signals:** Permite passar vetores de controle opcionais:
     * $c_{gaze}$ (direção do olhar nos eixos X/Y);
     * $c_{dist}$ (distância da cabeça em relação à câmera);
     * $c_{emo}$ (matriz de polaridade afetiva).
* **Taxa de Renderização:** 512x512 a 40+ FPS (tempo real).

---

## 2. InstructAvatar (AAAI 2025 - Peking University)
* **Título:** *InstructAvatar: Text-Guided Emotion and Motion Control for Avatar Generation*
* **Problema:** Usuários desejam direcionar a atuação do avatar em linguagem natural livre, e não através de rótulos emocionais fechados ou sliders manuais.
* **Arquitetura:**
  1. **Two-Branch Diffusion Architecture:**
     * **Ramificação Acústica:** Condiciona a sincronia fonética e labial via features extraídas de encoders de áudio (ex: Wav2Vec 2.0).
     * **Ramificação Textual:** Condiciona o estilo, velocidade e intensidade dos movimentos faciais e de cabeça usando embeddings de linguagem natural gerados por encoders de texto (CLIP / RoBERTa / LLM).
  2. **FACS & Motion Latent VAE:** Extrai representações de movimento contínuo a partir de vídeos reais.
  3. **Automated Annotation Pipeline:** Utilização de modelos multimodais de visão (GPT-4V) para rotular milhares de vídeos com instruções densas ("ergue as sobrancelhas", "acena lentamente com a cabeça", "expressão irônica").

---

## 3. AUHead (ICLR 2026)
* **Título:** *AUHead: Realistic Emotional Talking Head Generation via Action Units Control*
* **Problema:** Métodos baseados apenas em latentes "caixa-preta" perdem o controle anatômico fino e geram expressões emocionais genéricas.
* **Arquitetura:**
  1. **Spatial-Temporal Action Unit Tokenization:** Discretiza ou parametriza o espaço contínuo dos 46+ Action Units (AUs) do FACS de Paul Ekman.
  2. **Stage 1 (Cognição - Emotion-then-AU Chain-of-Thought):** Um modelo de áudio-linguagem (ALM) analisa o áudio de fala e infere primeiro a categoria/intensidade emocional e, em seguida, a sequência exata de ativação temporal de cada AU.
  3. **Stage 2 (Síntese Controlável):** Um modelo de difusão de vídeo condicionado diretamente nessa matriz de AUs renderiza o resultado final sem descolamento anatômico.

---

## 4. Audio2Photoreal (CVPR 2024 - Meta Reality Labs)
* **Título:** *From Audio to Photoreal Embodiment: Synthesizing Humans in Conversations*
* **Problema:** Humanóides conversando em RV/RA precisam gesticular e expressar postura corporal crível ao longo de conversas reais de duas pessoas (diádicas).
* **Arquitetura Híbrida (VQ-VAE + Diffusion):**
  1. **Codebook de Poses Corporais (VQ-VAE):** Para evitar que a rede invente posturas corporais com ossos torcidos ou impossíveis fisicamente, o VQ-VAE quantiza o espaço de poses em um catálogo de posturas naturais.
  2. **Diffusion Motion Generator:** Modela a dinâmica fina dos braços, mãos, tronco e cabeça sobre esse espaço quantizado, gerando transições suaves e detalhes expressivos a partir da conversa de áudio dos dois interlocutores.

---

## 5. OmniHuman-1.5 (ByteDance, 2025)
* **Título:** *OmniHuman-1.5: Instilling an Active Mind in Avatars via Cognitive Simulation*
* **Problema:** Avatares puramente reativos parecem vazios ("zumbis"), pois humanos reais planejam o que vão expressar antes ou durante a fala com base no conteúdo semântico.
* **Arquitetura Cognitiva de Dois Sistemas:**
  1. **Sistema 1 (Intuitivo / Reativo):** Rápido, acoplado ao ritmo acústico e fonemas instantâneos (lip-sync, modulações de tom, micro-vibrações).
  2. **Sistema 2 (Deliberado / Semântico):** Um MLLM interpreta o contexto do discurso e gera "metadados de intenção" (planejamento de gestos com ênfase, olhares reflexivos, sorrisos que antecipam piadas).
  3. **Diffusion Transformer Unificado:** Funde os sinais dos Sistemas 1 e 2 para renderizar vídeos de padrão cinematográfico de corpo e rosto.

---

## 6. Motion Diffusion Models (MDM)
* **Princípio Matemático:**  
  Dado uma trajetória de parâmetros $X = [x_1, \dots, x_T] \in \mathbb{R}^{T \times D}$ (onde $D$ é a dimensão da pose de cabeça + expressão):
  * **Difusão Direta:**
    $$q(X_t \mid X_0) = \mathcal{N}\left(X_t; \sqrt{\bar{\alpha}_t} X_0, (1 - \bar{\alpha}_t) \mathbf{I}\right)$$
  * **Previsão de Movimento Limpo ($X_0$-prediction):**
    Em animação motora, é mais estável treinar a rede para prever diretamente o movimento desruidificado $\hat{X}_0 = f_\theta(X_t, t, c)$ do que o ruído $\epsilon_t$, pois isso permite aplicar perdas geométricas (como suavidade de aceleração e limites articulares anatômicos) durante o treinamento:
    $$\mathcal{L} = \mathbb{E} \left[ \| X_0 - \hat{X}_0 \|^2 + \lambda_{geom} \mathcal{L}_{geom}(\hat{X}_0) \right]$$
  * **Classifier-Free Guidance (CFG):**
    Permite amplificar o controle textual/emocional:
    $$\hat{X}_0^{guided} = \hat{X}_0^{uncond} + s \cdot (\hat{X}_0^{cond} - \hat{X}_0^{uncond})$$
    Onde $s > 1$ aumenta a fidelidade à instrução (ex: raiva mais intensa ou sorriso mais marcado).
