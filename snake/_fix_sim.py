f = r"D:\OCgame\snake\index.html"
with open(f, "r", encoding="utf-8") as fh:
    content = fh.read()

# Replace flood fill with cycle-walk check
old = """    var nh=sim[0], tail=sim[sim.length-1];
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
    return reachedTail && cnt >= sim.length;"""

new = """    /* 沿环路走到尾巴：身体必须是环路连续段 */
    var tail=sim[sim.length-1];
    var cur=sim[0];
    for(var step=0;step<400;step++){
      var cn=cycle[cur.x+','+cur.y];
      if(!cn) return false;
      if(cn.x===tail.x&&cn.y===tail.y) return true;
      for(var bi=0;bi<sim.length-1;bi++){
        if(sim[bi].x===cn.x&&sim[bi].y===cn.y) return false;
      }
      cur=cn;
    }
    return false;"""

content = content.replace(old, new)
with open(f, "w", encoding="utf-8", newline="") as fh:
    fh.write(content)
print("OK")
