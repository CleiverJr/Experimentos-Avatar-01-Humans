# Modulo 08: Comparativo Mestre SOTA — A Prova de Fogo de Todos os Modelos

Este modulo consolida o experimento comparativo definitivo do projeto, submetendo os 6 modelos generativos do estado da arte a **exata mesma entrada condicional** para evidenciar empiricamente o que cada arquitetura aprimora.

---

## 1. Demonstracao Visual em Grade 2x3

![Comparativo Mestre SOTA](demo_comparativo_mestre.gif)

- **Video com Audio HD:** [video_comparativo_mestre.mp4](video_comparativo_mestre.mp4)
- **Formato:** Grade 2x3 em resolucao 1920x1370 @ 25 FPS
- **Audio de Teste:** `data/prova_de_fogo.wav` (9.69s | 242 frames)
- **Retrato Fonte:** `data/vasa_portrait.jpg` (Retrato neutro canonico)

### Disposicao dos Modelos na Grade:
```
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│  VASA-1 (Microsoft)     │  AUHead (ICLR 2026)     │  InstructAvatar (AAAI)  │
│  Dinamica Holistica     │  Controle Muscular FACS │  Direcao Cenica NLP     │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│  Audio2Photoreal (Meta) │  OmniHuman-1.5 (Byte)   │  Motion Diffusion (MDM) │
│  Escuta Ativa & Nodding │  Arquitetura Dual       │  Difusao Estocastica    │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

---

## 2. O Prompt Unificado: "A Prova de Fogo"

Para submeter os modelos a situacoes limite, o audio de teste foi estruturado em 3 fases distintas:

```
[0.0s a 2.4s]   FASE 1: CONCENTRACAO & FOCO
                Texto: "Analise esta hipotese com atencao."
                Desafio: Postura analitica e expressao compenetrada.

[2.4s a 4.6s]   FASE 2: PAUSA REFLEXIVA DE 2.2 SEGUNDOS EM SILENCIO ABSOLUTO
                Desafio Critico: O que o avatar faz quando nao ha som?
                - Fica congelado (uncanny valley)?
                - Fica com a boca aberta / dentes expostos?
                - Desvia o olhar para pensar?
                - Acena a cabeca em escuta ativa?

[4.6s a 9.69s]  FASE 3: CLIMAX & CONVICCAO ASSERTIVA
                Texto: "Exatamente! Quando a mente imagina o futuro, a inteligencia ganha vida!"
                Desafio: Elevacao de queixo, sorriso genuino, enfases motoras e energia cinetica.
```

---

## 3. Analise Comparativa: O Que Cada Modelo Melhora

| Modelo | Fase 1: Foco Analitico | Fase 2: Silencio (Prova da Boca e Olhar) | Fase 3: Conviccao e Climax | O Que Este Modelo Aprimora |
| :--- | :--- | :--- | :--- | :--- |
| **VASA-1** | Articulacao fonetica basal neutra. | **Passivo:** Boca semi-aberta com exposicao dentaria residual (sem VAD). | Articulacao sonora comum sem intencao emocional. | **Baseline holistico:** Referencia de partida sem intervencao comportamental. |
| **AUHead** | Ativacao muscular do corrugador (AU04 = 0.85): cenho franzido evidente. | Relaxamento gradual das Action Units faciais. | Sorriso Duchenne radiante com zigomatico (AU12 = 0.85) e orbicular (AU06 = 0.65). | **Controle anatomico:** Expressividade muscular cirurgica e sorriso aberto genuino. |
| **InstructAvatar** | Postura altiva de orador com queixo elevado ($\text{Pitch} = -4.5^\circ$). | **Labios selados:** `vad_alpha = 0.0` com boca 100% ocluida e fechada. | Presenca cenica imponente ($\text{Pitch} = -5.5^\circ$) e articulacao clara. | **Direcao cenica:** Postura de palco teatral e prevencao de boca entreaberta via NLP. |
| **Audio2Photoreal** | Fala ativa em turno conversacional. | **Escuta Ativa:** Dispara 2 acenos nitidos (*nodding* $\Delta \text{Pitch} = +5.5^\circ$) com boca 100% selada. | Retomada fluida de turno de fala sem descontinuidade. | **Comportamento social:** Balanca a cabeca em concordancia diadica durante o silencio. |
| **OmniHuman-1.5** | Arco 1: Foco introspectivo compenetrado ($\text{Pitch} = +2.5^\circ$). | **Gaze Aversion Notavel:** Vira cabeca e olhar para esquerda/cima ($\text{Yaw} = -9.0^\circ$, $\text{Pitch} = -3.5^\circ$). | Arco 3: Elevacao assertiva de queixo ($\text{Pitch} = -4.5^\circ$) e olhar direto. | **Cognicao deliberativa:** Simula pensamento e desvio de olhar reflexivo antes da resposta. |
| **MDM (Diffusion)** | Amostragem estocastica com cinematica viva. | Dinamica postural organica continua livre de rigidez. | Ampla dispersao angular tridimensional livre do colapso estatistico a media. | **Anti-colapso a media:** Movimentacao angular continua, rica e natural. |

---

## 4. Como Reproduzir

```bash
# 1. Gerar as 6 trajetorias cinematicas com o prompt unificado
python Implementacoes/08_comparativo_mestre_sota/gerar_trajetorias_comparativo.py

# 2. Renderizar a grade 2x3 (1920x1370) na GPU MPS e gerar o video e GIF
python Implementacoes/08_comparativo_mestre_sota/renderizar_grade_comparativa.py
```
