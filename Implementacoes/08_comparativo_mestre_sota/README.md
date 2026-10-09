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
| **VASA-1** | Articulacao fonetica basal neutra. | **Passivo:** Cabeca e rosto praticamente congelados sem som. | Articulacao sonora comum sem intencao emocional. | **Baseline holistico:** Gera movimento espontaneo sem necessidade de driving video. |
| **AUHead** | Ativacao muscular do corrugador (AU04), franzindo a glabela. | Retorno a posicao muscular basal em repouso. | Sorriso de Duchenne com zigomatico maior (AU12) e orbicular (AU06). | **Controle anatomico:** Permite controle muscular isolado e cirurgico via FACS. |
| **InstructAvatar** | Postura altiva ($\text{Pitch} = -2^\circ$) e olhar firme. | **Labios selados:** A atenuacao adaptativa impede exposicao dentaria. | Postura afirmativa e queixo erguido com articulacao labial livre. | **Direcao cenica:** Interpreta linguagem natural livre sem travar a mandibula. |
| **Audio2Photoreal** | Fala ativa em turno conversacional. | **Escuta Ativa:** Dispara 2 acenos harmonicos (*nodding* a $2.2\text{ Hz}$) com boca 100% selada. | Retomada fluida de turno de fala sem descontinuidade. | **Comportamento social:** Simula a dinamica real de conversa entre duas pessoas. |
| **OmniHuman-1.5** | Arco 1: Foco introspectivo compenetrado ($\text{Pitch} = +1.2^\circ$). | **Gaze Aversion:** Desvia o olhar e a cabeca para cima/esquerda para pensar. | Arco 3: Elevacao assertiva de queixo ($\Delta \text{Pitch} = -3.2^\circ$) e olhar direto. | **Mente ativa:** Introduz simulacao deliberativa e cognicao humana superior. |
| **MDM (Diffusion)** | Amostragem estocastica com dinamica viva. | Micro-variacoes cinematicas naturais continuas. | Ampla dispersao angular da cabeca livre do colapso estatistico a media. | **Anti-colapso a media:** Elimina a cabeca congelada gerada por modelos de regressao MSE. |

---

## 4. Como Reproduzir

```bash
# 1. Gerar as 6 trajetorias cinematicas com o prompt unificado
python Implementacoes/08_comparativo_mestre_sota/gerar_trajetorias_comparativo.py

# 2. Renderizar a grade 2x3 (1920x1370) na GPU MPS e gerar o video e GIF
python Implementacoes/08_comparativo_mestre_sota/renderizar_grade_comparativa.py
```
