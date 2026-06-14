---
title: "波は、運動方程式から生まれる ── ばね玉の鎖と、分野の境目"
description: "力学と波動は、別々の分野に見えて、実はひとつ。玉をばねで繋いだ鎖の一個一個に F=ma を立てるだけで、ぽろっと波動方程式が出てくる。離散の運動方程式が連続の波になる瞬間を、弾ける鎖で確かめる。"
pubDate: 2026-06-13
tags: ["力学", "波動", "運動方程式", "連続体"]
demo: "/chain/"
demoLabel: "ばね玉の鎖を全画面で開く"
series: "conservation"
order: 1
---

物理を習うと、力学・波動・電磁気・熱…と、分野ごとに章が分かれている。あの分け方は、教えやすさのための **縫い目** だと思う。便利だし、理由も分かる。でも時々、その縫い目を一本ほどいて「ほんとうは地続きだ」と確かめると、すごく気持ちがいい。

この回はそれをやる。これまで [力学](/docs/work-energy/) と [波動](/docs/waves-formants/) を別々に積んできたけれど ── **波は、いちばん素朴な力学（$F=ma$）から、勝手に生まれてくる**。その瞬間を見よう。

## ① ばね玉の鎖に、ただ $F=ma$ を立てる

舞台は単純だ。同じ質量 $m$ の玉を横一列に並べ、隣どうしを同じばね（ばね定数 $k$）で繋ぐ。両端は壁に固定。各玉は、真上・真下（横向きのずれ $y$）にだけ動けるとする。

$n$ 番目の玉に働く力を考える。右の隣 $y_{n+1}$ との段差で $k(y_{n+1}-y_n)$ だけ引かれ、左の隣 $y_{n-1}$ との段差で $k(y_n-y_{n-1})$ だけ引き戻される。足すと、その玉の運動方程式は

$$m\,\ddot{y}_n = k(y_{n+1}-y_n) - k(y_n-y_{n-1}) = k\,(y_{n+1} - 2y_n + y_{n-1})$$

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 480 200" width="480" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <line x1="95" y1="148" x2="385" y2="140" stroke="#cfc9be" stroke-width="1.2" stroke-dasharray="4 3"/>
  <line x1="95" y1="148" x2="240" y2="86" stroke="#3c7876" stroke-width="2"/>
  <line x1="240" y1="86" x2="385" y2="140" stroke="#3c7876" stroke-width="2"/>
  <line x1="240" y1="86" x2="240" y2="144" stroke="#c2543d" stroke-width="1" stroke-dasharray="3 2"/>
  <circle cx="240" cy="144" r="2.5" fill="#cfc9be"/>
  <line x1="240" y1="92" x2="240" y2="122" stroke="#c2543d" stroke-width="2.6"/>
  <polygon points="240,130 235,120 245,120" fill="#c2543d"/>
  <circle cx="95" cy="148" r="6" fill="#3c7876"/>
  <circle cx="240" cy="86" r="7" fill="#1d1b17"/>
  <circle cx="385" cy="140" r="6" fill="#3c7876"/>
  <text x="95" y="170" font-size="12" fill="#1d1b17" text-anchor="middle">yₙ₋₁</text>
  <text x="240" y="74" font-size="12.5" font-weight="700" fill="#1d1b17" text-anchor="middle">yₙ</text>
  <text x="385" y="162" font-size="12" fill="#1d1b17" text-anchor="middle">yₙ₊₁</text>
  <text x="118" y="104" font-size="9.5" fill="#3c7876">k(yₙ−yₙ₋₁)</text>
  <text x="298" y="104" font-size="9.5" fill="#3c7876">k(yₙ₊₁−yₙ)</text>
  <text x="256" y="118" font-size="10" fill="#c2543d">引き戻し</text>
  <text x="248" y="160" font-size="9.5" fill="#7d7568">← 隣の平均</text>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">玉 n が左右の隣を結ぶ線（＝隣の平均）からはみ出すほど、平均へ引き戻される。正味の力 ＝ k(yₙ₊₁−2yₙ+yₙ₋₁)。</figcaption>
</figure>

それだけ。特別なことは何もない、ただの $F=ma$ を玉の数だけ並べただけだ。右辺の $y_{n+1}-2y_n+y_{n-1}$ は「自分が、左右の平均からどれだけ出っ張っているか」を測っている。出っ張っていれば引き戻される ── ごく素朴な話。

下で「弾く」を押すと、真ん中の玉をつまんで離す。あとは各玉が上の式に従うだけ。なのに、**全体としては波が左右に走って、壁で跳ね返る**。誰も「波になれ」とは言っていないのに、$F=ma$ の集まりが勝手に波として振る舞う。

<div class="demo-embed">
  <iframe src="/chain/" title="ばね玉の鎖" loading="lazy"></iframe>
  <div class="cap"><span>chain</span><a href="/chain/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

## ② 玉を増やすと、波動方程式が出てくる

なぜ波になるのか。玉の間隔を $a$ として、$n$ 番目の玉の位置を $x = na$ とみなそう。さっきの右辺 $y_{n+1}-2y_n+y_{n-1}$ は、数値計算でおなじみの **二階微分の近似** そのものだ：

$$y_{n+1} - 2y_n + y_{n-1} \;\approx\; a^2\,\frac{\partial^2 y}{\partial x^2}$$

これを運動方程式に入れると、

