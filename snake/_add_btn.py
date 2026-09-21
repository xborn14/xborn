f = r'D:\OCgame\snake\index.html'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

old1 = '<button class="btn" id="btn-restart">\u518d\u6765\u4e00\u5c40</button>'
new1 = old1 + '\n    <button class="btn ghost" id="btn-ai-over">AI \u6f14\u793a</button>'
c = c.replace(old1, new1)

old2 = "document.getElementById('btn-ai').addEventListener('click',startAI);"
new2 = old2 + "\ndocument.getElementById('btn-ai-over').addEventListener('click',startAI);"
c = c.replace(old2, new2)

with open(f, 'w', encoding='utf-8', newline='') as fh:
    fh.write(c)

print('OK' if 'btn-ai-over' in c else 'FAIL')
