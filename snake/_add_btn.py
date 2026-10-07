# -*- coding: utf-8 -*-
f = r'D:\OCgame\snake\index.html'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

old = '''  <div class="overlay hidden" id="ov-pause">
    <p class="ov-title">已暂停</p>
    <div class="btn-row">
      <button class="btn" id="btn-resume">继续</button>
      <button class="btn ghost" id="btn-restart-p">重新开始</button>
    </div>
  </div>'''

new = '''  <div class="overlay hidden" id="ov-pause">
    <p class="ov-title">已暂停</p>
    <button class="btn" id="btn-resume">继续</button>
    <button class="btn ghost" id="btn-ai-p">AI 演示</button>
    <button class="btn ghost" id="btn-restart-p">重新开始</button>
  </div>'''

c = c.replace(old, new)

# Add click handler
old2 = "document.getElementById('btn-restart-p').addEventListener('click',startGame);"
new2 = old2 + "\ndocument.getElementById('btn-ai-p').addEventListener('click',startAI);"
c = c.replace(old2, new2)

with open(f, 'w', encoding='utf-8', newline='') as fh:
    fh.write(c)

print('OK' if 'btn-ai-p' in c else 'FAIL')
