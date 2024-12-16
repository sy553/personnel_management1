"""
PDF生成器模块
用于生成各种PDF文档，如工资条等
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

def generate_pdf(salary_record):
    """
    生成工资条PDF
    
    参数:
        salary_record: 工资记录对象
        
    返回:
        生成的PDF文件路径
    """
    try:
        # 创建临时目录用于存储PDF文件
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # 生成PDF文件名
        filename = f'salary_slip_{salary_record.employee.id}_{salary_record.year}{salary_record.month:02d}.pdf'
        filepath = os.path.join(temp_dir, filename)
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # 准备内容
        elements = []
        styles = getSampleStyleSheet()
        
        # 添加标题
        title = Paragraph(
            f'{salary_record.year}年{salary_record.month}月工资条',
            styles['Title']
        )
        elements.append(title)
        
        # 添加基本信息
        employee = salary_record.employee
        basic_info = [
            ['姓名', employee.name],
            ['部门', employee.department.name if employee.department else '未分配'],
            ['职位', employee.position.name if employee.position else '未分配'],
            ['工号', str(employee.id)],
            ['发薪日期', salary_record.payment_date.strftime('%Y-%m-%d')]
        ]
        
        # 添加工资明细
        salary_details = [
            ['项目', '金额（元）'],
            ['基本工资', f'{salary_record.base_salary:.2f}'],
            ['住房补贴', f'{salary_record.housing_allowance:.2f}'],
            ['交通补贴', f'{salary_record.transport_allowance:.2f}'],
            ['餐饮补贴', f'{salary_record.meal_allowance:.2f}'],
            ['加班工资', f'{salary_record.overtime_pay:.2f}'],
            ['奖金', f'{salary_record.bonus:.2f}'],
            ['应发工资', f'{salary_record.gross_salary:.2f}'],
            ['个人所得税', f'{salary_record.tax:.2f}'],
            ['社保扣除', f'{salary_record.social_security:.2f}'],
            ['实发工资', f'{salary_record.net_salary:.2f}']
        ]
        
        # 创建表格
        basic_table = Table(basic_info)
        salary_table = Table(salary_details)
        
        # 设置表格样式
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        
        basic_table.setStyle(table_style)
        salary_table.setStyle(table_style)
        
        # 添加表格到文档
        elements.append(basic_table)
        elements.append(Paragraph('<br/><br/>', styles['Normal']))  # 添加空行
        elements.append(salary_table)
        
        # 生成PDF
        doc.build(elements)
        
        return filepath
        
    except Exception as e:
        print(f'生成PDF失败: {str(e)}')
        return None
