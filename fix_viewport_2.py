for filepath in ['d:/Gopi_Clg/expense_tracker/templates/manage_expense.html', 'd:/Gopi_Clg/expense_tracker/templates/expense_report.html']:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'name="viewport"' not in content:
        content = content.replace('<head>', '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {filepath}')
