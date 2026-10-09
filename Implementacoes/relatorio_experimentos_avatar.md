# Pesquisa Trilha D: Sintese e Controle de Avatares Neurais
### Relatorio Pratico de Engenharia, Mecanismos Comportamentais e Decisoes de Produto

> **Arquivo PDF Oficial:** [`Implementacoes/relatorio_experimentos_avatar.pdf`](relatorio_experimentos_avatar.pdf) *(Documento clean de 2 paginas para apresentacao em reuniao)*

---

## 1. O Contexto Real: Engenharia Reversa e Emulacao dos Modelos

**Importante esclarecer de imediato:** A grande maioria dos modelos de ponta apresentados pela industria (como o **VASA-1** da Microsoft, **OmniHuman-1.5** da ByteDance, **Audio2Photoreal** da Meta Reality Labs, **InstructAvatar** e **AUHead**) **nao possui codigo-fonte nem pesos de rede liberados publicamente**. Sao pesquisas fechadas e proprietarias.

Por isso, o que construimos aqui e, de forma transparente, uma **engenharia pragmatica de alto nivel**: adotamos o motor neural de codigo aberto do **LivePortrait / Ditto (ACM MM 2025)** como espaco latente e base anatomica compartilhada (21 keypoints 3D implícitos + rotacao $\mathrm{SO}(3)$), e **implementamos diretamente sobre esse motor os principios matematicos e comportamentais de cada artigo**. Isso nos permitiu testar e comparar as ideias lado a lado sob as mesmas condicoes exatas.

---

## 2. Os 4 Principais Gargalos de Avatares e Como Foram Resolvidos

Ao implementar e rodar os testes, focamos em resolver os quatro defeitos que mais quebram a sensacao de realismo:

1. **Boca aberta e dentes expostos no silencio:** Modelos tradicionais de audio deixam a boca inerte e entreaberta quando o som para. Resolvemos isso implementando uma camada de **Voice Activity Detection (VAD)** que forca o fechamento labial estrito (`vad_alpha = 0.0`) na ausencia de voz.
2. **Cabeca congelada (Colapso MSE):** Treinar modelos com erro medio quadratico faz o avatar paralisar a cabeca. Superamos isso com a **Difusao Estocastica (MDM)**, que mantem micro-movimentos organicos continuos.
3. **Avatar passivo que nao reage ao interlocutor:** Adotamos a dinamica diadica do **Audio2Photoreal (Meta)**, onde o avatar assume o papel de ouvinte, selando a boca e balancando a cabeca afirmativamente (*Head Nods*) enquanto ouve.
4. **Olhar fixo de teleprompter:** Implementamos o **Gaze Aversion do OmniHuman (ByteDance)**, no qual o avatar desvia a cabeca e o olhar para cima/esquerda para "pensar" antes de responder, simulando deliberacao cognitiva humana.

---

## 3. O Que Cada Modelo Agrega na Pratica

- **VASA-1 (Microsoft Research, 2024):** Sintese holistica livre direto do som. Serve de referencia basal pura (sem controles adicionais).
- **AUHead (ICLR 2026):** Controle de musculos faciais isolados (FACS). Permite franzir a testa em concentracao (AU04) ou abrir um grande sorriso genuino (AU12 + AU06).
- **InstructAvatar (AAAI 2025):** Direcao cenica em linguagem natural (*"postura altiva, queixo elevado"*) com fechamento labial automatico em pausas.
- **Audio2Photoreal (Meta, CVPR 2024):** Dialogo entre duas pessoas: o avatar escuta ativamente com acenos harmonicos de cabeca e boca 100% selada.
- **OmniHuman-1.5 (ByteDance, 2025):** Arquitetura de Dois Sistemas: reflexo fonetico rapido + mente deliberativa que desvia o olhar (*Gaze Aversion*) para refletir.
- **Motion Diffusion Model (MDM, ICLR 2023):** Quebra do colapso da pose media via amostragem estocastica livre, garantindo movimento vivo e solto.

---

## 4. O Experimento Mestre: "A Prova de Fogo" (Grade 2x3)

Colocamos os 6 modelos lado a lado com a **exata mesma entrada** (audio de 9.69s com fala concentrada, uma pausa critica de 2.2s de silencio absoluto, e um climax oratorio final). Isso evidenciou com clareza visual o que cada modelo melhora:

| Modelo | Fase 1: Fala Inicial | Fase 2: Silencio de 2.2s | Fase 3: Climax | Diferencial Observado |
| :--- | :--- | :--- | :--- | :--- |
| **VASA-1** | Fala neutra direta. | Boca semi-aberta passiva (sem VAD). | Fala comum sem intencao. | Baseline puro de comparacao. |
| **AUHead** | Cenho franzido (AU04=0.85). | Relaxamento gradual muscular. | Grande sorriso Duchenne (AU12). | Expressividade muscular cirurgica. |
| **InstructAvatar** | Postura ereta (Pitch -4.5 deg). | **Labios 100% selados (`vad=0`).** | Queixo erguido e oratoria firme. | Presenca de palco e boca fechada. |
| **Audio2Photoreal** | Turno de fala normal. | **2 Acenos claros (+5.5 deg) + boca selada.** | Retomada suave de conversa. | Escuta ativa (concorda acenando). |
| **OmniHuman-1.5** | Foco compenetrado inicial. | **Gaze Aversion: vira o rosto (-9 deg).** | Foco direto frontal e queixo alto. | Desvia o olhar para pensar. |
| **Motion Diffusion** | Cinematica estocastica viva. | Dinamica postural organica continua. | Rica amplitude angular tridimensional. | Elimina a cabeca congelada/rigida. |

---

## 5. Recomendacoes Diretas para Decisao de Produto

Se fossemos escolher a "receita de bolo" ideal para colocar um avatar em producao hoje:

1. **Camada VAD Obrigatoria:** Qualquer motor de fala precisa ter um limitador de VAD (*Voice Activity Detection*). Se o usuario parou de falar ou o avatar fez uma pausa, o sistema deve zerar o deslocamento labial (`vad_alpha = 0.0`). Isso acaba definitivamente com a impressao de boca aberta ou dentes flutuantes.
2. **Para Assistentes e Atendimento Interativo:** Adotar a dinamica do **Audio2Photoreal + InstructAvatar**. O avatar escuta o cliente acenando com a cabeca e mantem os labios fechados. Isso gera empatia imediata.
3. **Para Aulas e Apresentacoes Longas:** Usar a arquitetura cognitiva do **OmniHuman-1.5 com AUHead**. O desvio de olhar reflexivo (*Gaze Aversion*) antes de responder duvidas e os sorrisos em momentos-chave removem a sensacao de "robo lendo texto".
4. **Viabilidade Tecnica:** Todo o pipeline roda em tempo real na etapa de keypoints e levou ~4 minutos para renderizar 10 segundos de video full-HD no chip Apple Silicon via GPU MPS. E perfeitamente escalavel em servidores de producao.

---

**Relatorio de Pesquisa Trilha D** | Cleiver Junior | Experimentos Avatar 01 Humans  
**Repositorio com Videos e Codigos:** github.com/CleiverJr/Experimentos-Avatar-01-Humans
