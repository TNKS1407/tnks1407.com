---
title: "ガウスの法則を、道具にする ── 対称性で、場を一発で出す"
description: "場を知るのに、源を一つずつ足すのは骨が折れる。でも電荷に対称性があれば、閉じた面で囲って数えるだけで、場が一発で出る。点・線・面 ── ガウス面を対称性に合わせて選ぶコツを、点電荷・帯電した線・無限平面・コンデンサで手を動かして掴む。"
pubDate: 2026-06-24
tags: ["電磁気", "ガウスの法則", "電場", "対称性", "フラックス"]
demo: "/gauss-symmetry/"
demoLabel: "対称性とガウス面のラボを全画面で開く"
series: "electromagnetism"
order: 3
related:
  - { title: "なぜ成り立つか ── 発散とガウスの法則（フラックスの概念）", url: "/docs/divergence-and-gauss/" }
  - { title: "電位とは、運んだ仕事のこと（ここで出した E を歩いて V にする）", url: "/docs/electric-potential/" }
  - { title: "場とは、測れる力のこと（E＝F/q とクーロン）", url: "/docs/field-as-measured-force/" }
---

[② 電位](/docs/electric-potential/) で、場の上を歩けば電位が出ると分かった ── $V = \int \vec E\cdot d\vec l$。でも、これには前もって **場 $\vec E$ そのもの** が要る。歩く地図がなければ、歩けない。

その $\vec E$ を、いまはどう出していたか。[① クーロンの法則](/docs/field-as-measured-force/) で源ひとつの $1/r^2$ を覚えて、源がいくつもあればその矢印を足す（重ね合わせ）。これは正しいけれど、**骨が折れる**。源が点ならいい。でも、電荷が金属の棒のように線に沿って連続に乗っていたり、平らな板いっぱいに塗り広げられていたら、足すべき源は無限個 ── 各点で無限本の矢印を $\cos/\sin$ で分解して足す、なんてやっていられない。

もっと楽な道はないか。── ある。電荷の並び方に **対称性** があるときに限って、源を一個も足さずに、場が一発で出る。今日はその道具を、手に馴染ませる。

## 道具の正体 ── 囲んで、数える

使う道具は、[⑥ 発散とガウスの法則](/docs/divergence-and-gauss/) で「なぜ成り立つか」までやった、あの法則だ。ここでは中身の証明は⑥に預けて、**使い方** に集中する。形だけ思い出しておこう：

$$\oint \vec E\cdot d\vec A = \frac{Q_{\text{中}}}{\varepsilon_0}$$

言葉に直すと一文。**どんな形でもいいから閉じた面で囲って、その面を貫いて外へ出ていく電場（フラックス）を数えると、中に入っている電荷の総量（を $\varepsilon_0$ で割ったもの）に等しい。** 左辺の $\oint \vec E\cdot d\vec A$ は「閉じた面ぜんぶで、貫く分を足す」という印 ── ⑥でフラックスとして触ったやつだ。右辺は「囲んだ中の電荷」。面の形には一切よらず、中身だけで決まる。

ここで、ちょっと不思議に思ってほしい。左辺には知りたい $\vec E$ が入っているのに、右辺は「中の電荷」というすでに知っている量だ。**ということは、この等式を $\vec E$ について解けば、場が出るのでは？** ── 半分は当たり。でも左辺は積分（足し算）だから、ふつうは $\vec E$ をくくり出せない。くくり出せるための、たった一つの条件 ── それが **対称性** だ。

## 手品のタネは、面の選び方

ガウスの法則そのものは、どんな閉じた面でも成り立つ。でも場を **出す** 道具として使えるのは、面をうまく選んだときだけだ。狙いはこう：

> **その面の上で、$\vec E$ の大きさが一定になり、しかも面に対して垂直（または平行）になる**ように、囲む面を選ぶ。

そういう面が選べると、左辺の足し算が、ただの掛け算につぶれる。$\vec E$ が面に垂直で大きさ $E$ で一定なら、$\oint \vec E\cdot d\vec A$ は **$E \times (\text{その面の面積})$** になるからだ（面に平行な所は貫かないので $0$、垂直な所だけが効く）。すると：

