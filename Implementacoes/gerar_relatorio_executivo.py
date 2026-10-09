"""
Script Gerador do Relatorio Tecnico Clean (Pesquisa Trilha D)
============================================================
Gera o documento limpo, direto e sem firulas burocraticas para uso em reuniao:
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

        # Cabecalho superior sutil a partir da pagina 2
        if self._pageNumber > 1:
            self.drawString(18 * mm, 287 * mm, "Pesquisa Trilha D: Sintese e Controle de Avatares Neurais")
            self.drawRightString(192 * mm, 287 * mm, "Relatorio para Reuniao Tecnica")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(18 * mm, 284 * mm, 192 * mm, 284 * mm)

        # Rodape discreto
        self.drawString(18 * mm, 12 * mm, "Pesquisa Trilha D | Engenharia e Experimentacao Pratica")
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

    # Estilos limpos e tipografia moderna
    style_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )

    style_sub = ParagraphStyle(
        'MainSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
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

    style_h2 = ParagraphStyle(
        'SecH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=7,
        spaceAfter=2,
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
    # TITULO DIRETO (SEM CABECALHO BUROCRATICO)
    # -------------------------------------------------------------------------
    story.append(Paragraph("Pesquisa Trilha D: Sintese e Controle de Avatares Neurais", style_title))
    story.append(Paragraph("Relatorio Pratico de Engenharia, Mecanismos Comportamentais e Decisoes de Produto", style_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    # -------------------------------------------------------------------------
    # 1. NOTA TECNICA SINCERA: ENGENHARIA REVERSA E EMULACAO PRATICA
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. O Contexto Real: Engenharia Reversa e Emulacao dos Modelos", style_h1))
    
    nota_texto = (
        "<b>Importante esclarecer de imediato:</b> A grande maioria dos modelos de ponta apresentados pela industria "
        "(como o <b>VASA-1</b> da Microsoft, <b>OmniHuman-1.5</b> da ByteDance, <b>Audio2Photoreal</b> da Meta Reality Labs, "
        "<b>InstructAvatar</b> e <b>AUHead</b>) <b>nao possui codigo-fonte nem pesos de rede liberados publicamente</b>. "
        "Sao pesquisas fechadas e proprietarias.<br/><br/>"
        "Por isso, o que construimos aqui e, de forma transparente, uma <b>engenharia pragmatica de alto nivel</b>: "
        "adotamos o motor neural de codigo aberto do <b>LivePortrait / Ditto (ACM MM 2025)</b> como espaco latente e base "
        "anatomica compartilhada (21 keypoints 3D implícitos + rotacao SO(3)), e <b>implementamos diretamente sobre esse motor "
        "os principios matematicos e comportamentais de cada artigo</b>. Isso nos permitiu testar e comparar as ideias "
        "lado a lado sob as mesmas condicoes exatas."
    )
    
    box_data = [[Paragraph(nota_texto, style_note)]]
    box_table = Table(box_data, colWidths=[174 * mm])
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(box_table)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 2. OS 4 PROBLEMAS PRATICOS RESOLVIDOS
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Os 4 Principais Gargalos de Avatares e Como Foram Resolvidos", style_h1))
    p_prob = (
        "Ao implementar e rodar os testes, focamos em resolver os quatro defeitos que mais quebram a sensacao de realismo:<br/>"
        "• <b>1. Boca aberta e dentes expostos no silencio:</b> Modelos tradicionais de audio deixam a boca inerte e entreaberta "
        "quando o som para. Resolvemos isso implementando uma camada de <b>Voice Activity Detection (VAD)</b> que forca "
        "o fechamento labial estrito (vad_alpha = 0.0) na ausencia de voz.<br/>"
        "• <b>2. Cabeca congelada (Colapso MSE):</b> Treinar modelos com erro medio quadratico faz o avatar paralisar a cabeca. "
        "Superamos isso com a <b>Difusao Estocastica (MDM)</b>, que mantem micro-movimentos organicos continuos.<br/>"
        "• <b>3. Avatar passivo que nao reage ao interlocutor:</b> Adotamos a dinamica diadica do <b>Audio2Photoreal (Meta)</b>, "
        "onde o avatar assume o papel de ouvinte, selando a boca e balancando a cabeca afirmativamente (Head Nods) enquanto ouve.<br/>"
        "• <b>4. Olhar fixo de teleprompter:</b> Implementamos o <b>Gaze Aversion do OmniHuman (ByteDance)</b>, no qual o avatar desvia "
        "a cabeca e o olhar para cima/esquerda para 'pensar' antes de responder, simulando deliberacao cognitiva humana."
    )
    story.append(Paragraph(p_prob, style_body))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 3. O QUE CADA MODELO ADICIONA (VISAO RAPIDA)
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. O Que Cada Modelo Agrega na Pratica", style_h1))
    
    mods_texto = [
        ("VASA-1 (Microsoft Research, 2024)", "Sintese holistica livre direto do som. Serve de referencia basal pura (sem controles adicionais)."),
        ("AUHead (ICLR 2026)", "Controle de musculos faciais isolados (FACS). Permite franzir a testa em concentracao (AU04) ou abrir um grande sorriso genuino (AU12 + AU06)."),
        ("InstructAvatar (AAAI 2025)", "Direcao cenica em linguagem natural ('postura altiva, queixo elevado') com fechamento labial automatico em pausas."),
        ("Audio2Photoreal (Meta, CVPR 2024)", "Dialogo entre duas pessoas: o avatar escuta ativamente com acenos harmonicos de cabeca e boca 100% selada."),
        ("OmniHuman-1.5 (ByteDance, 2025)", "Arquitetura de Dois Sistemas: reflexo fonetico rapido + mente deliberativa que desvia o olhar (Gaze Aversion) para refletir."),
        ("Motion Diffusion Model (MDM, ICLR 2023)", "Quebra do colapso da pose media via amostragem estocastica livre, garantindo movimento vivo e solto."),
    ]
    for nome, desc in mods_texto:
        story.append(Paragraph(f"• <b>{nome}:</b> {desc}", style_body))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 4. A PROVA DE FOGO (COMPARATIVO UNIFICADO)
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. O Experimento Mestre: 'A Prova de Fogo' (Grade 2x3)", style_h1))
    story.append(Paragraph(
        "Colocamos os 6 modelos lado a lado com a <b>exata mesma entrada</b> (audio de 9.69s com fala concentrada, "
        "uma pausa critica de 2.2s de silencio absoluto, e um climax oratorio final). "
        "Isso evidenciou com clareza visual o que cada modelo melhora:",
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
            Paragraph("Cenho franzido (AU04=0.85).", style_tbl_cell),
            Paragraph("Relaxamento gradual muscular.", style_tbl_cell),
            Paragraph("Grande sorriso Duchenne (AU12).", style_tbl_cell),
            Paragraph("Expressividade muscular cirurgica.", style_tbl_cell),
        ],
        [
            Paragraph("<b>InstructAvatar</b>", style_tbl_cell_bold),
            Paragraph("Postura ereta (Pitch -4.5 deg).", style_tbl_cell),
            Paragraph("<b>Labios 100% selados (vad=0).</b>", style_tbl_cell),
            Paragraph("Queixo erguido e oratoria firme.", style_tbl_cell),
            Paragraph("Presenca de palco e boca fechada.", style_tbl_cell),
        ],
        [
            Paragraph("<b>Audio2Photoreal</b>", style_tbl_cell_bold),
            Paragraph("Turno de fala normal.", style_tbl_cell),
            Paragraph("<b>2 Acenos claros (+5.5 deg) + boca selada.</b>", style_tbl_cell),
            Paragraph("Retomada suave de conversa.", style_tbl_cell),
            Paragraph("Escuta ativa (concorda acenando).", style_tbl_cell),
        ],
        [
            Paragraph("<b>OmniHuman-1.5</b>", style_tbl_cell_bold),
            Paragraph("Foco compenetrado inicial.", style_tbl_cell),
            Paragraph("<b>Gaze Aversion: vira o rosto (-9 deg).</b>", style_tbl_cell),
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
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
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
            "Se fossemos escolher a 'receita de bolo' ideal para colocar um avatar em producao hoje:",
            style_body
        ),
        Paragraph(
            "<b>1. Camada VAD Obrigatoria:</b> Qualquer motor de fala precisa ter um limitador de VAD (Voice Activity Detection). "
            "Se o usuario parou de falar ou o avatar fez uma pausa, o sistema deve zerar o deslocamento labial (vad_alpha = 0.0). "
            "Isso acaba definitivamente com a impressao de boca aberta ou dentes flutuantes.",
            style_body
        ),
        Paragraph(
            "<b>2. Para Assistentes e Atendimento Interativo:</b> Adotar a dinamica do <b>Audio2Photoreal + InstructAvatar</b>. "
            "O avatar escuta o cliente acenando com a cabeca e mantem os labios fechados. Isso gera empatia imediata.",
            style_body
        ),
        Paragraph(
            "<b>3. Para Aulas e Apresentacoes Longas:</b> Usar a arquitetura cognitiva do <b>OmniHuman-1.5 com AUHead</b>. "
            "O desvio de olhar reflexivo (Gaze Aversion) antes de responder duvidas e os sorrisos em momentos-chave removem a "
            "sensacao de 'robo lendo texto'.",
            style_body
        ),
        Paragraph(
            "<b>4. Viabilidade Tecnica:</b> Todo o pipeline roda em tempo real na etapa de keypoints e levou ~4 minutos para renderizar "
            "10 segundos de video full-HD no chip Apple Silicon via GPU MPS. E perfeitamente escalavel em servidores de producao.",
            style_body
        ),
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=5),
        Paragraph("<b>Relatorio de Pesquisa Trilha D</b> | Cleiver Junior | Experimentos Avatar 01 Humans", style_body),
        Paragraph("Videos, codigos e demonstracoes GIF: github.com/CleiverJr/Experimentos-Avatar-01-Humans", style_body)
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Relatorio PDF clean gerado com sucesso em: {caminho_pdf}")


if __name__ == "__main__":
    dir_imp = os.path.dirname(os.path.abspath(__file__))
    caminho_saida = os.path.join(dir_imp, "relatorio_experimentos_avatar.pdf")
    gerar_relatorio_pdf(caminho_saida)
