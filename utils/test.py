import os

list_file = []
for _, _, files in os.walk('static/tutorial/'):
        for filename in files:
            file = f'static/tutorial/{filename}'
            list_file.append(file)
print(list_file)