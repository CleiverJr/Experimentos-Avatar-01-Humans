"""
Script Gerador do Relatorio Clean (Pesquisa Trilha D)
=====================================================
Gera o documento limpo, direto, sem firulas e sem padroes de formatacao excessiva de IA.
- Apenas o titulo no topo.
- Negritos estritamente no comeco de linhas/topicos.
- Nota sincera sobre modelos proprietarios, risco de deepfakes e engenharia pragmatica/gambiarra.
- Arquivo de Saida: Implementacoes/relatorio_experimentos_avatar.pdf
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Cabecalho superior a partir da pagina 2
        if self._pageNumber > 1:
            self.drawString(18 * mm, 287 * mm, "Pesquisa Trilha D: Sintese e Controle de Avatares Neurais")
            self.drawRightString(192 * mm, 287 * mm, "Relatorio para Reuniao")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(18 * mm, 284 * mm, 192 * mm, 284 * mm)

        # Rodape discreto
        self.drawString(18 * mm, 12 * mm, "Pesquisa Trilha D — Engenharia e Experimentacao")
        self.drawRightString(192 * mm, 12 * mm, f"Pagina {self._pageNumber} de {page_count}")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)

        self.restoreState()


def gerar_relatorio_pdf(caminho_pdf: str):
    doc = SimpleDocTemplate(
        caminho_pdf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    # Tipografia limpa, sem negrito solto no meio de frases
    style_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=8
    )

    style_h1 = ParagraphStyle(
        'SecH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'BodyCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )

    style_note = ParagraphStyle(
        'NoteBox',
        parent=style_body,
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )

    style_tbl_header = ParagraphStyle(
        'TblHeader',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#FFFFFF"),
        alignment=0
    )

    style_tbl_cell = ParagraphStyle(
        'TblCell',
        fontName='Helvetica',
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#1E293B")
    )

    style_tbl_cell_bold = ParagraphStyle(
        'TblCellBold',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # -------------------------------------------------------------------------
    # APENAS O TITULO NO TOPO (SEM SUBTITULO LONG OU METADADOS BUROCRATICOS)
    # -------------------------------------------------------------------------
    story.append(Paragraph("Pesquisa Trilha D: Sintese e Controle de Avatares Neurais", style_title))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=8))

    # -------------------------------------------------------------------------
    # 1. DETALHE IMPORTANTE / CONTEXTO REAL
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Detalhe Importante: Natureza dos Modelos e Abordagem Pratica", style_h1))
    
    nota_texto = (
        "<b>Detalhe Importante:</b> Os modelos de ponta apresentados na literatura recente, como Vasa-1 da Microsoft, "
        "Omnihuman-1.5 da ByteDance, Audio2Photoreal da Meta e InstructAvatar, nao possuem pesos de rede nem codigos-fonte "
        "liberados publicamente. O motivo justificado oficialmente pelas empresas para nao liberarem esses modelos e a preocupacao "
        "com o uso indevido para geracao de deepfakes.<br/><br/>"
        "Portanto, os experimentos realizados aqui foram, de certa forma, uma 'gambiarra' tecnica para conseguir reproduzir e testar "
        "esses SOTAs. Utilizamos como base o motor de codigo aberto do LivePortrait / Ditto (ACM MM 2025), que fornece a espinha dorsal "
        "anatomica latente (21 keypoints tridimensionais e matriz de rotacao craniofacial), e implementamos diretamente sobre esse espaco "
        "os principios matematicos, mecanismos de controle facial, dinamicas de olhar e acenos propostos em cada artigo."
    )
    
    box_data = [[Paragraph(nota_texto, style_note)]]
    box_table = Table(box_data, colWidths=[174 * mm])
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(box_table)
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------------------
    # 2. OS 4 PROBLEMAS PRATICOS RESOLVIDOS
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Os 4 Principais Gargalos de Avatares e Como Foram Resolvidos", style_h1))
    
    p_prob1 = (
        "<b>1. Boca aberta e dentes expostos no silencio:</b> Modelos comuns guiados por audio deixam a boca inerte e entreaberta "
        "quando a pessoa para de falar. Resolvemos isso aplicando uma camada de Voice Activity Detection (VAD) que forca o fechamento "
        "labial estrito (vad_alpha = 0.0) na ausencia de voz, eliminando a sensacao de dentes flutuantes."
    )
    p_prob2 = (
        "<b>2. Cabeca congelada (colapso MSE):</b> Treinar redes neurais com erro medio quadratico tradicional faz o avatar paralisar "
        "a cabeca. Superamos esse problema com difusao estocastica (MDM), mantendo micro-movimentos organicos continuos."
    )
    p_prob3 = (
        "<b>3. Avatar passivo que nao reage ao interlocutor:</b> Adotamos a dinamica diadica do Audio2Photoreal da Meta. Durante a fala "
        "do usuario, o avatar assume o papel de ouvinte, selando a boca e balancando a cabeca afirmativamente (head nods) em escuta ativa."
    )
    p_prob4 = (
        "<b>4. Olhar fixo de teleprompter:</b> Implementamos o Gaze Aversion inspirado no Omnihuman da ByteDance, no qual o avatar desvia "
        "a cabeca e os olhos para pensar antes de responder perguntas, simulando deliberacao cognitiva humana."
    )
    story.append(Paragraph(p_prob1, style_body))
    story.append(Paragraph(p_prob2, style_body))
    story.append(Paragraph(p_prob3, style_body))
    story.append(Paragraph(p_prob4, style_body))
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------------------
    # 3. O QUE CADA MODELO ADICIONA (VISAO RAPIDA)
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. O Que Cada Modelo Agrega na Pratica", style_h1))
    
    mods_texto = [
        ("• VASA-1 (Microsoft, 2024):", "Sintese holistica livre direto do som. Serve de baseline puro sem intervencoes manuais."),
        ("• AUHead (ICLR 2026):", "Controle de musculos faciais isolados via FACS de Paul Ekman. Permite franzir a testa em foco (AU04) ou abrir um grande sorriso genuino (AU12 e AU06)."),
        ("• InstructAvatar (AAAI 2025):", "Direcao cenica em texto livre (postura altiva, queixo elevado) com fechamento labial automatico durante pausas."),
        ("• Audio2Photoreal (Meta, CVPR 2024):", "Dinamica de conversa real entre duas pessoas: o avatar escuta ativamente com acenos harmonicos de cabeca e boca 100% selada."),
        ("• OmniHuman-1.5 (ByteDance, 2025):", "Arquitetura de Dois Sistemas: fonacao rapida somada a mente deliberativa que desvia o olhar (Gaze Aversion) para refletir."),
        ("• Motion Diffusion Model (MDM, ICLR 2023):", "Amostragem estocastica livre que quebra a rigidez da pose media, garantindo movimentacao natural contínua."),
    ]
    for prefix, desc in mods_texto:
        story.append(Paragraph(f"<b>{prefix}</b> {desc}", style_body))

    # Forca quebra para a pagina 2 comecar exatamente no comparativo
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 4. A PROVA DE FOGO (COMPARATIVO UNIFICADO)
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. O Experimento Mestre: A Prova de Fogo (Grade 2x3)", style_h1))
    story.append(Paragraph(
        "Colocamos os 6 modelos lado a lado com a mesma entrada (audio de 9.69 segundos com fala analitica, uma pausa critica "
        "de 2.2 segundos em silencio absoluto, e um climax oratorio final). A comparacao evidenciou com clareza visual o que cada modelo melhora:",
        style_body
    ))
    story.append(Spacer(1, 4))

    # Tabela comparativa clean
    tbl_data = [
        [
            Paragraph("<b>Modelo</b>", style_tbl_header),
            Paragraph("<b>Fase 1: Fala Inicial</b>", style_tbl_header),
            Paragraph("<b>Fase 2: Silencio de 2.2s</b>", style_tbl_header),
            Paragraph("<b>Fase 3: Climax</b>", style_tbl_header),
            Paragraph("<b>Diferencial Observado</b>", style_tbl_header),
        ],
        [
            Paragraph("<b>VASA-1</b>", style_tbl_cell_bold),
            Paragraph("Fala neutra direta.", style_tbl_cell),
            Paragraph("Boca semi-aberta passiva (sem VAD).", style_tbl_cell),
            Paragraph("Fala comum sem intencao.", style_tbl_cell),
            Paragraph("Baseline puro de comparacao.", style_tbl_cell),
        ],
        [
            Paragraph("<b>AUHead</b>", style_tbl_cell_bold),
            Paragraph("Cenho franzido evidente (AU04).", style_tbl_cell),
            Paragraph("Relaxamento muscular gradual.", style_tbl_cell),
            Paragraph("Grande sorriso Duchenne (AU12).", style_tbl_cell),
            Paragraph("Expressividade muscular cirurgica.", style_tbl_cell),
        ],
        [
            Paragraph("<b>InstructAvatar</b>", style_tbl_cell_bold),
            Paragraph("Postura ereta (Pitch -4.5 deg).", style_tbl_cell),
            Paragraph("Labios 100% selados (vad=0).", style_tbl_cell),
            Paragraph("Queixo erguido e oratoria firme.", style_tbl_cell),
            Paragraph("Presenca cenica e boca fechada.", style_tbl_cell),
        ],
        [
            Paragraph("<b>Audio2Photoreal</b>", style_tbl_cell_bold),
            Paragraph("Turno de fala normal.", style_tbl_cell),
            Paragraph("2 Acenos claros (+5.5 deg) e boca selada.", style_tbl_cell),
            Paragraph("Retomada suave de conversa.", style_tbl_cell),
            Paragraph("Escuta ativa (concorda acenando).", style_tbl_cell),
        ],
        [
            Paragraph("<b>OmniHuman-1.5</b>", style_tbl_cell_bold),
            Paragraph("Foco compenetrado inicial.", style_tbl_cell),
            Paragraph("Gaze Aversion: vira o rosto (-9 deg).", style_tbl_cell),
            Paragraph("Foco direto frontal e queixo alto.", style_tbl_cell),
            Paragraph("Desvia o olhar para pensar.", style_tbl_cell),
        ],
        [
            Paragraph("<b>Motion Diffusion</b>", style_tbl_cell_bold),
            Paragraph("Cinematica estocastica viva.", style_tbl_cell),
            Paragraph("Dinamica postural organica continua.", style_tbl_cell),
            Paragraph("Rica amplitude angular tridimensional.", style_tbl_cell),
            Paragraph("Elimina a cabeca congelada/rigida.", style_tbl_cell),
        ],
    ]

    tbl_comp = Table(tbl_data, colWidths=[24 * mm, 34 * mm, 44 * mm, 36 * mm, 36 * mm])
    tbl_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
    ]))
    story.append(tbl_comp)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 5. O QUE LEVAR PARA A REUNIAO / DECISAO DE PRODUTO
    # -------------------------------------------------------------------------
    story.append(KeepTogether([
        Paragraph("5. Recomendacoes Diretas para Decisao de Produto", style_h1),
        Paragraph(
            "Se fossemos escolher a receita ideal para colocar um avatar em producao hoje:",
            style_body
        ),
        Paragraph(
            "<b>1. Camada VAD Obrigatoria:</b> Qualquer solucao comercial de audio para movimento precisa de um modulo de "
            "Voice Activity Detection. Se o som parou, o deslocamento dos labios deve ser zerado (vad_alpha = 0.0). Isso resolve "
            "completamente o vício visual de boca entreaberta ou dentes aparentes.",
            style_body
        ),
        Paragraph(
            "<b>2. Para Assistentes e Atendimento Interativo:</b> Adotar a combinacao de Audio2Photoreal com InstructAvatar. "
            "O avatar escuta o interlocutor acenando a cabeca afirmativamente e mantem os labios fechados, gerando sensacao imediata de atencao.",
            style_body
        ),
        Paragraph(
            "<b>3. Para Videoaulas e Apresentacoes Longas:</b> Utilizar a arquitetura cognitiva do Omnihuman com AUHead. "
            "O desvio reflexivo de olhar (Gaze Aversion) antes de responder e os sorrisos em momentos-chave removem a impressao de robo lendo texto.",
            style_body
        ),
        Paragraph(
            "<b>4. Custo e Latencia:</b> O pipeline opera em tempo real na etapa de keypoints e levou cerca de 4 minutos para renderizar "
            "10 segundos de video full-HD em hardware Apple Silicon com GPU MPS. E perfeitamente viavel tanto para pre-gravacao quanto para servidores CUDA.",
            style_body
        ),
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=5),
        Paragraph("<b>Relatorio de Pesquisa Trilha D</b> — Cleiver Junior | Experimentos Avatar 01 Humans", style_body),
        Paragraph("Codigos, videos e demonstracoes: github.com/CleiverJr/Experimentos-Avatar-01-Humans", style_body)
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Relatorio PDF clean gerado com sucesso em: {caminho_pdf}")


if __name__ == "__main__":
    dir_imp = os.path.dirname(os.path.abspath(__file__))
    caminho_saida = os.path.join(dir_imp, "relatorio_experimentos_avatar.pdf")
    gerar_relatorio_pdf(caminho_saida)
