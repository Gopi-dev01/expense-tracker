import glob

target = '<meta charset="UTF-8">'
replacement = '<meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'

for filepath in glob.glob('d:/Gopi_Clg/expense_tracker/templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if target in content and 'name="viewport"' not in content:
        content = content.replace(target, replacement)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {filepath}')
