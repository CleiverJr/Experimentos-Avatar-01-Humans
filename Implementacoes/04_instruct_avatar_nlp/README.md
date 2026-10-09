# Modulo 04: InstructAvatar (AAAI 2025) — Direcao Cenica via Linguagem Natural

Este modulo implementa o controle dramatico e comportamental guiado por texto em linguagem natural livre, fundamentado no paper **InstructAvatar: Text-Guided Emotion and Motion Control for High-Fidelity Talking Avatars** (AAAI 2025).

---

## 1. Video Demonstrativo Gerado

<video src="video_instruct.mp4" controls width="100%"></video>

- **Arquivo:** `video_instruct.mp4`
- **Duracao:** 10.80 segundos (270 frames)
- **Resolucao:** 1024x1024 @ 25 FPS
- **Prompt Cenico Testado:** *"fale com altivez, olhar frontal compenetrado e sorriso sutil"*

---

## 2. A Tese do InstructAvatar

Enquanto modelos baseados em FACS dependem de calibracao manual de coeficientes musculares (AU01, AU12, etc.), o InstructAvatar introduz um operador de traducao semantica que mapeia instrucoes de direcao em linguagem natural para:
1. Vetor continuo de distribuicao emocional ($v_{emo} \in \Delta^7$ no espaco de 8 emocoes fundamentais);
2. Atitude postural estatica e dinamica da cabeca (Pitch, Yaw, Roll);
3. Modulacao fina de Action Units anatomicas.

---

## 3. O Dilema da Oclusao Labial: Solucao do "Efeito Dentes Expostos"

### O Problema Identificado:
Ao injetar offsets de sorriso estatico ($\text{AU12} = 0.90, \text{AU06} = 0.70$) de forma constante em todos os frames, a boca permanece aberta e os dentes ficam expostos ininterruptamente. Como consequencia, o avatar perde a capacidade de tocar os labios nos fonemas bilabiais (/p/, /b/, /m/), gerando um aspecto visual rigido e nao-natural.

### A Solucao Implementada:
Implementou-se uma funcao de **modulacao adaptativa dependente de energia vocal**:

$$\text{AU}_{efetivo}(t) = \text{AU}_{alvo} \times \left(1.0 - \beta \cdot \text{VAD}(t)\right)$$

onde:
- $\text{VAD}(t) \in [0, 1]$ indica a intensidade e energia acustica do frame $t$;
- $\beta \in [0.4, 0.6]$ atenua a rigidez das AUs durante momentos de articulacao labial exigente;
- Limite maximo de $\text{AU12} \le 0.30$ e $\text{AU06} \le 0.20$ durante a fala ativa.

Essa formulacao garante que os labios se fechem completamente nas consoantes, mantendo a expressao de simpatia e confianca quando a mandíbula relaxa.

---

## 4. Metricas e Resultados

- **Postura Corporal:** $\text{Pitch} = -2.50^\circ$ (queixo elevado demonstrando altivez e seguranca), $\text{Yaw} = 0.00^\circ$ (olhar centrado no interlocutor);
- **Sincronia Fonetica:** Zero distorcoes na oclusao labial;
- **Transicoes Suaves:** Curvas de interpolacao sigmoide para variacao temporal de intensidade cênica.

---

## 5. Como Reproduzir

```bash
# 1. Executar o parser semantico e gerar a trajetoria (.npz)
python Implementacoes/04_instruct_avatar_nlp/instruct_avatar_parser.py

# 2. Renderizar o video com telemetria cenica (.mp4) na GPU MPS
python Implementacoes/04_instruct_avatar_nlp/renderizar_video_instruct.py
```
