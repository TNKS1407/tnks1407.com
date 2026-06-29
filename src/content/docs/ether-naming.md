---
title: "イーサって、結局なに？ ── 紛らわしい名前の地図"
description: "通信を調べると、Ethernet・EtherType・EtherNet/IP・EtherCAT・PROFINET… 似た“Ether”が次々出てきて、どれがどれだか分からなくなる。でも、こんがらがるのは中身じゃなくて名前のほうだ。『どの層の話か』『誰が作ったか』『TCP/IP を使うか』── この3つで切ると、全部が一枚の地図にきれいに収まる。コースを登る前の（あるいは迷ったとき戻ってくる）、見取り図。"
pubDate: 2026-06-29
tags: ["通信", "地図", "Ethernet", "EtherNet/IP", "EtherCAT", "PROFINET", "命名"]
series: "communication"
order: 0
---

<style>
.name-table{width:100%;border-collapse:collapse;margin:1.4rem 0;font-size:.8rem;}
.name-table th{background:#f0ece6;color:#1d1b17;font-weight:700;text-align:left;padding:.5rem .6rem;border:1px solid #e3dbd0;font-family:'JetBrains Mono',monospace;font-size:.72rem;}
.name-table td{padding:.5rem .6rem;border:1px solid #e3dbd0;vertical-align:top;line-height:1.55;}
.name-table tr:nth-child(even) td{background:#faf8f4;}
.name-table .nm{font-weight:700;color:#3c7876;white-space:nowrap;}
.name-table .yes{color:#c2543d;font-weight:700;}
.name-table .no{color:#2563aa;font-weight:700;}
</style>

通信のことを調べはじめると、すぐにこの壁にぶつかる ── **Ethernet、EtherType、EtherNet/IP、EtherCAT、PROFINET、Ethernet POWERLINK…** 似たような "Ether" が次々に出てきて、どれが何の仲間で、どこが違うのか、頭の中で団子になる。

でも、安心してほしい。こんがらがっているのは、**中身じゃなくて名前のほう**だ。中身は、このコースで一段ずつ開けてきた（あるいはこれから開ける）もので、ちゃんと別物として並んでいる。名前が似ているせいで、近くに見えているだけ。

ほぐすのに要るのは、たった3つの問いだ ── **どの層の話か／誰が作ったか／TCP/IP を使うか**。この3本の物差しを当てると、紛らわしい名前が、すっと地図に収まる。コースを登る前の見取り図として、あるいは途中で迷子になったとき戻ってくる地図として、置いておくよ。

## 1. まず、土台の Ethernet

いちばん大事な切り分けは、これ。**「Ethernet」そのものと、「Ethernet を名乗る産業ネットワーク」は、別の層の話**だ。

**Ethernet**（IEEE 802.3）は、**土台**だ。線・コネクタ・信号（PHY）、機器ごとの MAC 番地、宛先を書いた**フレーム**、そして「中身は何か」を示す **EtherType** ── この「ラベル付きの封筒を線に乗せ、スイッチが配る」仕掛けそのものを指す。[Ethernet の回](/docs/ethernet/)で開けた、あれだ。あとに出てくる "Ether-なんとか" は、ほぼ全部、**この土台を借りて、その上に何かを乗せている**。

ここで一個、罠をつぶしておく。**EtherType は「プロトコル」ではなく、フレームの中の2バイトの“中身ラベル”**だ。0x0800 なら中身は IPv4、0x0806 なら ARP、0x86DD なら IPv6、0x88A4 なら EtherCAT、0x8892 なら PROFINET ── という具合に、「封筒の中に何が入っているか」を示す番号にすぎない。"EtherType" を見たら「Ethernet の一種」ではなく「中身の種類を書く欄」と思えばいい。

## 2. 土台の上の、二つの行き方

では、土台の上に何を乗せるか。産業ネットワークの答えは、大きく**二派**に分かれる（[産業 Ethernet の回](/docs/industrial-ethernet/)で見た景色を、ここでは名前の整理として置き直す）。

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 480 250" width="480" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <!-- foundation bar -->
  <rect x="20" y="196" width="440" height="40" rx="6" fill="#e6f0ef" stroke="#3c7876" stroke-width="1.5"/>
  <text x="240" y="214" font-size="11" fill="#1d1b17" text-anchor="middle" font-weight="bold">物理 Ethernet（IEEE 802.3）</text>
  <text x="240" y="229" font-size="8.5" fill="#7d7568" text-anchor="middle">線・PHY・MAC・フレーム・EtherType ── みんなの土台</text>
  <!-- left column: keep standard stack -->
  <rect x="34" y="92" width="190" height="92" rx="6" fill="#faf8f4" stroke="#2563aa" stroke-width="1.3"/>
  <text x="129" y="110" font-size="10" fill="#2563aa" text-anchor="middle" font-weight="bold">① 標準スタックを残す</text>
  <rect x="50" y="146" width="158" height="28" rx="4" fill="#fff" stroke="#cdd8e6"/>
  <text x="129" y="164" font-size="9" fill="#7d7568" text-anchor="middle">TCP / UDP / IP（そのまま）</text>
  <text x="129" y="132" font-size="9.5" fill="#1d1b17" text-anchor="middle">EtherNet/IP・Modbus TCP</text>
  <!-- right column: bypass / special -->
  <rect x="256" y="92" width="190" height="92" rx="6" fill="#faf8f4" stroke="#c2543d" stroke-width="1.3"/>
  <text x="351" y="110" font-size="10" fill="#c2543d" text-anchor="middle" font-weight="bold">② 速さのため作り変える</text>
  <rect x="272" y="146" width="158" height="28" rx="4" fill="#fff" stroke="#e6cdc6"/>
  <text x="351" y="164" font-size="8.5" fill="#7d7568" text-anchor="middle">TCP/IP を迂回 / 専用層</text>
  <text x="351" y="132" font-size="9" fill="#1d1b17" text-anchor="middle">EtherCAT・PROFINET・POWERLINK</text>
  <!-- legs to foundation -->
  <line x1="129" y1="184" x2="129" y2="196" stroke="#2563aa" stroke-width="1.3"/>
  <line x1="351" y1="184" x2="351" y2="196" stroke="#c2543d" stroke-width="1.3"/>
  <!-- title -->
  <text x="240" y="30" font-size="11" fill="#1d1b17" text-anchor="middle" font-weight="bold">同じ土台 ── 上で「便利さ」と「速さ」のどちらを取るか</text>
  <text x="240" y="50" font-size="9" fill="#7d7568" text-anchor="middle">① つながりやすさを取る（柔らかい）　／　② 時刻の揺れを消す（硬い）</text>
  <line x1="240" y1="60" x2="240" y2="88" stroke="#e3dbd0" stroke-width="1" stroke-dasharray="3 3"/>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">同じ物理 Ethernet の上で、二つの行き方に分かれる。① は標準の TCP/IP をそのまま残して、その上に産業の言葉を乗せる（EtherNet/IP、Modbus TCP）＝つながりやすいが、時刻はきっちり揃わない。② は速さのために標準スタックを迂回・作り変える（EtherCAT、PROFINET の RT/IRT、POWERLINK）＝揃うが、専用の仕掛けが要る。名前は似ていても、立っている層と選んだ割り切りが違う。</figcaption>
</figure>

**①「標準スタックを残す」派**は、TCP/IP をそっくりそのまま使い、その上に産業の言葉を乗せる。代表が **EtherNet/IP** と **Modbus TCP**。普通のネットと素直につながるかわり、時刻はきっちりは揃わない（ソフトなリアルタイム）。

**②「速さのため作り変える」派**は、揺れを消すために標準スタックを迂回したり、専用の処理を足したりする。代表が **EtherCAT**、**PROFINET**（の RT/IRT）、**POWERLINK**。硬く・速いかわり、専用の仕掛けが要る。

## 3. 名前の早見表

3つの物差し（どの層・誰が・TCP/IP を使うか）で、主役たちを一枚に並べると、こうなる。

<table class="name-table">
<thead><tr><th>名前</th><th>正式には</th><th>どの層の話か</th><th>誰が</th><th>TCP/IP</th></tr></thead>
<tbody>
<tr><td class="nm">Ethernet</td><td>（固有名・IEEE 802.3）</td><td>物理〜データリンク＝<b>土台そのもの</b></td><td>IEEE</td><td>──</td></tr>
<tr><td class="nm">EtherType</td><td>（フレーム内の型フィールド）</td><td>フレームの中の<b>2バイトの欄</b>（中身ラベル）</td><td>IEEE</td><td>──</td></tr>
<tr><td class="nm">EtherNet/IP</td><td>EtherNet <b>Industrial Protocol</b></td><td>TCP/UDP/IP の上の応用層（CIP）</td><td>ODVA（Rockwell系）</td><td class="yes">使う</td></tr>
<tr><td class="nm">Modbus TCP</td><td>Modbus over TCP</td><td>TCP/IP の上に、あの Modbus を載せる</td><td>Modbus Org</td><td class="yes">使う</td></tr>
<tr><td class="nm">EtherCAT</td><td>Ethernet for <b>Control Automation Technology</b></td><td>Ethernet 枠を借り、IP/TCP は積まない</td><td>Beckhoff／ETG</td><td class="no">使わない</td></tr>
<tr><td class="nm">PROFINET</td><td><b>Process Field Net</b></td><td>Ethernet 上。周期 RT は TCP/IP を迂回</td><td>Siemens／PI</td><td>一部だけ</td></tr>
<tr><td class="nm">POWERLINK</td><td>Ethernet POWERLINK</td><td>Ethernet 上、時間割で送る専用方式</td><td>B&amp;R／EPSG</td><td class="no">使わない</td></tr>
</tbody>
</table>

この表でいちばん効くのが、**EtherNet/IP の "IP" は Internet Protocol ではなく Industrial Protocol** という一行だ。これは本当に紛らわしくて、しかも EtherNet/IP は**実際に**インターネットの IP（Internet Protocol）の上でも動くから、二重にややこしい。けれど名前の "IP" が指しているのは「産業用プロトコル（CIP）」のほう。表記が "Ethernet/IP" でも "EtherNet/IP" でも同じものを指していて、ODVA が「Net/IP＝産業の意味」を強調したくて大文字を散らしているだけ、と思えばいい。

## 4. ほぐし方 ── 新しい "Ether-X" に出会ったら

整理しておくと、これからどこかで知らない "Ether-なんとか" に出会っても、3つ問えば、たいてい棚に収まる。

1. **どの層の話か？** ── 土台の物理 Ethernet そのもの？　フレームの中の一フィールド？　それとも土台の上に建てたシステム？
2. **誰が作ったか？** ── ベンダや団体（Beckhoff／Siemens／ODVA…）。これがエコシステム（対応機器や工具）を決める。
3. **TCP/IP を使うか？** ── 標準スタックをそのまま使う＝柔らかく繋がりやすい。迂回・専用化する＝硬く時刻が揃う。

層・出自・割り切り。この3つで、名前の団子はだいたいほどける。

## 5. 地図を手に、登る

こうして並べ直すと、"Ether" の山は、もう怖くない。**土台が一つあって、その上での割り切りが何通りかあるだけ**だ。

- 土台の物理 Ethernet は **[Ethernet の回](/docs/ethernet/)**（コースの中ほど）で。
- 「便利さ vs 速さ」の二派が並ぶ景色は **[産業 Ethernet の回](/docs/industrial-ethernet/)**（コースの終盤）で。
- その②派のいちばん深いところ、専用シリコンまで降りる **[EtherCAT の回](/docs/ethercat/)**（コースの最後）で。

名前が、いちばん最初のブラックボックスだったわけだ。開けてみれば、中身は「一枚の土台と、いくつかの選択」── それだけだった。地図はここに置いておくから、登っている途中で名前に迷ったら、いつでも戻ってきていいよ。
