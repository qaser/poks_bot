from math import ceil

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

from config.mongo_config import petitions
import utils.constants as const


def set_cell_color(cell, color):
    cell_xml_element = cell._tc
    table_cell_properties = cell_xml_element.get_or_add_tcPr()
    shade_obj = OxmlElement('w:shd')
    shade_obj.set(qn('w:fill'), color)
    table_cell_properties.append(shade_obj)


def create_docx_file():
    DOC_HEADER = 'Отчет по проблемным вопросам филиалов по направлению ПОпоЭКС'
    TABLE_HEADERS = (
        '№ п/п',
        'Направление',
        'Дата',
        'Содержание вопроса',
        'Решено',
    )
    document = Document()
    section = document.sections[0]
    # левое поле в миллиметрах
    section.left_margin = Mm(25)
    # правое поле в миллиметрах
    section.right_margin = Mm(15)
    # верхнее поле в миллиметрах
    section.top_margin = Mm(15)
    # нижнее поле в миллиметрах
    section.bottom_margin = Mm(15)

    style = document.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    header = document.add_paragraph(DOC_HEADER)
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.style = document.styles['Normal']

    table = document.add_table(rows=2, cols=5, style='Table Grid')
    table_hdr = table.rows[0].cells  # заголовки таблицы
    table_num = table.rows[1].cells  # нумерация таблицы
    table.columns[0].width = Mm(10)
    table.columns[1].width = Mm(35)
    table.columns[2].width = Mm(25)
    table.columns[3].width = Mm(88)
    table.columns[4].width = Mm(20)

    for id, cell in enumerate(table_hdr):
        cell.text = TABLE_HEADERS[id]
        table_num[id].text = str(id + 1)

    # table_hdr[4].merge(table_hdr[5])

    current_rows = 2  # текущее количество строк в таблице
    for ks in const.KS:
        ks_row = table.add_row().cells
        for cell_id in range(0, 3):
            table.rows[current_rows].cells[cell_id].merge(table.rows[current_rows].cells[cell_id])
        queryset = list(petitions.find({'ks': ks, 'done': 'false'}))
        num_petitions = len(queryset)
        for num, pet in enumerate(queryset):
            res = 'Да' if pet.get('done') == 'true' else 'Нет'
            main_row = table.add_row().cells
            main_row[0].text = str(num + 1)
            main_row[1].text = const.DIRECTIONS_CODES[pet.get('direction')]
            main_row[2].text = pet.get('date')
            main_row[3].text = pet.get('text')
            main_row[4].text = res
        current_rows += num_petitions

    # for num, q_id in enumerate(questions_list):
    #     q = questions.find_one({'_id': q_id})
    #     num_answers = q.get('num_answers')
    #     main_row = table.add_row().cells
    #     main_row[0].text = str(num + 1)
    #     main_row[1].text = themes.find_one({'code': q.get('theme')}).get('name')
    #     main_row[2].text = str(num + 1)
    #     main_row[3].text = q.get('question')
    #     main_row[4].text = '1'
    #     main_row[5].text = q.get('answers')[0]
    #     for i in range(1, num_answers):
    #         row_ans = table.add_row().cells
    #         row_ans[-2].text = str(i + 1)
    #         row_ans[-1].text = q.get('answers')[i]
    #     for row_id in range(current_rows, current_rows + num_answers - 1):
    #         for cell_id in range(0, 4):
    #             table.rows[row_id].cells[cell_id].merge(table.rows[row_id+1].cells[cell_id])
    #     current_rows += num_answers

    path = f'static/docs_email/Сводный перечень вопросов.docx'
    document.save(path)


# def create_results_docx_file(year, quarter, test_type, department, results_set):
#     DOC_HEADER = (
#         f'Результаты тестирования {test_type} контроля знаний по технической учебе\n'
#         f'за {quarter} квартал {year} года'
#     )
#     TABLE_HEADERS = ('№ вопроса', 'Вариант ответа')
#     document = Document()
#     section = document.sections[0]
#     section.left_margin = Mm(25)
#     section.right_margin = Mm(15)
#     section.top_margin = Mm(15)
#     section.bottom_margin = Mm(15)

#     style = document.styles['Normal']
#     font = style.font
#     font.name = 'Times New Roman'
#     font.size = Pt(12)

#     for res in results_set:
#         results = res.get('quiz_results')
#         username = users.find_one({'user_id': res.get('user_id')}).get('full_name')
#         grade = res.get('grade')

#         len_test = len(results)
#         num_rows = ceil(len_test / 10) * 2
#         header = document.add_paragraph(DOC_HEADER)
#         header.alignment = WD_ALIGN_PARAGRAPH.CENTER
#         header.style = document.styles['Normal']

#         table = document.add_table(rows=num_rows, cols=11, style='Table Grid')
#         table.columns[0].width = Mm(25)
#         for c in range(1, 11):
#             table.columns[c].width = Mm(15)

#         table_hdr = table.columns[0].cells
#         for id, cell in enumerate(table_hdr):
#             cell_id = id % 2  # определение нечётных полей
#             cell.text = TABLE_HEADERS[cell_id]
#             cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

#         for id, data in enumerate(results):
#             _, _, ans, correct = data
#             row_id = (id // 10) * 2
#             cell_id = int(str(id)[-1])
#             cell_hdr = table.rows[row_id].cells[cell_id+1]
#             cell_value = table.rows[row_id+1].cells[cell_id+1]
#             cell_hdr.text = str(id + 1)
#             cell_hdr.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
#             cell_value.text = str(ans + 1)
#             cell_value.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
#             if correct == 'true':
#                 set_cell_color(cell_value, 'addfad')

#         document.add_paragraph('')
#         document.add_paragraph(f'Тестируемый   ______________   {username}')
#         document.add_paragraph(f'Результат тестирования: {grade}')
#         document.add_paragraph('')
#         document.add_paragraph('')




#         path = f'static/reports/Результаты {test_type} контроля знаний ({quarter} кв. {year}г).docx'
#         document.save(path)