$$E \times (\text{面積}) = \frac{Q_{\text{中}}}{\varepsilon_0} \quad\Longrightarrow\quad E = \frac{Q_{\text{中}}}{\varepsilon_0 \times (\text{面積})}$$

積分が消えて、割り算ひとつで $E$ が出た。── これが道具の三段だ。

- **手順** ── 電荷の対称性を見て、「$E$ が一定＆垂直になる」閉じた面を選ぶ。$\oint \vec E\cdot d\vec A = E\times$面積 とおき、$=Q_{\text{中}}/\varepsilon_0$ を $E$ について解く。
- **意味** ── 中の電荷が外へ撒くフラックスを、対称な面で均等に受け止めている。面積で割れば、一点あたりの強さ＝場。
- **嬉しさ** ── 源を一個ずつ足す積分が、まるごと要らなくなる。対称性のある所では、これが最短路だ。

肝心なのは、**面（ガウス面）を電荷の対称性に合わせて選ぶ** こと。点には球、線には円柱、面には箱 ── この対応さえ手に入れば、あとは面積を書くだけだ。順にやってみよう。

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 460 180" width="460" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <!-- point -> sphere -->
  <circle cx="78" cy="86" r="44" fill="none" stroke="#3c7876" stroke-width="1.5" stroke-dasharray="5 3"/>
  <circle cx="78" cy="86" r="4" fill="#c2543d"/>
  <g stroke="#3c7876" stroke-width="1.3">
    <line x1="78" y1="82" x2="78" y2="46"/><line x1="82" y1="86" x2="118" y2="86"/><line x1="74" y1="86" x2="38" y2="86"/><line x1="78" y1="90" x2="78" y2="126"/>
  </g>
  <text x="78" y="158" font-size="10.5" fill="#1d1b17" text-anchor="middle">点 → 球</text>
  <!-- line -> cylinder -->
  <line x1="230" y1="40" x2="230" y2="132" stroke="#c2543d" stroke-width="2.4"/>
  <ellipse cx="230" cy="40" rx="34" ry="10" fill="none" stroke="#3c7876" stroke-width="1.5" stroke-dasharray="5 3"/>
  <ellipse cx="230" cy="132" rx="34" ry="10" fill="none" stroke="#3c7876" stroke-width="1.5" stroke-dasharray="5 3"/>
  <line x1="196" y1="40" x2="196" y2="132" stroke="#3c7876" stroke-width="1.5" stroke-dasharray="5 3"/>
  <line x1="264" y1="40" x2="264" y2="132" stroke="#3c7876" stroke-width="1.5" stroke-dasharray="5 3"/>
  <g stroke="#3c7876" stroke-width="1.3">
    <line x1="234" y1="86" x2="262" y2="86"/><line x1="226" y1="86" x2="198" y2="86"/>
  </g>
  <text x="230" y="158" font-size="10.5" fill="#1d1b17" text-anchor="middle">線 → 円柱</text>
  <!-- plane -> box -->
  <line x1="338" y1="86" x2="438" y2="86" stroke="#c2543d" stroke-width="2.4"/>
  <rect x="360" y="58" width="56" height="56" fill="none" stroke="#3c7876" stroke-width="1.5" stroke-dasharray="5 3"/>
  <g stroke="#3c7876" stroke-width="1.3">
    <line x1="388" y1="82" x2="388" y2="50"/><line x1="388" y1="90" x2="388" y2="122"/>
  </g>
  <text x="388" y="158" font-size="10.5" fill="#1d1b17" text-anchor="middle">面 → 箱</text>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">ガウス面は、電荷の対称性に合わせて選ぶ。点電荷なら球、無限に長い線なら円柱、無限に広い面なら箱（その面でだけ $E$ が一定＆垂直になる）。選び方さえ合えば、あとは「面積で割る」だけ。</figcaption>
</figure>

## 点電荷 ── 球で囲うと、クーロンが戻ってくる

まず点電荷 $Q$。場は中心から放射状に、どの向きにも同じ強さで出ているはずだ（向きを区別する理由がどこにもないから ── これが対称性だ）。なら、囲む面は **中心 $Q$ をくるむ半径 $r$ の球** が素直だ。球の上ではどこでも $\vec E$ は外向き垂直、大きさは同じ $E$。

球の表面積は $4\pi r^2$ だから、フラックスは $E \times 4\pi r^2$。これが中の電荷 $Q$ を $\varepsilon_0$ で割ったものに等しい：

