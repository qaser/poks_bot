import os

list_file = []
for _, _, files in os.walk('static/tutorial/'):
        for filename in files:
            file = f'static/tutorial/{filename}'
            list_file.append(file)
print(list_file)
file_pdf = open('static/tutorial_pdf/tutorial_pdf.pdf')
print(file_pdf)