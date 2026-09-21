# -*- coding: utf-8 -*-
f = r'D:\OCgame\snake\index.html'
with open(f, 'r', encoding='utf-8') as fh:
    lines = fh.readlines()

start = end = None
for i, line in enumerate(lines):
    if 'AI' in line and '自动游玩' in line:
        start = i
    if '输入：键盘' in line:
        end = i
        break

print(f'Start: {start}, End: {end}')

new_ai = """/* ===== AI 自动游玩（BFS 捷径 + 汉密尔顿回路） =====
   蛇身 <=20：BFS 最短路径吃果实（模拟整条路径 + 追尾安全校验）
   蛇身 >20：沿汉密尔顿回路走 */
var aiPath = null;

function aiStep(){
  if(state!=='playing') return;
  var head=snake[0], len=snake.length;
  var ds=[{x:1,y:0},{x:-1,y:0},{x:0,y:1},{x:0,y:-1}];
  function key(x,y){ return x+','+y; }
  function isBlocked(x,y,exTail){
    var n = exTail ? snake.length-1 : snake.length;
    for(var i=0;i<n;i++) if(snake[i].x===x&&snake[i].y===y) return true;
    return false;
  }

  /* 蛇长超过阈值 -> 纯环路 */
  if(len > 20){
    aiPath = null;
    var cn = cycle[head.x+','+head.y];
    if(cn && !isBlocked(cn.x, cn.y, true)){
      setDir({x:cn.x-head.x, y:cn.y-head.y});
      return;
    }
    /* 环路被挡 -> 找空间最大方向 */
    var bestDir=null, bestScore=-1;
    for(var i=0;i<4;i++){
      var nx=head.x+ds[i].x, ny=head.y+ds[i].y;
      if(nx<=0||ny<=0||nx>=COLS-1||ny>=ROWS-1) continue;
      if(isBlocked(nx,ny,true)) continue;
      var seen={}, q=[{x:nx,y:ny}], cnt=0;
      seen[key(nx,ny)]=1;
      while(q.length){
        var c=q.shift(); cnt++;
        for(var j=0;j<4;j++){
          var ex=c.x+ds[j].x, ey=c.y+ds[j].y;
          if(ex<=0||ey<=0||ex>=COLS-1||ey>=ROWS-1) continue;
          if(isBlocked(ex,ey,true)) continue;
          if(seen[key(ex,ey)]) continue;
          seen[key(ex,ey)]=1; q.push({x:ex,y:ey});
        }
      }
      if(cnt>bestScore){ bestScore=cnt; bestDir={x:ds[i].x,y:ds[i].y}; }
    }
    if(bestDir) setDir(bestDir);
    return;
  }

  /* 继续走已规划路径 */
  if(aiPath && aiPath.length > 1){
    var nx=aiPath[1].x, ny=aiPath[1].y;
    if(nx>0&&ny>0&&nx<COLS-1&&ny<ROWS-1 && !isBlocked(nx,ny,true)){
      setDir({x:nx-head.x, y:ny-head.y});
      aiPath.shift();
      return;
    }
    aiPath = null;
  }

  /* BFS 到食物 */
  function bfsPath(){
    if(!food) return null;
    var prev={}, dist={}, q=[head];
    dist[key(head.x,head.y)]=0; prev[key(head.x,head.y)]=null;
    var found=null;
    while(q.length){
      var c=q.shift();
      if(c.x===food.x&&c.y===food.y){ found=c; break; }
      for(var i=0;i<4;i++){
        var nx=c.x+ds[i].x, ny=c.y+ds[i].y;
        if(nx<=0||ny<=0||nx>=COLS-1||ny>=ROWS-1) continue;
        if(isBlocked(nx,ny,false)) continue;
        var k=key(nx,ny);
        if(dist[k]!==undefined) continue;
        dist[k]=dist[key(c.x,c.y)]+1; prev[k]=c; q.push({x:nx,y:ny});
      }
    }
    if(!found) return null;
    var path=[found], cur=found;
    while(prev[key(cur.x,cur.y)]){ cur=prev[key(cur.x,cur.y)]; path.unshift(cur); }
    return path;
  }

  /* 模拟整条路径 + 追尾校验 */
  function simulate(path){
    var sim=[];
    for(var i=0;i<snake.length;i++) sim.push({x:snake[i].x,y:snake[i].y});
    for(var s=1;s<path.length;s++){
      var nx=path[s].x, ny=path[s].y;
      for(var bi=0;bi<sim.length-1;bi++){
        if(sim[bi].x===nx&&sim[bi].y===ny) return false;
      }
      sim.unshift({x:nx,y:ny});
      if(s<path.length-1) sim.pop();
    }
    /* 洪水填充：新蛇头能到尾巴 */
    var nh=sim[0], tail=sim[sim.length-1];
    var seen={}, q2=[nh], cnt=1;
    seen[key(nh.x,nh.y)]=1;
    var reachedTail=false;
    while(q2.length){
      var c=q2.shift();
      if(c.x===tail.x&&c.y===tail.y) reachedTail=true;
      for(var i=0;i<4;i++){
        var nx=c.x+ds[i].x, ny=c.y+ds[i].y;
        if(nx<=0||ny<=0||nx>=COLS-1||ny>=ROWS-1) continue;
        var bl=false;
        for(var bi=0;bi<sim.length-1;bi++) if(sim[bi].x===nx&&sim[bi].y===ny){ bl=true; break; }
        if(bl) continue;
        var k=key(nx,ny);
        if(seen[k]) continue;
        seen[k]=1; cnt++; q2.push({x:nx,y:ny});
      }
    }
    return reachedTail && cnt >= sim.length;
  }

  var path=bfsPath();
  if(path && path.length>1 && simulate(path)){
    aiPath = path;
    setDir({x:path[1].x-head.x, y:path[1].y-head.y});
    aiPath.shift();
    return;
  }
  var cn = cycle[head.x+','+head.y];
  if(cn) setDir({x:cn.x-head.x, y:cn.y-head.y});
}

"""

out = lines[:start] + [new_ai] + lines[end:]
with open(f, 'w', encoding='utf-8', newline='') as fh:
    fh.writelines(out)
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()
print(f'Braces: {c.count("{")}/{c.count("}")}')
print('OK')
