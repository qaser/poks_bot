import os

for _, _, files in os.walk('static/tutorial/'):
        for filename in files:
            file = f'static/tutorial/{filename}'
            print(file)
