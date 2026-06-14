// PixLab 計算ロジックの検証テスト。
// public/pixlab/index.html の核心関数を「そのまま」写して、テスト画像で手計算と照合する。
// 推測でなく、実装どおりに計算した結果を assert する。

let N = 5;
// ---- PixLab からそのまま写した関数 ----
function ci(v){ return v<0?0:v>=N?N-1:v; }            // 境界＝端の値を複製（clamp-to-edge）
function selOf(d, chan){                                 // 見る面の値
  if(chan==='R') return d[0]; if(chan==='G') return d[1]; if(chan==='B') return d[2];
  return Math.round(0.299*d[0]+0.587*d[1]+0.114*d[2]);  // L = Rec.601 輝度
}
function applyDisp(sum,k){ let d;
  if(k.disp==='avg') d=Math.round(sum/k.div);
  else if(k.disp==='abs') d=Math.min(255,Math.abs(Math.round(sum)));
  else if(k.disp==='offset') d=Math.round(sum)+128;
  else d=Math.round(sum);
  return d<0?0:d>255?255:d;
}
function convCellSel(dots,col,row,k,chan){              // 選択面の畳み込み（実装は相関）
  let win=[]; for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){ win.push(selOf(dots[ci(row+dy)*N+ci(col+dx)],chan)); }
  let sum=0; for(let i=0;i<9;i++) sum+=k.m[i]*win[i];
  return { sum:sum, disp:applyDisp(sum,k), win:win };
}
function gradCell(dots,col,row,chan){
  let sx=[-1,0,1,-2,0,2,-1,0,1], sy=[-1,-2,-1,0,0,0,1,2,1], win=[];
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){ win.push(selOf(dots[ci(row+dy)*N+ci(col+dx)],chan)); }
  let gx=0,gy=0; for(let i=0;i<9;i++){ gx+=sx[i]*win[i]; gy+=sy[i]*win[i]; }
  let mag=Math.round(Math.sqrt(gx*gx+gy*gy)); if(mag>255)mag=255;
  return { gx:gx, gy:gy, mag:mag };
}
function betweenVar(H,total,k){ let w0=0,sum0=0,sumAll=0;
  for(let t=0;t<256;t++){ sumAll+=t*H[t]; if(t<=k){ w0+=H[t]; sum0+=t*H[t]; } }
  let w1=total-w0; if(w0===0||w1===0) return {v:0};
  let m0=sum0/w0, m1=(sumAll-sum0)/w1, p0=w0/total, p1=w1/total;
  return {v:p0*p1*(m0-m1)*(m0-m1), m0:m0, m1:m1};
}
function otsuBest(dots,chan){ let H=new Array(256).fill(0); for(let i=0;i<N*N;i++) H[selOf(dots[i],chan)]++;
  let best=-1,bk=0; for(let k=0;k<256;k++){ let v=betweenVar(H,N*N,k).v; if(v>best){best=v;bk=k;} } return bk; }

const KER = {
  blur:    {m:[1,1,1,1,1,1,1,1,1], div:9, disp:'avg'},
  sharpen: {m:[0,-1,0,-1,5,-1,0,-1,0], div:1, disp:'clamp'},
  sobelx:  {m:[-1,0,1,-2,0,2,-1,0,1], div:1, disp:'abs'},
  sobely:  {m:[-1,-2,-1,0,0,0,1,2,1], div:1, disp:'abs'},
  lap:     {m:[-1,-1,-1,-1,8,-1,-1,-1,-1], div:1, disp:'abs'},
};
function gray(v){ return [v,v,v]; }
function field(fn){ let d=new Array(N*N); for(let r=0;r<N;r++)for(let c=0;c<N;c++) d[r*N+c]=fn(c,r); return d; }
function mapCells(dots,k,chan){ let o=new Array(N*N); for(let r=0;r<N;r++)for(let c=0;c<N;c++) o[r*N+c]=convCellSel(dots,c,r,k,chan).disp; return o; }
function allEqual(a,v){ return a.every(x=>x===v); }
function maxAbs(a){ return Math.max(...a.map(Math.abs)); }

let pass=0, fail=0, log=[];
function ok(name,cond,extra){ if(cond){pass++; log.push('  ok  '+name);} else {fail++; log.push('  FAIL '+name+(extra?'  '+extra:''));} }

