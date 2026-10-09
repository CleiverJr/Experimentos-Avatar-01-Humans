# Modulo 06: OmniHuman-1.5 (ByteDance, 2025) — Arquitetura Cognitiva Dual

Este modulo implementa a simulacao de uma mente ativa em avatares virtuais atraves de arquitetura cognitiva dual, conforme proposto no paper **OmniHuman-1.5: Instilling an Active Mind in Avatars via Cognitive Simulation** (ByteDance Intelligent Creation, 2025).

---

## 1. Video Demonstrativo Gerado

![OmniHuman-1.5 Dual System](demo_omnihuman.gif)

- **Video com Audio HD:** [video_omnihuman.mp4](video_omnihuman.mp4)

- **Arquivo:** `video_omnihuman.mp4`
- **Duracao:** 10.76 segundos (269 frames)
- **Resolucao:** 1024x1024 @ 25 FPS
- **Estrutura:** Discurso estruturado em 3 arcos cognitivos com telemetria visual em tempo real.

---

## 2. A Tese do OmniHuman-1.5: Teoria dos Dois Sistemas

Inspirado na psicologia cognitiva de Daniel Kahneman (*Thinking, Fast and Slow*), o modelo divide a geracao em duas instancias complementares:

### Sistema 1 (Pensamento Rapido / Reativo):
- Opera em baixa latencia;
- Traduz diretamente a onda sonora acústica em geometria labial e micro-movimentos reflexos;
- Responde mecanicamente ao estimulo imediato sem compreensao global do discurso.

### Sistema 2 (Pensamento Lento / Deliberativo):
- Opera em nivel semantico superior (simulado por modelos de linguagem multimodal);
- Planeja a macro-trajetoria de atitude corporal, intencoes cênicas e arcos dramáticos;
- Modula a atencao visual e o foco postural do avatar ao longo da narrativa.

---

## 3. Os Tres Arcos Cognitivos Implementados

```
[0.0s a 4.2s]   ARCO 1: PENSAMENTO ANALITICO / INTROSPECCAO
                - Queixo contido (Pitch = +1.50°)
                - Olhar centrado com cenho levemente compenetrado (AU04 = 0.25)

[4.2s a 6.6s]   ARCO 2: PAUSA REFLEXIVA E DESVIO COGNITIVO DO OLHAR (GAZE AVERSION)
                - Humanos desviam o olhar para acessar a memoria interna de trabalho
                - Desvio lateral e ascendente: Yaw = -3.80°, Pitch = -1.80°, Roll = +1.20°
                - Relaxamento de expressao (AU02 = 0.15)

[6.6s a 10.7s]  ARCO 3: ILUMINACAO E CONVICCAO ASSERTIVA
                - Queixo elevado e postura afirmativa: Pitch = -3.20°
                - Olhar fixado diretamente no espectador
                - Enfases motoras de cabeca sincronizadas com o climax do discurso
```

---

## 4. Metricas e Validacao Quantitativa

O processamento da trajetoria `trajetoria_omnihuman.npz` registrou as seguintes metricas de comportamento:

- **Desvio de Olhar (Gaze Aversion no Arco 2):** $\Delta \text{Yaw} = -3.80^\circ$ de rotacao horizontal com suave amortecimento;
- **Elevacao Assertiva de Queixo (Arco 3):** $\Delta \text{Pitch} = -3.20^\circ$ em relacao a postura neutra;
- **Sincronia Labial:** Sincronizacao HuBERT preservada integralmente com fechamento bilabial natural.

---

## 5. Como Reproduzir

```bash
# 1. Executar a simulacao dual e salvar a trajetoria (.npz)
python Implementacoes/06_omnihuman_dual_system/omnihuman_sistema_dual.py

# 2. Renderizar o video com monitoramento dos Sistemas 1 e 2 (.mp4) na GPU MPS
python Implementacoes/06_omnihuman_dual_system/renderizar_video_omnihuman.py
```