$$m\,\ddot{y} = k\,a^2\,\frac{\partial^2 y}{\partial x^2} \quad\Longrightarrow\quad \frac{\partial^2 y}{\partial t^2} = \frac{k a^2}{m}\,\frac{\partial^2 y}{\partial x^2}$$

玉を細かくしていく（$N\to\infty$、$a\to0$）と、つぶつぶの鎖は **なめらかな1本のひも** になり、この式が残る。これは ── 前にやった [波動方程式](/docs/formant-transfer-matrix/) と、まったく同じ形だ：

$$\frac{\partial^2 y}{\partial t^2} = c^2\,\frac{\partial^2 y}{\partial x^2}, \qquad c = a\sqrt{\frac{k}{m}}$$

$c$ が波の速さ。張った弦で言えば $c=\sqrt{T/\mu}$（$T$ は張力、$\mu$ は線密度）── 同じ形だ。**「波動」という分野は、ばねと玉という純・力学から、二階微分を一つ経由しただけで出てきた**。鎖の遊び場で $N$ を増やすほど、つぶつぶの跳ね返りがなめらかな波に近づくのは、この極限を目で見ているんだよ。

<figure style="margin:1.6rem 0;text-align:center;">
  <img src="/docs/discrete-to-continuous.svg" alt="玉を細かくすると、とびとびの鎖がなめらかなひもになる" style="max-width:100%;border-radius:10px;border:1px solid #e3dbd0;" />
  <figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">玉を細かくしていくと、とびとびの鎖がなめらかなひもに ── 離散の「差」（$y_{n+1}-2y_n+y_{n-1}$）が、連続の「微分」（$\partial^2 y/\partial x^2$）に化ける。畳み込みの「和→積分」と、同じ“刻み→0”の手だよ。</figcaption>
</figure>

## ③ 鎖の固有の揺れ ＝ あの定在波

もう一つ、繋がる所がある。鎖を「弾く」のではなく、特別な形に整えて離すと、**形を保ったまま、その場で上下に揺れるだけ** の運動になる。これが鎖の **基準振動（ノーマルモード）**。遊び場の「基準モード 1／2／3」がそれだ。

$N$ 個の玉・両端固定だと、基準モードの形はきれいに決まっていて、第 $j$ モードは

$$y_n^{(j)} = \sin\!\frac{j\pi n}{N+1}$$

これ、見覚えがあるはず ── [前編の定在波](/docs/waves-formants/) で出てきた $\sin(kx)$ の並びと同じだ。第1モードは腹が1つ、第2モードは2つ、第3モードは3つ。固定端が節になり、半波長おきに腹が並ぶ。**鎖の「固有の揺れ」と、波動の「定在波」は、同じものだった**。

おまけに、その揺れの速さ（角振動数）は

$$\omega_j = 2\sqrt{\frac{k}{m}}\;\left|\sin\!\frac{j\pi}{2(N+1)}\right|$$

で決まる。長い波（$j$ が小さい）では $\sin\theta\approx\theta$ なので $\omega_j \approx \sqrt{k/m}\cdot\frac{j\pi}{N+1}$ ── ちょうど理想のひもの $\omega_j = j\pi c/L$ に一致する。短い波になるとこの近似がずれていく（これを **分散** と呼ぶ）。「つぶつぶの鎖」と「なめらかなひも」の違いは、まさにここに出る。素朴なモデルが、ちゃんと自分の限界まで教えてくれるのが面白い所だね。

## ④ 縫い目は、地続きのしるし

ここまでで、力学（$F=ma$）と波動（波動方程式）のあいだの縫い目を一本ほどいた。底ではひとつだった。

そして、同じ波動方程式は、他の分野にも顔を出す。

- **音**：空気の圧力を、前の [声道の話](/docs/formant-transfer-matrix/) でやったとおり、同じ $\partial_t^2 p = c^2\,\partial_x^2 p$ で動く。
- **光・電磁波**：マクスウェルの方程式を整理すると、電場・磁場が同じ波動方程式に従う。光は電磁場の波。
- **量子**：シュレーディンガー方程式も「波」の式で、粒子が波として広がる。

形が同じなら、起きることも同じ ── 進む波、定在波、共鳴、反射。だから一度どこかで波を掴むと、別の分野の波も「あ、これ知ってる」になる。分野の壁は、越えられない壁じゃなくて、**地続きであることのしるし**みたいなものだと、私は思う。

## まとめ

- 玉をばねで繋いだ鎖の各玉に、ただ $F=ma$ を立てる：$m\ddot{y}_n = k(y_{n+1}-2y_n+y_{n-1})$。
- 玉を細かくする（$N\to\infty$）と、右辺が二階微分になり、**波動方程式 $\ddot{y}=c^2 y''$** が出てくる。波は力学から生まれる。
- 鎖の **基準モード** $\sin\!\frac{j\pi n}{N+1}$ は、波動の **定在波** そのもの。長波長では理想のひもに一致し、短波長でずれる（分散）。
- 同じ波動方程式は、弦・音・光・量子に共通。分野の縫い目は、底が地続きだから引けるんだ。

[力学のページ](/docs/work-energy/) と [波動のページ](/docs/waves-formants/)、別々に読んできた2本が、ここで1本に繋がった。物理が分野に分かれているのは便利のためで、奥はちゃんと一つ ── そう思えると、章の切れ目が少し心地よくなると思う。
