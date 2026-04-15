"""
将 Markdown 需求文档转换为 PDF 格式
"""

import markdown2
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_pdf_from_markdown():
    """从 Markdown 文件创建 PDF"""
    
    # 读取 Markdown 文件
    with open('scp_prd.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # 转换为 HTML
    html_content = markdown2.markdown(markdown_content, extras=['tables', 'toc', 'fenced-code-blocks'])
    
    # 创建 PDF 文档
    doc = SimpleDocTemplate(
        "scp_prd.pdf",
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # 存储 PDF 内容的列表
    story = []
    
    # 定义样式
    styles = getSampleStyleSheet()
    
    # 添加自定义样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1890ff'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#666666'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#888888'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        fontName='Helvetica',
        leading=14
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#d63384'),
        fontName='Courier',
        backColor=colors.HexColor('#f8f9fa'),
        leftIndent=20,
        rightIndent=20,
        spaceAfter=10,
        spaceBefore=10
    )
    
    # 解析 Markdown 内容并添加到 story
    lines = markdown_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 处理标题
        if line.startswith('# '):
            title = line[2:].strip()
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))
        elif line.startswith('## '):
            heading = line[3:].strip()
            story.append(Paragraph(heading, heading1_style))
            story.append(Spacer(1, 0.15*inch))
        elif line.startswith('### '):
            subheading = line[4:].strip()
            story.append(Paragraph(subheading, heading2_style))
            story.append(Spacer(1, 0.1*inch))
        elif line.startswith('#### '):
            subheading = line[5:].strip()
            story.append(Paragraph(subheading, heading3_style))
            story.append(Spacer(1, 0.05*inch))
        
        # 处理表格
        elif line.startswith('|') and line.endswith('|'):
            table_data = []
            while i < len(lines) and lines[i].strip().startswith('|') and lines[i].strip().endswith('|'):
                row = lines[i].strip()
                cells = [cell.strip() for cell in row.split('|')[1:-1]]
                table_data.append(cells)
                i += 1
            
            if table_data:
                # 创建表格
                table = Table(table_data, colWidths=[2*inch] * len(table_data[0]))
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f2f5')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')])
                ]))
                story.append(table)
                story.append(Spacer(1, 0.15*inch))
            continue
        
        # 处理代码块
        elif line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            
            if code_lines:
                code_text = '\n'.join(code_lines)
                code_para = Paragraph(code_text, code_style)
                story.append(code_para)
                story.append(Spacer(1, 0.1*inch))
        
        # 处理列表项
        elif line.startswith('- '):
            list_item = line[2:].strip()
            bullet = Paragraph(f"• {list_item}", normal_style)
            story.append(bullet)
            story.append(Spacer(1, 0.05*inch))
        
        # 处理普通段落
        elif line and not line.startswith('---'):
            # 移除粗体和斜体标记
            line = line.replace('**', '').replace('*', '')
            para = Paragraph(line, normal_style)
            story.append(para)
            story.append(Spacer(1, 0.05*inch))
        
        # 处理分隔线
        elif line.startswith('---'):
            story.append(PageBreak())
        
        i += 1
    
    # 构建 PDF
    doc.build(story)
    print("✓ PDF 文件已成功生成：scp_prd.pdf")

if __name__ == "__main__":
    create_pdf_from_markdown()
