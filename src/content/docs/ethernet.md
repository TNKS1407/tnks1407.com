---
title: "Ethernet ── 配達先を書いて、スイッチが運ぶ"
description: "共有バス（RS-485 / CAN）は、一本の線を皆で分け合った。Ethernet はそこを抜けて、点対点をスイッチで束ねる ── 各機器に世界で一意な MAC 番地を振り、フレームに『宛先』を書き、スイッチが『どの機器がどの口に居るか』を学習して、その口だけへ運ぶ。物理のあの波形から、フレームの中身、スイッチの学習までを開けてみる。この上に、次回 TCP/IP が積まれる。"
pubDate: 2026-06-29
tags: ["通信", "Ethernet", "MAC", "スイッチ", "イーサネット", "物理層"]
demo: "/eth-switch/"
demoLabel: "スイッチの MAC 学習ラボを全画面で開く"
series: "communication"
order: 5
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
