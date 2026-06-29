---
title: "Ethernet ── 配達先を書いて、スイッチが運ぶ"
description: "共有バス（RS-485 / CAN）は、一本の線を皆で分け合った。Ethernet はそこを抜けて、点対点をスイッチで束ねる ── 各機器に世界で一意な MAC 番地を振り、フレームに『宛先』を書き、スイッチが『どの機器がどの口に居るか』を学習して、その口だけへ運ぶ。物理のあの波形から、フレームの中身、スイッチの学習までを開けてみる。この上に、次回 TCP/IP が積まれる。"
pubDate: 2026-06-29
tags: ["通信", "Ethernet", "MAC", "スイッチ", "イーサネット", "物理層"]
demo: "/eth-switch/"
demoLabel: "スイッチの MAC 学習ラボを全画面で開く"
series: "communication"
order: 6
---

<style>
.code-sample{background:#fbf8f2;border:1px solid #e3dbd0;border-radius:8px;padding:.85rem 1rem;margin:1.3rem 0;font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.8;overflow-x:auto;color:#3a3835;white-space:pre;}
.code-sample .ck{color:#7a5ea8;}.code-sample .cf{color:#2563aa;}.code-sample .cs{color:#3c7876;}.code-sample .cn{color:#c9761f;}.code-sample .cc{color:#aaa49b;font-style:italic;}
.code-cap{font-size:.74rem;color:#aaa49b;font-family:'JetBrains Mono',monospace;margin:-.7rem 0 1.3rem;}
</style>

ここまで、[RS-485](/docs/rs485-modbus/) も [CAN](/docs/can-canopen/) も、一本のバスを皆で分け合う「共有バス」だった。だから「一度に喋れるのは1台」という制約と、ずっと付き合ってきた。今日の **Ethernet** は、そこを抜ける ── 機器どうしを点対点でつなぎ、**スイッチ**という賢い箱で束ねる。一度に大勢が、ぶつからずに喋れる世界だ。

そして Ethernet は、ただの一通信じゃない。この後に出てくる TCP/IP も、産業用の EtherCAT や PROFINET も、みんなこの Ethernet の上に乗っている ── いわば、ここから上の階ぜんぶの **土台**だ。だから、ここは丁寧に開けておきたい。物理の波形から、フレームの中身、そしてスイッチが「どこへ送るか」を学ぶ仕組みまで。

## 1. 線の上 ── 物理は、あの波形

いちばん下、線の上の話は、実はもう [EtherCAT の回](/docs/ethercat/)で開けている。EtherCAT が「物理は Ethernet を借りている」と言ったとおり、ここは共通だ。

おさらいすると ── バイトはビットになり、ビットは線の上の電圧（信号）として時間で流れる。よく使う 100BASE-TX なら、ツイストペア（より合わせた2本）で **差動**（[RS-485 と同じ理屈](/docs/rs485-modbus/)で、ノイズに強い）、しかも素朴な高/低ではなく **3値（MLT-3）＋4B5B** という符号化を一段かませている。下の widget（再掲）で、バイトが波形になり、エンディアンが時間の順に見え、最後に「本物の線はもう一段の符号化がある」まで、もう一度確かめられる。

<div class="demo-embed">
  <iframe src="/ethercat-wave/" title="バイトを波形で見る" loading="lazy"></iframe>
  <div class="cap"><span>ethercat-wave</span><a href="/ethercat-wave/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

せっかくなので、さっき名前だけ出した **「3値（MLT-3）＋4B5B」が何をしているのか**を、もう一段開けておこう。素朴な高/低（2値）でそのまま流さず、わざわざ二段の符号化をかませているのには、ちゃんと理由がある。受信側が抱える二つの悩み ──「**時計をどう合わせるか**」と「**線の帯域に収まるか**」── を、それぞれ片付けているんだ。

**4B5B ── 時計のための“息継ぎ”を混ぜる。** Ethernet には、UART の start ビットのような分かりやすい同期の合図がない。受信側は、信号の **変化（エッジ）そのものから時計を復元**している。ということは、0 が延々と続いて線が変化しないと、エッジが来なくて、受信の時計が迷子になる。そこで **4ビットを5ビットに置き換える**（決まった変換表で）。5ビット側のコードは「0 が長く続かない」ものだけを選んであって、これで必ず一定の間隔で変化が入る＝**受信が時計を見失わない**。代償は、4ビットを5ビットで運ぶので **25%の水増し**（だから 100Mbit/s のデータに、線の上では 125Mボー必要になる）。おまけに、5ビットで作れるコードは余るので、その余りを「アイドル」「フレームの開始/終了」みたいな**制御の合図**にも使える。

**MLT-3 ── 3つの高さで、周波数を下げる。** 4B5B で整えたビット列を、こんど線の電圧に乗せる。ここで素朴な2値（高/低）を使うと、1 が続くたびに高低がバタバタ反転して、**高い周波数**の信号になる ── 細いより線（Cat5）の帯域を食い、ノイズも撒く。MLT-3 は **−／0／＋ の3つの高さ**を使い、ルールはこうだ：**「1」のとき次の高さへ一段ずつ進み（…−→0→＋→0→−…）、「0」のときその場に留まる**。すると、1 が連続しても −,0,＋,0 と4ビットでひと巡りするので、**いちばん速い変化でも、ビット速度の 1/4 の周波数**で済む（2値の素朴な方形波なら 1/2）。125Mボーの信号が、実質 30MHz ちょっとの帯域に収まる ── だから普通の Cat5 ケーブルできれいに通り、放射ノイズも小さい。

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 480 200" width="480" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <!-- bit labels -->
  <text x="20" y="34" font-size="10" fill="#7d7568" text-anchor="end">bit</text>
  <text x="85" y="34" font-size="11" fill="#1d1b17" text-anchor="middle">1</text><text x="135" y="34" font-size="11" fill="#1d1b17" text-anchor="middle">1</text><text x="185" y="34" font-size="11" fill="#aaa49b" text-anchor="middle">0</text><text x="235" y="34" font-size="11" fill="#1d1b17" text-anchor="middle">1</text><text x="285" y="34" font-size="11" fill="#aaa49b" text-anchor="middle">0</text><text x="335" y="34" font-size="11" fill="#1d1b17" text-anchor="middle">1</text><text x="385" y="34" font-size="11" fill="#1d1b17" text-anchor="middle">1</text><text x="435" y="34" font-size="11" fill="#aaa49b" text-anchor="middle">0</text>
  <!-- NRZ (2値) -->
  <text x="52" y="68" font-size="9" fill="#7d7568" text-anchor="end" font-weight="bold">2値</text>
  <path d="M60,50 L160,50 L160,80 L210,80 L210,50 L260,50 L260,80 L310,80 L310,50 L410,50 L410,80 L460,80" fill="none" stroke="#b6ab99" stroke-width="2"/>
  <!-- MLT-3 level guides -->
  <line x1="55" y1="120" x2="462" y2="120" stroke="#ece3d6" stroke-width="1" stroke-dasharray="2 3"/>
  <line x1="55" y1="145" x2="462" y2="145" stroke="#ece3d6" stroke-width="1" stroke-dasharray="2 3"/>
  <line x1="55" y1="170" x2="462" y2="170" stroke="#ece3d6" stroke-width="1" stroke-dasharray="2 3"/>
  <text x="50" y="123" font-size="9" fill="#aaa49b" text-anchor="end">＋</text><text x="50" y="148" font-size="9" fill="#aaa49b" text-anchor="end">0</text><text x="50" y="173" font-size="9" fill="#aaa49b" text-anchor="end">−</text>
  <!-- MLT-3 (3値) -->
  <text x="52" y="148" font-size="9" fill="#3c7876" text-anchor="end" font-weight="bold">3値</text>
  <path d="M60,120 L110,120 L110,145 L210,145 L210,170 L310,170 L310,145 L360,145 L360,120 L460,120" fill="none" stroke="#3c7876" stroke-width="2.2"/>
  <text x="240" y="195" font-size="9" fill="#7d7568" text-anchor="middle">「1」で次の高さへ一段ずつ進む／「0」はその場に留まる ── 同じ 1 続きでも、3値なら変化がゆっくり</text>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">同じビット列を、素朴な2値（上）と MLT-3 の3値（下）で。2値は 1 のたびに高低を行き来して変化が速い。MLT-3 は −/0/＋ を一段ずつ辿るので、同じビットでも電圧の変化がゆっくり＝周波数が低い。線が運びやすく、ノイズも出にくい。</figcaption>
</figure>

つまり、**4B5B で「時計が迷子にならないだけの変化」を保証し、MLT-3 で「その変化を、線が運べる低い周波数に収める」**。受信の同期と、ケーブルの帯域 ── 物理層の二大悩みを、符号化の合わせ技で同時に片付けているわけだ。私はこの「2値を3値にするだけで、最高周波数が半分になる」あたりが、地味だけど効いていて好きだ。（ちなみに、もっと速い 1000BASE-T では、今度は4対すべてを使い、5値の PAM-5 ＋誤り訂正でさらに詰め込む。けれど発想は同じ ──「変化は十分に・周波数は低く・線に収まるように」符号を設計する、だ。）

つまり、Ethernet の物理層は「差動でノイズに強い線に、符号化したビットを流す」── ここまでの回で握った道具が、そのまま効いている。新しいのは、ここから上だ。

## 2. フレームと MAC ── 配達先の書き方

Ethernet が運ぶ一個の荷物を **フレーム**と呼ぶ。中身を頭から見ると、こうだ。

- **宛先 MAC アドレス**（6バイト）── 誰へ。
- **送信元 MAC アドレス**（6バイト）── 誰から。
- **EtherType**（2バイト）── 中身が何か（`0x0800`＝IP、`0x88A4`＝EtherCAT…）。
- **データ**（最大1500バイト程度）。
- **FCS**（4バイト）── 誤り検出（CRC）。

主役は **MAC アドレス**だ。これは機器の Ethernet 口ごとに、世界で一意に振られた48ビットの番地（例 `aa:bb:cc:00:00:01`）── 製造時に焼かれていて、原則かぶらない。CAN の「ID」や Modbus の「アドレス」が、ここでは「MAC」という名前で、配達の宛先になっている。

`EtherType` も覚えておきたい。これは「この箱の中身は何の規格か」の札だ。`0x0800` なら「中身は IP だよ」、`0x88A4` なら「中身は EtherCAT だよ」── [EtherCAT の回](/docs/ethercat/)で出てきた `0x88A4` は、まさにこれだった。下の widget（scapy）で、フレームを自分で組み立てて、流して、覗いてみよう。

<div class="demo-embed">
  <iframe src="/eth-code/" title="Ethernet をコードで" loading="lazy"></iframe>
  <div class="cap"><span>eth-code</span><a href="/eth-code/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

ここで「イーサ」という言葉のモヤを、いちど晴らしておこう。「Ethernet」と言ったとき、人は二つの違うものを指していることがある ── ひとつは、いま見た **線・MAC・フレームという土台そのもの**。もうひとつは、その土台の *上に載るもの*（EtherType で中身を切り替える、IP だの EtherCAT だの）。「`0x88A4` で Ethernet の上に直に乗る EtherCAT」と「IP→TCP を積む普通のネット」は、同じ土台を共有しつつ、上の中身が違うだけ、というわけだ。同じ「イーサ」でも、どの層の話かで意味が変わる。

## 3. スイッチ ── どこへ送るかを、学習する

さて、いちばん面白いところ。フレームに宛先 MAC を書いた ── でも、その MAC を持つ機器は、**どの線の先に居る**んだろう？ ネットワークは、それをどうやって知るのか。

昔の「ハブ」は、知らなかった。ある口から来たフレームを、残り全部の口へそのままばらまくだけ（フラッディング）。誰宛かを気にせず全員に配るので、無駄だし、皆が一本を共有して衝突もした ── CAN や RS-485 の「共有バス」に近い。

**スイッチ**は、ここを賢くする。スイッチは中に「**MAC アドレス → どの口**」の対応表を持っていて、フレームが流れるたびに **学習**する。コツは、学習に使うのが**送信元**だということ ── A（ポート1）からフレームが来たら、「A はポート1に居る」と表に書く。そして次に誰かが A 宛に送ったら、表を引いて **ポート1だけ**へ運ぶ。表が育つほど、無駄なばらまきが消えていく。下の widget で、空っぽの表が、フレームが流れるたびに育って、転送が一点に絞られていく様子を、手で追ってみてほしい。

<div class="demo-embed">
  <iframe src="/eth-switch/" title="スイッチの MAC 学習ラボ" loading="lazy"></iframe>
  <div class="cap"><span>eth-switch</span><a href="/eth-switch/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

学習するのは送信元 MAC、引くのは宛先 MAC ── この非対称が、ちょっと利いていて面白い。誰かが一度でも喋れば、その居場所が表に残る。だからネットワークは、最初こそ手探り（フラッディング）でも、トラフィックが流れるうちに、勝手に「誰がどこ」を覚えていく。中央に司令塔が居るわけじゃないのに、配達網が自己組織化していくのが、私はけっこう好きだ。

## 4. 全二重と、その先

スイッチで点対点になったことの、もう一つの大きな効能が **全二重**だ。共有バス（やハブ）では「一度に1台」「送受信どちらか」だったのが、スイッチの各口は、送信と受信を別々の線で同時にできる ── 衝突という概念そのものが消える。昔の Ethernet が悩んだ CSMA/CD（みんなで様子を見ながら喋り、ぶつかったらやり直す）は、もう要らなくなった。速くて、ぶつからない。

そして、ここが全ネットワークの土台になる。MAC で「どこへ」、EtherType で「中身は何か」── この素朴な枠の上に、次回はいよいよ **IP と TCP** を積む。EtherType を `0x0800` にして、中身の側に「世界中どこへでも届く住所と経路（IP）」と「落ちても届く再送と順番（TCP）」を載せる、あの巨大な仕組みだ。

土台はもう、君の手の内にある ── 差動の線、フレーム、MAC、スイッチの学習。次の階で、この上に「世界中とつながる」が乗る。通信の梯子も、いよいよ見晴らしのいい高さまで来た。