$$E \times 4\pi r^2 = \frac{Q}{\varepsilon_0} \quad\Longrightarrow\quad E = \frac{Q}{4\pi\varepsilon_0 r^2}$$

見覚えがあるよね。── これは①のクーロンの法則 $E = \dfrac{Q}{4\pi\varepsilon_0 r^2}$ そのものだ。出発点だったクーロンが、ガウスから **戻ってきた**。①で「$1/4\pi\varepsilon_0$ の $4\pi$ は、球の表面積の $4\pi$ と後で打ち消し合う」と予告しておいたのは、これのことだった ── いまちょうど、$4\pi r^2$ の $4\pi$ と相殺している。点電荷では、ガウスはクーロンと同じ答えを返す“確かめ算”になっている。本領は、次の二つだ。

## 無限に長い線 ── 円柱で囲う

こんどは、電荷が細い棒に沿って一様に乗っている（線電荷）。1メートルあたりの電荷を $\lambda$（線電荷密度）とする。棒のまわりの対称性は、点とは違う ── 棒からの距離 $r$ が同じなら、場は同じ強さで、棒に対して **真横（放射状）** を向く。棒に沿ってどこへずれても景色は変わらない。

この対称性に合う面は、**棒を芯にした半径 $r$・長さ $L$ の円柱** だ。円柱の **側面** では $\vec E$ は外向き垂直で一定。**上下のふた** では $\vec E$ は面と平行（横向き）に通り抜けるだけなので、貫かない＝フラックス $0$。だから効くのは側面だけ。側面の面積は $2\pi r \times L$（円周 × 長さ）：

$$E \times 2\pi r L = \frac{\lambda L}{\varepsilon_0} \quad\Longrightarrow\quad E = \frac{\lambda}{2\pi\varepsilon_0 r}$$

両辺の $L$ が消えるのが気持ちいい（場は棒の長さの取り方によらない ── 無限に長い、の意味だ）。点電荷では $1/r^2$ だったのに、線では **$1/r$**。薄まり方が一段ゆるい。理由も対称性にある：点は球面（$\propto r^2$）に薄まるのに、線は円柱の側面（$\propto r$）にしか薄まらないから、一つ分ゆるくなる。

## 無限に広い面 ── 箱で囲うと、距離によらない

最後に、電荷が広い板いっぱいに一様に塗られている（面電荷）。1平方メートルあたりの電荷を $\sigma$（面電荷密度）とする。対称性はさらに違って、場は板に **垂直** に、両側へまっすぐ出る。板に平行にどこへずれても、板に近づいても遠ざかっても（無限に広いので）、強さは変わらないはずだ。

合う面は、**板をまたぐ箱**（板の表と裏に面積 $A$ のふたを持つ、薄い箱）。箱の **表と裏のふた** では $\vec E$ が垂直に出ていく ── 効く面積は両側で $2A$。**箱の側面**（板に垂直な壁）では $\vec E$ は面と平行に走るだけで貫かない＝$0$。箱の中の電荷は $\sigma A$：

$$E \times 2A = \frac{\sigma A}{\varepsilon_0} \quad\Longrightarrow\quad E = \frac{\sigma}{2\varepsilon_0}$$

$A$ が消えて、残った $E$ には **$r$ が入っていない**。── 無限に広い板の場は、**離れても弱くならない**。点や線の感覚だと意外だけど、これも薄まりの話で読める：点は球面に、線は円柱面に薄まったが、無限平面は「広がる先」がない（どこまで行っても同じ無限平面が目の前にある）から、薄まりようがないんだ。

## コンデンサ ── 板を2枚、重ねて足す

板を1枚やったら、応用はすぐそこだ。**コンデンサ**＝向かい合う2枚の板に、$+\sigma$ と $-\sigma$ を持たせたもの。場は、2枚それぞれが作る $\dfrac{\sigma}{2\varepsilon_0}$ を **重ね合わせる**（①の足し算）だけで出る。

