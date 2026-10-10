# Modulo 05: Audio2Photoreal (Meta Reality Labs, CVPR 2024) — Dialogo Diadico e Escuta Ativa

Este modulo implementa o comportamento social e conversacional em cenarios diadicos (dois interlocutores), com base nas pesquisas do paper **Audio2Photoreal: Audio-Driven Photorealistic Avatars with Realistic Backchanneling** (Meta Reality Labs, CVPR 2024).

---

## 1. Video Demonstrativo Gerado

![Audio2Photoreal Dialogo Diadico](demo_diadico.gif)

- **Video com Audio HD:** [video_diadico.mp4](video_diadico.mp4)

- **Arquivo:** `video_diadico.mp4`
- **Duracao:** 14.68 segundos (367 frames)
- **Resolucao:** 1024x1024 @ 25 FPS
- **Cenario:** Alternancia dinamica entre fala ativa, escuta atenta (*backchanneling*) e retomada do turno.

---

## 2. A Tese do Audio2Photoreal

A comunicacao humana interpessoal nao e composta apenas por emissoes isoladas de fala. Em uma conversa real:
- O ouvinte fornece feedback continuo nao-verbal (*backchanneling*), sinalizando atencao e compreensao;
- Quando o interlocutor esta falando, a boca do ouvinte permanece **completamente selada em repouso**, enquanto a cabeca realiza micro-acenos harmonicos (*nodding*);
- Falhas nessa dinamica (como a boca do avatar se mexendo ao ouvir a voz de outra pessoa) destroem o realismo da interacao.

---

## 3. Arquitetura de Estados e Deteccao VAD

O sistema monitora a distribuicao de energia do sinal atraves de um classificador de Voice Activity Detection (VAD) acustico em janelas moveis:

```
[0.0s a 4.8s]  ESTADO 1: FALA ATIVA DO AVATAR
               - Articulacao labial completa e gestual espontaneo

[4.8s a 9.6s]  ESTADO 2: ESCUTA ATIVA (INTERLOCUTOR FALA)
               - Boca 100% selada em repouso (vad_alpha = 0.0)
               - Injecao de 2 acenos amortecidos de cabeca (Nodding a 2.2 Hz)

[9.6s a 14.6s] ESTADO 3: RETOMADA DA PALAVRA PELO AVATAR
               - Reativacao fluida do motor de fonacao
```

### Formulacao Matematica do Aceno de Cabeca (*Nodding*):
O aceno afirmativo e sintetizado por uma funcao senoidal amortecida com envelope gaussiano:

$$\Delta \theta_{pitch}(t) = A \cdot \exp\left(-\frac{(t - t_{pico})^2}{2\sigma^2}\right) \cdot \sin(2\pi f (t - t_{inicio}))$$

onde:
- Frequencia fundamental de aceno: f = 2.2 Hz;
- Amplitude angular: A em [1.8°, 2.5°];
- Desvio padrao do envelope: sigma = 0.35 s.

---

## 4. Resultados e Telemetria

- **Repouso Bucal na Escuta:** Deslocamento labial vertical nulo (Delta y_exp = 0.000) durante a fala do interlocutor;
- **Cinematica de Cabeca:** 2 ciclos de aceno perfeitamente sincronizados com os picos de entonacao do interlocutor;
- **Zero Jitter:** Transicao suave de retorno a fala atraves de interpolacao Hermite (smoothstep).

---

## 5. Como Reproduzir

```bash
# 1. Executar o simulador diadico e gerar a trajetoria (.npz)
python Implementacoes/05_audio2photoreal_dialogue/audio2photoreal_diadico.py

# 2. Renderizar o video com telemetria dos turnos (.mp4) na GPU MPS
python Implementacoes/05_audio2photoreal_dialogue/renderizar_video_diadico.py
```
