with open('run_cypher_http.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('r[0]:<18', 'str(r[0]):<18')
text = text.replace('r[1]:<35', 'str(r[1]):<35')
text = text.replace('r[2]:<15', 'str(r[2]):<15')
text = text.replace('r[3]:<20', 'str(r[3]):<20')

with open('run_cypher_http.py', 'w', encoding='utf-8') as f:
    f.write(text)
