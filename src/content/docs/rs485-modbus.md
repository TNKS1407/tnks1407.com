---
title: "RS-485 と Modbus ── 遠くまで、大勢に"
description: "UART は近くて1対1だった。これを「遠く・大勢」へ広げるのが RS-485 だ。鍵は二つ ── 2本の線に逆向きの信号を流して“差”で読むと、ノイズがまるごと消える（だから1200m 届く）。そして同じ2本に何台もぶら下げ、アドレスで呼び分ける。その上で話す Modbus は「1台ずつ聞いて回る」── EtherCAT がひっくり返した、あの世界の入口だ。"
pubDate: 2026-06-29
tags: ["通信", "RS-485", "Modbus", "差動", "マルチドロップ", "フィールドバス"]
demo: "/rs485/"
demoLabel: "差動信号のラボを全画面で開く"
series: "communication"
order: 4
---

<style>
.code-sample{background:#fbf8f2;border:1px solid #e3dbd0;border-radius:8px;padding:.85rem 1rem;margin:1.3rem 0;font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.8;overflow-x:auto;color:#3a3835;white-space:pre;}
.code-sample .ck{color:#7a5ea8;}.code-sample .cf{color:#2563aa;}.code-sample .cs{color:#3c7876;}.code-sample .cn{color:#c9761f;}.code-sample .cc{color:#aaa49b;font-style:italic;}
.code-cap{font-size:.74rem;color:#aaa49b;font-family:'JetBrains Mono',monospace;margin:-.7rem 0 1.3rem;}
</style>

[UART](/docs/uart/) は近くて1対1、[SPI / I²C](/docs/spi-i2c/) は基板の中だった。今日は、ここを **「遠く・大勢」** へ広げる。工場の端から端まで、何十台もの機器を、一本のバスでつなぐ ── そういう世界の定番が **RS-485**、そしてその上で話す言葉が **Modbus** だ。

うれしいことに、土台は UART のまま。start/stop の枠も、ボーレートの約束も、そっくり生きている。RS-485 が付け足すのは、**二つの工夫**だけ ── 「遠くまで届かせる電気の持ち方」と「一本のバスに大勢ぶら下げる作法」。順に開けていこう。

## 1. 差で送ると、ノイズが消える ── 差動

まず「遠くまで」。UART の信号は、1本の線の電圧で 1/0 を表した（シングルエンド）。近くなら十分だけど、線が長くなると外来ノイズに弱い ── ノイズが電圧を揺らして、0V の境を逆に押し越えると、受け手が読み間違える。

RS-485 の答えが、いっそ美しい。**線を2本（A と B）使って、同じ信号を逆向きに流す。受け手は、その“差”を読む。** こうすると何が起きるか ── ノイズは2本の線にほぼ等しく乗る（同じ場所を並んで走っているから）。だから A と B の差を取ると、**両方に等しく乗ったノイズが、引き算でまるごと消える**。残るのは信号だけ、しかも 2 倍になって。

下の widget で、その引き算を手で確かめてほしい。シングルエンドにノイズを乗せて誤読する所、そして A−B でノイズがすっと消える所が、いちばんの見どころだ。

<div class="demo-embed">
  <iframe src="/rs485/" title="差動信号のラボ" loading="lazy"></iframe>
  <div class="cap"><span>rs485</span><a href="/rs485/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

式で書くと、ばかばかしいほど単純だ。A が「信号＋ノイズ」、B が「−信号＋ノイズ」。差を取ると：

$$ A - B = (\,s + n\,) - (\,-s + n\,) = 2s $$

ノイズ $n$ は、二つの線に共通（コモンモード）だから、引き算で消える。これを **コモンモード除去** と呼ぶ。差動という一手だけで、RS-485 は最大 **1200m**、しかも高速・多ノイズ環境に耐える線になる。ツイストペア（2本をより合わせた線）を使うのも同じ理屈で、より合わせると2本がいっそう「同じノイズ」を浴びるので、引き算がさらによく効く。

## 2. 一本のバスに、大勢 ── マルチドロップ

次に「大勢」。RS-485 は、その2本の線を **共有のバス**にして、たくさんの機器をぶら下げられる（マルチドロップ）。一本の幹線に、機器が枝のようにぶら下がる ── 32台、対応チップによってはもっと。

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 480 150" width="480" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <!-- bus (2 lines A/B) -->
  <line x1="30" y1="46" x2="450" y2="46" stroke="#2563aa" stroke-width="2"/>
  <line x1="30" y1="56" x2="450" y2="56" stroke="#7a5ea8" stroke-width="2"/>
  <text x="455" y="48" font-size="9" fill="#2563aa">A</text>
  <text x="455" y="58" font-size="9" fill="#7a5ea8">B</text>
  <!-- master -->
  <rect x="30" y="14" width="74" height="22" rx="5" fill="#e6f0ef" stroke="#3c7876" stroke-width="1.4"/>
  <text x="67" y="29" font-size="10" fill="#3c7876" text-anchor="middle" font-weight="bold">master</text>
  <line x1="67" y1="36" x2="67" y2="46" stroke="#9a8f7e" stroke-width="1.2"/>
  <!-- slaves -->
  <g>
    <rect x="150" y="92" width="60" height="22" rx="5" fill="#fff" stroke="#c9b8a8" stroke-width="1.2"/>
    <text x="180" y="107" font-size="9.5" fill="#5a5550" text-anchor="middle">addr 1</text>
    <line x1="180" y1="56" x2="180" y2="92" stroke="#9a8f7e" stroke-width="1.2"/>
    <rect x="250" y="92" width="60" height="22" rx="5" fill="#fff" stroke="#c9b8a8" stroke-width="1.2"/>
    <text x="280" y="107" font-size="9.5" fill="#5a5550" text-anchor="middle">addr 2</text>
    <line x1="280" y1="56" x2="280" y2="92" stroke="#9a8f7e" stroke-width="1.2"/>
    <rect x="350" y="92" width="60" height="22" rx="5" fill="#fff" stroke="#c9b8a8" stroke-width="1.2"/>
    <text x="380" y="107" font-size="9.5" fill="#5a5550" text-anchor="middle">addr 3</text>
    <line x1="380" y1="56" x2="380" y2="92" stroke="#9a8f7e" stroke-width="1.2"/>
  </g>
  <text x="240" y="138" font-size="9.5" fill="#7d7568" text-anchor="middle">同じ2本のバスに、アドレスを持った機器がぶら下がる（半二重＝一度に話せるのは1台）</text>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">RS-485 のマルチドロップ。1本の幹線（A/B の2本）に、アドレスを持った機器が並んでぶら下がる。線は共有で半二重 ── 同時に二人が喋ると混信するので、「一度に話すのは1台だけ」という約束が要る。その交通整理をするのが、次の Modbus だ。</figcaption>
</figure>

ただ、線が共有ということは、**同時に二人が喋ると混信する**。だから「いつ・誰が喋るか」の交通整理が要る。いちばん素直なやり方は、**親分（master）を一人決めて、その親分だけが口火を切る**こと。子（slave）は、自分が名指しで聞かれたときだけ答える。この交通整理の作法が、次の Modbus だ。

## 3. 順番に、聞いて回る ── Modbus とポーリング

**Modbus** は、RS-485 の上でいちばん広く使われている言葉だ。やることは拍子抜けするほど素朴で、master が **「アドレス○番の機器の、レジスタ△を読んで（書いて）」** と頼み、その相手だけが返事をする。中身は、アドレス＋機能コード（読み 0x03 / 書き 0x06 など）＋レジスタ番号＋データ＋誤り検出（CRC）。下の widget で1行ずつ。

<div class="demo-embed">
  <iframe src="/modbus-code/" title="Modbus をコードで" loading="lazy"></iframe>
  <div class="cap"><span>modbus-code</span><a href="/modbus-code/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

ここで、この記事でいちばん覚えておいてほしい言葉が出てくる ── **ポーリング**だ。共有バスでは一度に1台しか喋れないから、master は **1台ずつ、順番に聞いて回る**しかない。「addr 1 さん？」と聞いて返事を待ち、「addr 2 さん？」と聞いて待ち……。

<pre class="code-sample"><span class="cc"># master は、相手を変えて聞いて回る（ポーリング）</span>
<span class="ck">for</span> addr <span class="ck">in</span> [<span class="cn">1</span>, <span class="cn">2</span>, <span class="cn">3</span>, <span class="cn">4</span>]:
    rr = client.<span class="cf">read_holding_registers</span>(<span class="cn">0</span>, <span class="cn">2</span>, slave=addr)
    <span class="cc"># ↑ 1台ぶんの往復。台数が増えるほど、一周が遅くなる</span></pre>
<div class="code-cap">N 台なら N 回の往復。これがマルチドロップ＋ポーリングの宿命であり、限界でもある。</div>

この「1台ずつ往復する」やり方は、堅実で、配線も安くて、いまも世界中の工場で現役だ。でも弱点もはっきりしている ── **台数が増えるほど、一周が遅くなる**。100台あれば、最後の1台の番が回ってくるまで、99回の往復を待つことになる。

そして ── ここで線がつながる。[EtherCAT](/docs/ethercat/) が「一枚のフレームで全員ぶんを一度に」とひっくり返したのは、まさに**この**ポーリングの世界だったんだ。RS-485 / Modbus が「順番に聞いて回る」なら、EtherCAT は「列車が全員の家を通り抜けながら一度に集める」。今その対比が、実感として効いてくるはずだ。

## 4. どこに居るのか ── 産業ネットワークの、最初の一段

RS-485 と Modbus は、**産業フィールドバスのいちばん土台**にいる。差動で遠くまで、マルチドロップで大勢、master-slave で交通整理 ── この三点セットが、この後に出てくる賢いネットワークたちの、共通の出発点になる。

- 「ポーリングが遅い」を、優先度つきの早い者勝ちで解く → **CAN**（次回）。
- 「共有バスの混信」を、Ethernet の物理に載せ替えて速くする → **産業 Ethernet**（PROFINET / EtherCAT …）。

UART で握った start/stop・ボーレートは、ここでも生きていた。SPI/I²C で覚えた「アドレスで選ぶ」も、Modbus でそのまま効いた。土台に石を積むほど、下の石が何度も顔を出す ── これが、通信を下から積む面白さだと思う。次は、車の中で鍛えられた賢いバス、CAN へ行こう。