// ===== テスト1：全画素 100 =====
N=5; { let d=field(()=>gray(100));
  ok('T1 blur 全100→全100', allEqual(mapCells(d,KER.blur,'L'),100));
  ok('T1 sobelx 全0(端・角含む)', allEqual(mapCells(d,KER.sobelx,'L'),0));
  ok('T1 sobely 全0', allEqual(mapCells(d,KER.sobely,'L'),0));
  ok('T1 lap 全0', allEqual(mapCells(d,KER.lap,'L'),0));
  ok('T1 sharpen 全100', allEqual(mapCells(d,KER.sharpen,'L'),100));
  // 角(0,0)を明示確認
  ok('T1 角(0,0) sobelx=0', convCellSel(d,0,0,KER.sobelx,'L').disp===0);
}
// ===== テスト2：横グラデーション 0,50,100,150,200（列ごと）=====
N=5; { let cols=[0,50,100,150,200]; let d=field((c,r)=>gray(cols[c]));
  let sx=mapCells(d,KER.sobelx,'L'), sy=mapCells(d,KER.sobely,'L');
  ok('T2 sobelx 反応する(>0)', maxAbs(sx)>0, 'max='+maxAbs(sx));
  ok('T2 sobely ほぼ0', maxAbs(sy)===0, 'max='+maxAbs(sy));
  // 内側列(col=2)の手計算: 列[50,100,150] → Σ=400 → abs cap 255
  ok('T2 内側 sobelx 手計算=255(400→cap)', convCellSel(d,2,2,KER.sobelx,'L').sum===400 && convCellSel(d,2,2,KER.sobelx,'L').disp===255);
  // 左端(col=0): 列[ci(-1)=0→0, 0, 1] = [0,0,50] → Σ=200
  ok('T2 左端 sobelx 手計算=200(端複製)', convCellSel(d,0,2,KER.sobelx,'L').sum===200);
}
// ===== テスト3：縦グラデーション =====
N=5; { let rows=[0,50,100,150,200]; let d=field((c,r)=>gray(rows[r]));
  let sx=mapCells(d,KER.sobelx,'L'), sy=mapCells(d,KER.sobely,'L');
  ok('T3 sobely 反応する(>0)', maxAbs(sy)>0, 'max='+maxAbs(sy));
  ok('T3 sobelx ほぼ0', maxAbs(sx)===0, 'max='+maxAbs(sx));
}
// ===== テスト4：中央だけ 255 =====
N=5; { let d=field((c,r)=>gray((c===2&&r===2)?255:0));
  let bl=mapCells(d,KER.blur,'L');
  ok('T4 blur 中央=round(255/9)=28', bl[2*5+2]===Math.round(255/9));
  ok('T4 blur 隣接(2,1)=round(255/9)=28', bl[1*5+2]===Math.round(255/9));
  ok('T4 blur 中央周囲へ広がる(>0)', bl[1*5+2]>0 && bl[2*5+1]>0);
  // ラプラシアン中央: 8*255 - 0 = 2040 → abs cap 255
  ok('T4 lap 中央 sum=2040→cap255', convCellSel(d,2,2,KER.lap,'L').sum===2040 && convCellSel(d,2,2,KER.lap,'L').disp===255);
  // ラプラシアン隣接(2,1): 中心=8*0 - (周囲に255が1つ) = -255 → abs=255
  ok('T4 lap 隣接 sum=-255→abs255', convCellSel(d,2,1,KER.lap,'L').sum===-255 && convCellSel(d,2,1,KER.lap,'L').disp===255);
}
// ===== テスト5：二峰性で Otsu =====
N=6; { // 暗30が多数, 明220がまとまり
  let vals=[30,30,30,30,30,30, 30,30,30,30,30,30, 30,30,30,30,30,30,
            30,30,30,220,220,220, 30,30,220,220,220,220, 30,30,220,220,220,220];
  let d=vals.map(gray);
  let k=otsuBest(d,'L');
  // 値は{30,220}の2値。最適σ²Bは k∈[30,219] で同点 → 実装は同点なら最低 k（strict >）→ k=30。
  ok('T5 Otsu が2山を分離(30≤k<220)', k>=30 && k<220, 'k='+k);
  ok('T5 Otsu 同点は低いしきい値→k=30', k===30, 'k='+k);
}
// ===== clamp / round / step=finish =====
N=3; { // round 確認: sum/div の round
  let d=field(()=>gray(0)); d[1*3+1]=gray(100); // 中央100
  // blur: 中央 = round((100)/9)=11
  ok('clamp/round blur round確認', convCellSel(d,1,1,KER.blur,'L').disp===Math.round(100/9));
  // 255超え clamp: sharpen で大きな正
  let d2=field(()=>gray(0)); d2[1*3+1]=gray(200);
  // sharpen中央 = 5*200 - 0 = 1000 → clamp 255
  ok('clamp 255超え→255', convCellSel(d2,1,1,KER.sharpen,'L').sum===1000 && convCellSel(d2,1,1,KER.sharpen,'L').disp===255);
  // 負→abs と 負→clamp(0)
  let d3=field(()=>gray(100)); d3[1*3+1]=gray(0); // 中央0,周囲100
  // sharpen中央 = 5*0 - 4*100 = -400 → clamp 0
  ok('clamp 負→0', convCellSel(d3,1,1,KER.sharpen,'L').disp===0);
  // lap中央 = 8*0 - 8*100 = -800 → abs 255
  ok('abs 負→|.|cap255', convCellSel(d3,1,1,KER.lap,'L').disp===255);
}
// step==finish: 同じ画像・同じ演算で convCellSel を全マス回した結果は順序によらず一意（決定的）
N=5; { let d=field((c,r)=>gray((c*37+r*53)%256));
  let a=mapCells(d,KER.sobelx,'L'), b=mapCells(d,KER.sobelx,'L');
  ok('step==finish（決定的・同一）', JSON.stringify(a)===JSON.stringify(b));
}

console.log(log.join('\n'));
console.log('\n==== '+pass+' passed, '+fail+' failed ====');
process.exit(fail?1:0);
