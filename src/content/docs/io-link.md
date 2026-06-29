---
title: "IO-Link ── センサの3本線に、デジタルの言葉を"
description: "SPI・I²C は基板の中の話だった。これを基板の外 ── 現場のセンサまで延ばすのが IO-Link。すごいのは、いつもの3本線（24V の電源と、オン/オフのスイッチ信号）をそのまま使うのに、その同じ線でセンサがしゃべり・名乗り・設定を受け取れること。しかも中身は、第一歩で開けた UART そのものだ。点対点のまま、“賢いセンサ”へもう一段。"
pubDate: 2026-06-29
tags: ["通信", "IO-Link", "センサ", "UART", "フィールド", "点対点"]
series: "communication"
order: 3
---

<style>
.code-sample{background:#fbf8f2;border:1px solid #e3dbd0;border-radius:8px;padding:.85rem 1rem;margin:1.3rem 0;font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.8;overflow-x:auto;color:#3a3835;white-space:pre;}
.code-sample .ck{color:#7a5ea8;}.code-sample .cf{color:#2563aa;}.code-sample .cs{color:#3c7876;}.code-sample .cn{color:#c9761f;}.code-sample .cc{color:#aaa49b;font-style:italic;}
.code-cap{font-size:.74rem;color:#aaa49b;font-family:'JetBrains Mono',monospace;margin:-.7rem 0 1.3rem;}
</style>

[SPI と I²C](/docs/spi-i2c/) は、どちらも「基板の上で、チップ同士を近くで結ぶ」話だった。数センチ〜十数センチの世界だ。今日は、その点対点の発想を **基板の外** ── 機械の上に付いた、現場のセンサまで延ばす。出てくるのが **IO-Link** だ。

そして IO-Link のいちばん面白いところは、**新しい線を一本も足さない**ことだ。工場のセンサが昔から使ってきた、あの3本線（電源 +24V、0V、そしてオン/オフのスイッチ信号）── その**同じ3本**を使う。なのに、その線でセンサがしゃべり、自分の名前を名乗り、設定を受け取れるようになる。いつものケーブルのまま、ただのスイッチが“賢いセンサ”に化ける、という回だ。

## 1. いつもの3本線が、しゃべりだす

工場の近接センサを思い浮かべてほしい。金属が近づくと出力線が 24V になり、離れると 0V に戻る ── ただそれだけの、オン/オフの線。配線は3本で、+24V（電源）、0V（GND）、そして信号線が1本。この信号線を、IO-Link の世界では **C/Q** と呼ぶ。

IO-Link は、この C/Q 線に二つの顔を持たせる。

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 480 220" width="480" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <!-- 3 wires labels -->
  <text x="8" y="30" font-size="10" fill="#c2543d" font-weight="bold">L+ 24V</text>
  <text x="8" y="60" font-size="10" fill="#7d7568" font-weight="bold">L− 0V</text>
  <text x="8" y="120" font-size="10" fill="#2563aa" font-weight="bold">C/Q</text>
  <line x1="70" y1="26" x2="470" y2="26" stroke="#c2543d" stroke-width="1.5"/>
  <line x1="70" y1="56" x2="470" y2="56" stroke="#7d7568" stroke-width="1.5"/>
  <!-- divider -->
  <line x1="260" y1="78" x2="260" y2="210" stroke="#e3dbd0" stroke-width="1" stroke-dasharray="3 3"/>
  <text x="160" y="95" font-size="10.5" fill="#7d7568" text-anchor="middle" font-weight="bold">SIO（従来＝オン/オフ）</text>
  <text x="370" y="95" font-size="10.5" fill="#3c7876" text-anchor="middle" font-weight="bold">IO-Link（通信）</text>
  <!-- SIO: simple step -->
  <path d="M70,150 L120,150 L120,112 L200,112 L200,150 L255,150" fill="none" stroke="#2563aa" stroke-width="2"/>
  <text x="160" y="170" font-size="8.5" fill="#aaa49b" text-anchor="middle">物が来た＝High / 離れた＝Low</text>
  <!-- IO-Link: UART burst -->
  <path d="M270,150 L282,150 L282,112 L294,112 L294,150 L306,150 L306,112 L312,112 L312,150 L330,150 L330,112 L342,112 L342,150 L348,150 L348,112 L366,112 L366,150 L378,150 L378,112 L390,112 L390,150 L402,150 L402,112 L420,112 L420,150 L432,150 L432,112 L444,112 L444,150 L465,150" fill="none" stroke="#3c7876" stroke-width="2"/>
  <text x="370" y="170" font-size="8.5" fill="#aaa49b" text-anchor="middle">同じ線に、ビットの列が流れる</text>
  <text x="240" y="205" font-size="9" fill="#7d7568" text-anchor="middle">── 同じ C/Q 線。マスタが「起こす」と、左から右へ顔が変わる ──</text>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">3本線はそのまま。C/Q 線が、ただのオン/オフ（SIO モード）にも、ビットが流れる通信（IO-Link モード）にもなる。だから IO-Link 対応の差し込み口に、昔ながらのただのスイッチを挿しても、ちゃんと動く（その時は SIO のまま）。後方互換、というやつだ。</figcaption>
</figure>

一つめは **SIO**（Standard IO）── 昔のまま、ただのオン/オフ。二つめが **IO-Link** ── 同じ線にビットの列を流して通信する。差し込み口（マスタ側）は、最初に「ねえ、君しゃべれる？」という合図（**ウェイクアップ**）をその線に送る。相手が返事をすれば通信モードへ、しなければ「ああ、ただのスイッチか」と SIO のまま、という切り替えだ。

もう一つ大事な前提。IO-Link は **点対点** ── マスタの1ポートと、デバイス1台。**バスではない**（一本の線に大勢ぶら下げるのは、次の RS-485 からの世界）。規格の名前 IEC 61131-9 の正式名も "Single-drop"、つまり「一滴＝1台」だ。SPI/I²C の点対点を、そのまま現場のケーブルへ持ち出した、と思えばいい。

## 2. 中身は、実は UART

では、その C/Q 線を流れるビットは何の形をしているのか。ここが気持ちのいいところで ── **第一歩で開けた [UART](/docs/uart/) そのもの**だ。

通信モードに入ると、C/Q 線には UART のフレームが流れる。start ビットで始まり、8 ビットのデータ、パリティ（偶数）、stop ビット ── あの「枠にはめて送る」やつだ。速さ（ボーレート）は3段階のどれかで、マスタとデバイスがウェイクアップのときに握り合う：

- **COM1** … 4.8 kbit/s
- **COM2** … 38.4 kbit/s
- **COM3** … 230.4 kbit/s

つまり、UART の回で握った勘 ── start/stop の枠、ボーレート＝1ビットの幅、受信は各ビットの真ん中で読む ── が、**そっくりそのまま**ここで効く。下は UART の波形ラボだけど、IO-Link の線を流れているのは、まさにこれだと思って眺めてほしい。

<div class="demo-embed">
  <iframe src="/uart/" title="UART の波形ラボ（IO-Link の線も、中身はこれ）" loading="lazy"></iframe>
  <div class="cap"><span>uart</span><a href="/uart/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

役割もはっきりしている。**いつもマスタが主導**して問いかけ、デバイスが答える。毎周期やり取りする「いまのセンサ値」＝**プロセスデータ**（数バイト、最大32バイトほど）と、ときどき読み書きする「設定や素性」＝**オンリクエストデータ**の二本立てだ。常に流れる細い管（プロセス値）と、必要なときだけ開く太い扉（設定）、と分けて持っている。

## 3. 名乗る・設定できる ── ただのスイッチとの違い

ここからが、ただのオン/オフ線との本当の違いだ。IO-Link のデバイスは、**素性**と**設定の引き出し**を持っている。

- **素性** ── ベンダ ID と デバイス ID。「どこの何という製品か」をマスタが読める。
- **設定の引き出し** ── パラメータが **インデックス**（と必要ならサブインデックス）という番号で並んでいて、マスタが読み書きできる。感度、しきい値、フィルタ、単位、表示色…。この番号引きの仕組みを **ISDU**（Indexed Service Data Unit）と呼ぶ。
- **異常の申告** ── 「汚れてきた」「温度が高い」といったイベントを、デバイスの側から上げられる。黙って壊れるのでなく、**理由を言って**から落ちる。

そして、その引き出しの中身が機種ごとにどう並んでいるかは、**IODD**（IO Device Description）という XML ファイルに書いてある。マスタはこれを読めば、見たことのないセンサでも「インデックス 0x0012 は製品名、0x0024 はしきい値」と分かる。

この「機種を説明する一枚の XML」という発想、実はこのシリーズで何度も顔を出す。EtherCAT の [ESI](/docs/ethercat/)、PROFINET の GSD ── みんな同じ役回りだ。「どんな相手でも、説明書さえ標準形なら、汎用のマスタが扱える」。IO-Link の IODD は、その最小版、といっていい。

## 4. コードでは ── プロセス値と、パラメータ

ソフトから触るとき、入口は機種（マスタ）によって違う。けれど **形はいつも同じ二つの扉**だ ── 毎周期の **プロセスデータ**（いまの値）と、番号引きの **パラメータ**（ISDU）。

最近の IO-Link マスタは、その二つを JSON-REST で外に出していることが多い。例えばこんな具合（パスはメーカごとに違うけれど、「ポートを選んで、プロセス値か、インデックスでパラメータを読む」という形は共通だ）：

<pre class="code-sample"><span class="cc"># IO-Link マスタ（IP: 192.168.0.10）の ポート1 を読む例</span>
<span class="ck">import</span> requests

M = <span class="cs">'http://192.168.0.10'</span>

<span class="cc"># (1) 毎周期のプロセスデータ＝いまのセンサ値（生バイト列）</span>
pd = requests.<span class="cf">get</span>(<span class="cs">f'{M}/port/1/processdata/value'</span>).<span class="cf">json</span>()
<span class="cf">print</span>(<span class="cs">'process data ='</span>, pd[<span class="cs">'value'</span>])     <span class="cc"># 例: '01A4' （意味は IODD が決める）</span>

<span class="cc"># (2) パラメータ＝インデックス番号で引く（ISDU）。0x0012 = 製品名</span>
name = requests.<span class="cf">get</span>(<span class="cs">f'{M}/port/1/param/<span class="cn">18</span>'</span>).<span class="cf">json</span>()   <span class="cc"># 18 = 0x12</span>
<span class="cf">print</span>(<span class="cs">'product ='</span>, name[<span class="cs">'value'</span>])

<span class="cc"># (3) パラメータを書く＝設定する（例: しきい値インデックスに 500 を入れる）</span>
requests.<span class="cf">put</span>(<span class="cs">f'{M}/port/1/param/<span class="cn">100</span>'</span>, json={<span class="cs">'value'</span>: <span class="cn">500</span>})</pre>
<div class="code-cap">入口の見た目はメーカ次第。でも「ポートを選ぶ → プロセス値を読む／インデックスでパラメータを読み書きする」という骨格は、どのマスタでも変わらない。PLC から使うときも同じで、プロセス値は I/O の一区画として、パラメータは番号引きのアクセスとして見える。</div>

プロセスデータが「生バイト列」なのがポイントだ。`01A4` が圧力なのか温度なのか、何倍すれば物理量になるのか ── それを決めているのは IODD。[EtherCAT のフレーム](/docs/ethercat/)で見た「バイトの並びの意味は、別腹の説明書が決める」と、まったく同じ構図になっている。

## 5. 特別な機構 ── 壊れたセンサを、ポン付けで戻す

IO-Link がただの「デジタル化」を超えて現場で重宝される理由が、一つある。**データストレージ**だ。

マスタは、つないでいるデバイスのパラメータの控えを **自分の側に**持っている。だから、センサが壊れて、同じ型番の新品にポン付けで交換すると ── マスタが控えのパラメータを**自動で書き戻す**。ノートPCを持って現場へ行き、しきい値や感度を設定し直す、という作業が要らない。ラインが数秒で復帰する。

地味に見えて、これは工場ではとても大きい。「センサ交換＝専門家＋設定作業＝ライン停止」が、「センサ交換＝誰でも・ポン付け・即復帰」に変わる。先の「異常を理由つきで申告する（黙って落ちない）」と合わせて、**止まらない・直しやすい**を、いつもの3本線のまま手に入れている。

## 6. どこに居るのか ── 最後の一メートル

最後に、地図の上での居場所を確かめておこう。

IO-Link は **点対点で、近い**（ケーブルは20mまで）。マスタの1ポートにつき、デバイス1台。だから IO-Link は、上位のネットワーク（フィールドバス）を**置き換えない**。その**下にぶら下がる**。IO-Link マスタ自身が、PROFINET や EtherNet/IP、EtherCAT といったフィールドバス上の一台（ノード）になっていて、何ポートぶんものセンサを束ねて、まとめて上の PLC へ渡す。

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 480 230" width="480" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <!-- PLC -->
  <rect x="190" y="14" width="100" height="34" rx="6" fill="#faf8f4" stroke="#3c7876" stroke-width="1.5"/>
  <text x="240" y="36" font-size="12" fill="#1d1b17" text-anchor="middle" font-weight="bold">PLC</text>
  <!-- fieldbus line -->
  <line x1="240" y1="48" x2="240" y2="78" stroke="#7a5ea8" stroke-width="2"/>
  <text x="248" y="68" font-size="9" fill="#7a5ea8">フィールドバス（PROFINET / EtherNet-IP / EtherCAT）</text>
  <!-- master -->
  <rect x="160" y="78" width="160" height="34" rx="6" fill="#faf8f4" stroke="#2563aa" stroke-width="1.5"/>
  <text x="240" y="100" font-size="11" fill="#1d1b17" text-anchor="middle" font-weight="bold">IO-Link マスタ（4〜8ポート）</text>
  <!-- 4 point-to-point cables -->
  <line x1="180" y1="112" x2="120" y2="158" stroke="#c9761f" stroke-width="1.5"/>
  <line x1="215" y1="112" x2="200" y2="158" stroke="#c9761f" stroke-width="1.5"/>
  <line x1="265" y1="112" x2="280" y2="158" stroke="#c9761f" stroke-width="1.5"/>
  <line x1="300" y1="112" x2="360" y2="158" stroke="#c9761f" stroke-width="1.5"/>
  <text x="355" y="140" font-size="8.5" fill="#c9761f" text-anchor="middle">IO-Link</text>
  <text x="355" y="151" font-size="8.5" fill="#c9761f" text-anchor="middle">点対点・最後の1m</text>
  <!-- sensors -->
  <rect x="95" y="158" width="50" height="28" rx="5" fill="#fff" stroke="#7d7568"/>
  <rect x="175" y="158" width="50" height="28" rx="5" fill="#fff" stroke="#7d7568"/>
  <rect x="255" y="158" width="50" height="28" rx="5" fill="#fff" stroke="#7d7568"/>
  <rect x="335" y="158" width="50" height="28" rx="5" fill="#fff" stroke="#7d7568"/>
  <text x="120" y="176" font-size="9" fill="#7d7568" text-anchor="middle">センサ</text>
  <text x="200" y="176" font-size="9" fill="#7d7568" text-anchor="middle">センサ</text>
  <text x="280" y="176" font-size="9" fill="#7d7568" text-anchor="middle">弁</text>
  <text x="360" y="176" font-size="9" fill="#7d7568" text-anchor="middle">表示</text>
  <text x="240" y="214" font-size="9.5" fill="#7d7568" text-anchor="middle">上＝みんなで共有するネットワーク。下＝マスタから各機器への、一本ずつの線。</text>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">IO-Link は「最後の一メートル」を受け持つ。ネットワーク（上）はみんなで共有する大通り、IO-Link（下）はマスタから各センサへ伸びる一本道。だから IO-Link を学ぶと、フィールドバスの“末端の枝”が見えるようになる。</figcaption>
</figure>

梯子の上での位置はこうだ。SPI・I²C は「基板の上の点対点」だった。IO-Link は、その**点対点の発想を、現場のセンサケーブルへ持ち出して、相手を賢くした**もの ── でも、つなぐ相手はやっぱり1台ずつ（点対点）のまま。「最後の一メートル」を、いつもの線でデジタルにする、という一段だ。

さて、ここまでは「1対1」で来た。次は、いよいよ**一本のバスに、大勢を、長い距離で**ぶら下げたくなる。そのために変えるのは、電圧の持ち方 ── 2本の線に逆向きの信号を流して“差”で読む **差動**だ。これで、ノイズに強く・遠く・多数の世界、[RS-485 と Modbus](/docs/rs485-modbus/) へ進む。点対点の枝を一通り見たから、今度は幹のほうへ。
