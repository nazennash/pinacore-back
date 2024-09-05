import chardet

with open('data1.json', 'rb') as file:
    result = chardet.detect(file.read())
    print(result)
