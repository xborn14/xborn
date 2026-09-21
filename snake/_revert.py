f = r"D:\OCgame\snake\index.html"
with open(f, "r", encoding="utf-8") as fh:
    lines = fh.readlines()
start = end = None
for i, line in enumerate(lines):
    if "AI" in line and "自动游玩" in line: start = i
    if "输入：键盘" in line: end = i; break
new_ai = """/* ===== AI 自动游玩（汉密尔顿回路） =====
   预计算遍历全部 400 格的闭合环路，蛇头每步沿环路走一格。
   蛇身始终是环路连续段 → 永不撞墙/撞自己，最终占满全屏。 */
function aiStep(){
  if(state!=='playing') return;
  var h=snake[0];
  var nxt=cycle[h.x+','+h.y];
  if(!nxt) return;
  setDir({x:nxt.x-h.x, y:nxt.y-h.y});
}

"""
out = lines[:start] + [new_ai] + lines[end:]
with open(f, "w", encoding="utf-8", newline="") as fh:
    fh.writelines(out)
print("OK")
