---
title: "UART ── 一本の線に、バイトを乗せる"
description: "通信のしくみを、いちばん素朴なところから積んでいく第一歩。UART（シリアル）は、線一本でビットを順番に送るだけ ── しかもクロックの線を共有しない。文字 'A' を、start/stop の枠にはめ、波形にして送り、受信側が“真ん中”で読み解くまでを、触れる widget と pyserial のコードで開けてみる。ハードの勘が、そのまま通信の勘につながるように。"
pubDate: 2026-06-29
tags: ["通信", "UART", "シリアル", "RS-232C", "ボーレート", "波形"]
demo: "/uart/"
demoLabel: "UART の波形ラボを全画面で開く"
series: "communication"
order: 1
---

<style>
.code-sample{background:#fbf8f2;border:1px solid #e3dbd0;border-radius:8px;padding:.85rem 1rem;margin:1.3rem 0;font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.8;overflow-x:auto;color:#3a3835;white-space:pre;}
.code-sample .ck{color:#7a5ea8;}.code-sample .cf{color:#2563aa;}.code-sample .cs{color:#3c7876;}.code-sample .cn{color:#c9761f;}.code-sample .cc{color:#aaa49b;font-style:italic;}
.code-cap{font-size:.74rem;color:#aaa49b;font-family:'JetBrains Mono',monospace;margin:-.7rem 0 1.3rem;}
.ref-table{width:100%;border-collapse:collapse;margin:1.1rem 0;font-size:.8rem;}
.ref-table th{background:#f0ece6;color:#1d1b17;font-weight:700;text-align:left;padding:.45rem .6rem;border:1px solid #e3dbd0;font-family:'JetBrains Mono',monospace;font-size:.71rem;}
.ref-table td{padding:.45rem .6rem;border:1px solid #e3dbd0;vertical-align:top;line-height:1.5;}
.ref-table tr:nth-child(even) td{background:#faf8f4;}
.ref-table .nm{font-weight:700;color:#3c7876;}
</style>

「通信のしくみ」を、いちばん下の段から一つずつ積んでいこうと思う。その第一歩が UART だ。マイコンを触ったことがあれば、`Serial.begin(9600)` とか、USB シリアルでログを垂れ流したことが、きっとあるはず。あの、いちばん身近なやつ。

身近すぎて中を覗かないまま使いがちだけど、開けてみると、これがきれいなんだ。**線は一本。ビットは時間で順番に。しかも、時計（クロック）の線を共有しない。** 時計がないのに、どうやって受信側はビットの切れ目を見つけるのか ── そこに、ちょっとした知恵が一つ入っている。文字 `'A'` を一個送る、ただそれだけを、線の上の波形まで降りて追いかけてみよう。

## 1. 一本の線に、順番に ── そして時計を共有しない

UART のつなぎ方は、拍子抜けするほど簡単だ。送信（TX）と受信（RX）を一本の線でつなぐ（往復させるならもう一本）、あと共通の GND。それだけ。

ただ、この「TX と RX」、いつも配線でミスる人が多い（私も何度もやった）。なので、名前のことをここで一度きっちり畳んでおく。TX と RX は、**いつも“その機器自身から見た”名前**だ ── TX＝自分がしゃべる口、RX＝自分が聞く耳。だから配線は必ず **たすき掛け**：自分の TX を相手の RX へ、自分の RX を相手の TX へ。GND だけは交差させず、そのまま GND どうしでつなぐ。

<table class="ref-table">
<thead><tr><th>名前（別名いろいろ）</th><th>向き（その機器から見て）</th><th>つなぐ先</th></tr></thead>
<tbody>
<tr><td><span class="nm">TX</span>（TXD / SOUT / DO / Tx）</td><td>出力＝送信（しゃべる）</td><td>相手の <b>RX</b></td></tr>
<tr><td><span class="nm">RX</span>（RXD / SIN / DI / Rx）</td><td>入力＝受信（聞く）</td><td>相手の <b>TX</b></td></tr>
<tr><td><span class="nm">GND</span>（GND / VSS / ⏚）</td><td>電圧の基準</td><td>相手の <b>GND</b>（交差しない）</td></tr>
<tr><td><span class="nm">RTS / CTS</span>（任意・フロー制御）</td><td>「送っていい？」の合図</td><td>RTS→CTS とたすき掛け</td></tr>
</tbody>
</table>

ここで一つ大事なこと ── UART には、後でやる SPI や I²C のような「マスタ／スレーブ」は**本来ない**。両側とも対等に、自分の TX と RX を1本ずつ持つ点対点だ。だから迷ったら難しく考えず、「TX→RX、RX→TX、GND→GND」の三行だけ思い出せばいい。

そして、いちばんの罠を一つ。モジュールや USB シリアル変換基板の中には、ピンを“つなぐ相手の視点”でラベルしてあるものがある（基板に書いてある「RX」が、実は「ここに**あなたの TX** を挿してね」の意味）。この手のボードは、ラベルどおり TX↔TX・RX↔RX で挿すと、結果的に正しく交差する。**表記がどっち視点か**を一度疑う ── 「いつもミスる」の正体は、たいていこれだ。

ここで一つ、後の話の効いてくる事実を置いておく。**UART は、クロックの線を持たない。** これは地味だけど、UART の性格を決める一番大事な点だ。たとえば後の回でやる SPI や I²C は、データとは別に「いま読んでいいよ」を伝える時計の線を一本引く。UART は、引かない。

時計がないなら、受信側はどうやって「1ビットの長さ」を知るんだろう。── 答えは、**前もって速さを約束しておく**。これが **ボーレート**（baud rate）だ。9600 baud なら「1秒間に9600ビット」、つまり1ビットの幅は約 104 マイクロ秒。送る側と受ける側が同じボーレートに設定してさえいれば、時計線がなくても、お互い同じ物差しでビットを刻める。

何も送っていないとき、線は **High** のまま待っている（idle）。この「待機は High」も、ただの約束だ。下の widget の Step 1 で、その素朴なつなぎを見られる。

## 2. 枠にはめて、波形にする

さあ、`'A'` を送ろう。`'A'` は ASCII で `0x41`、ビットで書くと `0100 0001`。これを線に流すんだけど、二つ、約束ごとがある。

ひとつ目。受信側に「ここから1バイトが始まるよ／終わったよ」を伝えるために、データを **枠** にはめる。頭に **start ビット（Low）**、お尻に **stop ビット（High）** を付ける。idle の High から start で Low にカクッと落ちる、その下りエッジが「始まるよ」の合図になる。

ふたつ目。データ8ビットは、**下位ビット（LSB）から先に**送る。これが UART の流儀だ。だから `0x41 = 0100 0001` は、線の上では `1, 0, 0, 0, 0, 0, 1, 0` の順に並ぶ。

この「start ＋ 8データ ＋ stop」という形を、まとめて **8N1**（8データ・パリティ無し・stop 1ビット）と呼ぶ。下の widget で、`'A'` が枠にはまり、波形になり、最後に受信側が各ビットの“真ん中”で読む、というところまで、一歩ずつ触れる。

<div class="demo-embed">
  <iframe src="/uart/" title="UART の波形ラボ" loading="lazy"></iframe>
  <div class="cap"><span>uart</span><a href="/uart/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

1ビットの幅は、ボーレートの逆数だ。コードで書けば、ただの割り算でしかない。

<pre class="code-sample">baud      = <span class="cn">9600</span>              <span class="cc"># ビット/秒</span>
bit_time  = <span class="cn">1</span> / baud           <span class="cc"># ≈ 104µs ＝ 1ビットの幅</span>
frame_len = <span class="cn">1</span> + <span class="cn">8</span> + <span class="cn">1</span>           <span class="cc"># start + データ8 + stop = 10ビット</span>
<span class="cc"># 1バイト送るのにかかる時間 ≈ 10 × 104µs ≈ 1.04ms</span></pre>

ひとつ正直に言っておくと ── ここで波形として見せた「High=1 / Low=0」は、マイコンの足から直接出てくる **TTL レベル**（0V と 3.3V など）の話だ。題に入れた **RS-232C** は、同じ枠組みのまま電圧の約束だけが違う：論理を反転させ、しかも ±12V くらいの大きな振幅を使う（昔の長いケーブルでノイズに負けないように）。だから PC の RS-232 とマイコンを直結すると、レベル変換チップ（MAX232 など）が要る。**枠（start/データ/stop）とボーレートの話は、TTL でも RS-232 でも、まったく同じ**。違うのは電圧の着せ替えだけ、と思っておけばいい。

## 3. コードでは、開く・書く・読む

波形まで見たあとで実際のコードを見ると、ほっとすると思う。Python の **pyserial** で `'A'` を送って受け取るのは、たった数行だ。下の widget で、1行ずつ「いま何をしているか」を確かめられる。

<div class="demo-embed">
  <iframe src="/uart-code/" title="UART をコードで" loading="lazy"></iframe>
  <div class="cap"><span>uart-code</span><a href="/uart-code/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

大事なのは、君が書くのは **開く・書く・読む** の三つだけ、という点だ。`write(b'A')` と渡せば、**start/stop の枠付けも、波形にしてボーレートで送り出すのも、UART のハードが勝手にやってくれる**。受信側も同じで、`read(1)` の裏で、ハードが波形を組み立て直してバイトに戻している。コードはこんなに素っ気ない。

<pre class="code-sample"><span class="ck">import</span> serial
ser = serial.<span class="cf">Serial</span>(<span class="cs">'/dev/ttyUSB0'</span>, <span class="cn">9600</span>)   <span class="cc"># 8N1 が既定</span>

ser.<span class="cf">write</span>(<span class="cs">b'A'</span>)        <span class="cc"># 送る（枠付け・波形化はハード）</span>
data = ser.<span class="cf">read</span>(<span class="cn">1</span>)     <span class="cc"># 受け取る（来るまで待つ）→ b'A'</span></pre>
<div class="code-cap">これが UART プログラミングの芯。あとは「何バイト読むか」「改行まで読むか」等の都合が乗るだけ。</div>

同じことを、Python に隠してもらわず **C** で書いてみると、pyserial が一行の裏でやっていた“お膳立て”が、表に出てくる。下は Linux（POSIX）での最小形だ。`open` で口を開け、`termios` でボーレートと 8N1 を設定し、あとは `write` / `read`。やっている動きは Python と同じなのに、設定の一つ一つが見えるのが分かると思う。

<pre class="code-sample"><span class="ck">#include</span> <span class="cs">&lt;fcntl.h&gt;</span>      <span class="cc">// open</span>
<span class="ck">#include</span> <span class="cs">&lt;termios.h&gt;</span>    <span class="cc">// シリアルの設定</span>
<span class="ck">#include</span> <span class="cs">&lt;unistd.h&gt;</span>     <span class="cc">// write / read</span>

<span class="ck">int</span> fd = <span class="cf">open</span>(<span class="cs">"/dev/ttyUSB0"</span>, O_RDWR | O_NOCTTY);  <span class="cc">// 口を開ける</span>

<span class="ck">struct</span> termios tio;
<span class="cf">tcgetattr</span>(fd, &amp;tio);              <span class="cc">// いまの設定を読む</span>
<span class="cf">cfsetspeed</span>(&amp;tio, <span class="cn">B9600</span>);          <span class="cc">// ボーレート = 9600</span>
tio.c_cflag |=  <span class="cn">CS8</span>;              <span class="cc">// データ 8 ビット</span>
tio.c_cflag &amp;= ~<span class="cn">PARENB</span>;           <span class="cc">// パリティ無し（N）</span>
tio.c_cflag &amp;= ~<span class="cn">CSTOPB</span>;           <span class="cc">// stop 1 ビット  → これで 8N1</span>
<span class="cf">tcsetattr</span>(fd, TCSANOW, &amp;tio);     <span class="cc">// 設定を反映</span>

<span class="cf">write</span>(fd, <span class="cs">"A"</span>, <span class="cn">1</span>);                <span class="cc">// 送る（枠付け・波形化はハード）</span>
<span class="ck">char</span> buf[<span class="cn">1</span>];
<span class="cf">read</span>(fd, buf, <span class="cn">1</span>);                 <span class="cc">// 受け取る（来るまで待つ）→ 'A'</span></pre>
<div class="code-cap">Python の <code>Serial('/dev/ttyUSB0', 9600)</code> 一行が隠していた中身＝「ボーレートと 8N1 の設定」が、C では termios の数行として表に出る。逆に言えば、pyserial はここを気持ちよく畳んでくれていた、ということ。動き自体は同じだ。</div>

ちなみに、PC でなくマイコン側（Arduino など）だと、もっと短い ── `Serial.begin(9600)` で 8N1 とボーレートを決め、`Serial.write('A')` / `Serial.read()`。**開く・書く・読むの三つの扉は、PC でもマイコンでも、言語が C でも Python でも、まったく同じ**だ。違うのは、その扉の奥を誰がどこまで畳んでくれているか、だけ。

## 4. 中の仕掛け ── シフトレジスタと、真ん中サンプリング

「ハードが勝手にやる」と言った、その中身を少しだけ開けておこう。マイコンの中の **UART ペリフェラル**（USART とも）の正体は、**シフトレジスタ**だ。

送る側（TX）は、バイト `0x41` をシフトレジスタに置いて、ボーレートのリズムで1ビットずつ端から押し出していく。並列（8ビット同時）を直列（1本の線に順番）へ変える ── これが「シリアル化」だ。前後に start と stop を足すのも、このハードがやる。

受け取る側（RX）の方が、ちょっと賢い。時計を共有していないから、まず **start の下りエッジ** を見張っていて、それを見つけた瞬間に「いま始まった」と内部の時計を走らせる。あとはボーレートぶんずつ進んで、各ビットの **真ん中** で電圧を読む（widget の Step 4 の橙の点）。端っこでなく中央で読むのがミソで、送受信のクロックが多少ずれていても、判定をいちばん間違えにくい場所だからだ。実際のハードは1ビットを16分割くらいで細かく刻んで（オーバーサンプリング）、ど真ん中を狙っている。

ここで「波形のどの下りエッジが start か、いつでも分かるの？　何か工夫があるの？」と引っかかった人がいるかもしれない（鋭い）。── 工夫は、ある。鍵は、**待機（idle）も stop も High** だということ。線は、何も送っていなければ High、1バイトが終わっても stop で High に戻る。つまり、線が **High → Low にカクッと落ちるのは、新しいバイトの start のときだけ**。受信ハードは「High に張りついた線が、急に Low に落ちた瞬間」だけを待てばよくて、それは必ず start だ。落ちたら 16分割の刻みでエッジの位置を確かめ、半ビットぶん進んで最初のビットの真ん中へ ── あとは1ビット幅ずつ、中央を読んでいく。そして1バイト読み終えたら、また High に戻った線で、次の下りを待つ。**毎バイト、頭のところで時計を合わせ直している**わけだ。だから二つの離れた時計のズレは、溜まりきる前に、毎回リセットされる。stop ビットを「ただの区切り」と侮れない理由がこれで、stop が線を High に戻してくれるからこそ、次の start の下りが、また綺麗に立つ。

> **時計を共有しない代わりに、「start で同期し、真ん中で読む」。** この一手だけで、二つの離れた時計を、バイトごとに合わせ直している。私は、この割り切りがけっこう好きだ ── 完璧に同期し続けるんじゃなく、毎バイトの頭でちょいと合わせ直すだけ、という軽さがいい。

ただし、この方式には素直な弱点もある。ボーレートが合っていないと、真ん中で読んでいるつもりが少しずつズレて、最後のビットでとうとう隣に滑り込む ── これが、ボーレート設定を間違えたときの、あの **文字化け** の正体だ。原因が「速さの約束のズレ」だと分かっていると、デバッグのとき少し落ち着ける。

## 5. ハードでやる／手でやる ── ソフト UART

ここまで「UART のハードが勝手にやる」と何度か言った。じゃあ、専用ハードが無いとできないのか？　── いや、**ソフトでもできる**。CPU が GPIO の足を、自分のプログラムでカチカチ叩いて波形を作ればいい。これを **ビットバンギング**（bit-banging）と呼ぶ。やることは、上で開けた中身そのままだ：

- **送信（TX）** ── 足を start のぶん Low にして 104µs 待ち、次のビットの値にして 104µs 待ち…を10回くり返す。要は「正しい間隔で、足を上げ下げするだけ」。これは比較的やさしい。**自分が時間の主導権を握っている**からだ。
- **受信（RX）** ── こっちが難しい。相手の start エッジを**取りこぼさずに**捕まえ、そこから 104µs 刻みで“真ん中”を読み続ける。その間、CPU は他のことをしている余裕があまりない。割り込みが一発入って数十µs もたつくと、読む位置がずれて、バイトが壊れる。

つまり、ソフト UART の難しさは、ぜんぶ **時間の精度** に化ける。低い速度で・送信が中心なら、ソフトで十分こなせる。でも「速くしたい・受信もしたい・他の処理も同時に回したい」となると、途端に苦しくなる。だから多くのマイコンは、この「正確なタイミングで足を上げ下げ・読む」専用回路 ── つまり前の節で見た **ハード UART（シフトレジスタ＋ボーレート生成器）** を、最初から積んでいる。タイミングのシビアな仕事をソフトに任せず、シリコンに焼いてしまえば、CPU は `write` と書くだけで、裏は寸分たがわず動く。

この **「時間にシビアな仕事を、CPU から専用ハードへ追い出す」** という発想、ここで一度握っておいてほしい。コースの終盤、EtherCAT が“通り抜けながら書き換える”処理を専用チップ（ESC）に焼いた話と、根っこはまったく同じだ ── タイミングが命なら、ハードに落とす。UART は、その一番やさしい実例になっている。

## 6. どこに居るのか ── 同期と、遠く・多数の手前

最後に、UART が通信の地図のどこに立っているかを置いておこう。これから積み上げる土台として。

UART の性格は、一言でいうと **非同期**（asynchronous）── クロック線を共有しない、の言い換えだ。この一点から、隣のものたちが見えてくる。

- **クロック線を“引く”ほうへ** ── 次にやる **SPI / I²C** は、基板の中でチップ同士をつなぐときの定番で、データとは別に時計の線を引く（同期式）。線が増える代わりに、速くて、ズレない。「時計を共有する／しない」が、UART とのいちばんの分かれ目になる。
- **遠く・多数へ** ── UART は基本、点対点（1対1）で、距離も短い。これを「何台もぶら下げたい」「長い距離を引きたい」へ拡張したのが、**RS-485**（と、その上で話す Modbus）だ。電圧の持ち方を差動に変えて、一本のバスに大勢をつなぐ ── ここから先は、もう EtherCAT で見た「マスタが順番に聞いて回る」世界の入口になる。

そう、UART で握った **start/stop・ボーレート・LSB 先・真ん中サンプリング** は、消えてなくならない。RS-485 でも、Modbus でも、根っこは同じ「枠にはめて、速さの約束で読む」だ。土台のいちばん下の石を、いま一つ置いた。次は、この石の上に「距離」と「台数」を積んでいこう。