- **板と板のあいだ**：$+$ の板からは外（右）へ、$-$ の板へは内（右）へ ── 二つの場が **同じ向き** にそろって、足されて2倍：$E = \dfrac{\sigma}{\varepsilon_0}$。
- **板の外側**：2枚の場が **逆向き** にぶつかって、ぴたり打ち消し合う：$E = 0$。

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 440 170" width="440" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <line x1="150" y1="26" x2="150" y2="134" stroke="#c2543d" stroke-width="3"/>
  <text x="150" y="18" font-size="11" fill="#c2543d" text-anchor="middle">＋σ</text>
  <line x1="290" y1="26" x2="290" y2="134" stroke="#3c7876" stroke-width="3"/>
  <text x="290" y="18" font-size="11" fill="#3c7876" text-anchor="middle">−σ</text>
  <!-- inside field arrows (strong, rightward) -->
  <g stroke="#1d1b17" stroke-width="1.8">
    <line x1="178" y1="56" x2="262" y2="56"/><polygon points="262,56 252,51 252,61" fill="#1d1b17"/>
    <line x1="178" y1="80" x2="262" y2="80"/><polygon points="262,80 252,75 252,85" fill="#1d1b17"/>
    <line x1="178" y1="104" x2="262" y2="104"/><polygon points="262,104 252,99 252,109" fill="#1d1b17"/>
  </g>
  <text x="220" y="150" font-size="10" fill="#1d1b17" text-anchor="middle">あいだ：足されて E＝σ/ε₀</text>
  <text x="65" y="84" font-size="10.5" fill="#aaa49b" text-anchor="middle">外：E＝0</text>
  <text x="375" y="84" font-size="10.5" fill="#aaa49b" text-anchor="middle">外：E＝0</text>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">コンデンサは、2枚の無限平面の重ね合わせ。あいだでは2つの場が同じ向きにそろって2倍（σ/ε₀）、外では逆向きで打ち消してゼロ。中だけに、一様な場を閉じ込められる ── これが「電気を溜める」入れ物の正体だ。</figcaption>
</figure>

あいだに **一様な場** だけを閉じ込め、外には漏らさない ── これが電気を溜める入れ物、コンデンサの素の姿だ。一様だから、あいだの電位差（電圧）も素直に出る。場が一定 $E$、板の間隔が $d$ なら、②の歩いて足す $V=\int E\,dl$ は、ただの掛け算 $V = E\,d = \dfrac{\sigma}{\varepsilon_0}d$ になる。場を出す道具（ガウス）と、場を歩く道具（②の電位）が、ここで噛み合う。

## ②へ、つなぐ ── 場を出して、歩く

最後に、今日の道具を②と結んでおく。②で「歩く地図が要る」と言ったのは、まさにこの $\vec E$ のことだった。ガウスで場を出して、②で歩けば、電位が出る。

点電荷で確かめよう。ガウスで $E = \dfrac{Q}{4\pi\varepsilon_0 r^2}$ を出し、これを②の流儀で無限遠から足し上げる：

$$V(r) = \int_r^{\infty} \frac{Q}{4\pi\varepsilon_0 r'^2}\,dr' = \frac{Q}{4\pi\varepsilon_0 r}$$

②で出した点電荷の電位 $V = \dfrac{Q}{4\pi\varepsilon_0 r}$ が、ちゃんと戻ってくる。**ガウスで $E$ を出す → ②で歩いて $V$ にする** ── この二段が、電場まわりの計算のいちばん使う型だ。線電荷でも面でも、同じ二段で電位まで出せる（線なら $V$ は $\log$ 型、平板なら一次関数）。

下のラボで、対称性とガウス面の対応を手で掴んでほしい。点・線・面を切り替えると、それに合うガウス面（球・円柱・箱）が立ち上がり、面積で割るだけで場が出る ── その「面の選び方で積分が消える」瞬間を、目で追えるようにした。

<div class="demo-embed">
  <iframe src="/gauss-symmetry/" title="対称性とガウス面のラボ" loading="lazy"></iframe>
  <div class="cap"><span>gauss-symmetry</span><a href="/gauss-symmetry/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

ガウスがこんなに楽なのは、対称性という特別な贈り物があったからだ。電荷がいびつに散らばっていたら、この手は使えず、また源を一つずつ足す世界（[④ 源を足して、場を作る](/docs/field-from-sources/)）へ戻る。けれど、対称性さえあれば、囲んで数えるだけで場が落ちてくる ── ①が挙げた電磁気の“5つの芯”の、その1番目を、これで道具として手にしたことになる。
