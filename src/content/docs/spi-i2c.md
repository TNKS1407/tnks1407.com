---
title: "SPI と I²C ── 時計の線を、引く"
description: "UART の次の一歩は、線を一本足すこと ── クロック（時計）の線だ。時計を共有すると、速さの約束も“真ん中で読む”も要らなくなる。基板の中でチップ同士を結ぶ二大定番、SPI（4本・全二重・線で選ぶ）と I²C（2本・アドレスで選ぶ）を、波形とコードで開けてみる。UART で握った勘が、そのまま効いてくる。"
pubDate: 2026-06-29
tags: ["通信", "SPI", "I2C", "同期式", "シリアル", "クロック"]
demo: "/spi/"
demoLabel: "SPI の波形ラボを全画面で開く"
series: "communication"
order: 2
---

<style>
.code-sample{background:#fbf8f2;border:1px solid #e3dbd0;border-radius:8px;padding:.85rem 1rem;margin:1.3rem 0;font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.8;overflow-x:auto;color:#3a3835;white-space:pre;}
.code-sample .ck{color:#7a5ea8;}.code-sample .cf{color:#2563aa;}.code-sample .cs{color:#3c7876;}.code-sample .cn{color:#c9761f;}.code-sample .cc{color:#aaa49b;font-style:italic;}
.code-cap{font-size:.74rem;color:#aaa49b;font-family:'JetBrains Mono',monospace;margin:-.7rem 0 1.3rem;}
</style>

[UART](/docs/uart/) で、いちばん素朴な「一本の線にバイトを乗せる」を見た。その最後に、UART の性格は「クロックの線を共有しない（非同期）」ことだ、と置いた。今日は、そこに**線を一本、足してみる**。足すのは、時計（クロック）の線だ。

たった一本だけど、これで景色が変わる。**速さを前もって約束する必要も、ビットの“真ん中”をねらって読む必要も、なくなる。** 時計の線が「いま、このビットを読め」と、一発ごとに教えてくれるからだ。この「時計を共有する」やり方を **同期式**（synchronous）と呼ぶ。基板の中で、マイコンとセンサ、マイコンと ADC、みたいにチップ同士を近くで結ぶときの定番が、ここで出てくる二つ ── **SPI** と **I²C** だ。

## 1. 時計の線を、引く ── SPI

SPI は線が **4本**。順に、CS（相手を選ぶ）、SCLK（クロック＝master が刻む時計）、MOSI（master→slave のデータ）、MISO（slave→master のデータ）。

UART との違いは、SCLK があること、これに尽きる。master が SCLK をカチカチ刻むと、その**エッジ（立ち上がり）に合わせて**データが読まれる。何ヘルツで叩こうが構わない ── 速さの約束が要らない。時計がぜんぶ決めてくれるからだ。しかも MOSI と MISO が別々にあるので、**送りながら同時に受ける**（全二重）。master と slave のシフトレジスタが輪のように繋がって、1ビットずつ入れ替わっていく。

下の widget で、4本の線 → クロック → エッジで読む → 同時に交換、と一歩ずつ組み上げてみてほしい。UART が「真ん中で読む」だったのに対し、SPI は「エッジで読む」── 時計があるから迷いがない、という所が見どころだ。

<div class="demo-embed">
  <iframe src="/spi/" title="SPI の波形ラボ" loading="lazy"></iframe>
  <div class="cap"><span>spi</span><a href="/spi/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

相手の選び方も UART と違う。SPI はアドレスを持たない。**CS の線を Low に落とした相手**とだけ話す。slave が複数なら、CS 線をそれぞれに引く ── 2台なら CS が2本、3台なら3本。速くて単純だけど、台数ぶん線が増えていくのが弱点だ。

## 2. 2本で、多数を ── I²C

その「線が増える」を嫌って、**たった2本**で多数を相手にするのが I²C だ。線は SDA（データ）と SCL（クロック）だけ。CS 線が無いぶん、相手は **アドレス**で選ぶ ── 同じ2本のバスに何台ぶら下げても、7ビットのアドレスで呼び分けられる。

2本しかないから、やり取りには作法が要る。SCL が High のあいだに SDA を動かすのは「合図」専用、と決めておく：SCL が High のまま SDA が下がったら **START**（始めるよ）、上がったら **STOP**（終わり）。その合図にはさまれた中で、SCL のリズムに乗せてビットを送る。

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 480 175" width="480" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <text x="8" y="42" font-size="11" fill="#2563aa" font-weight="bold">SDA</text>
  <text x="8" y="105" font-size="11" fill="#7a5ea8" font-weight="bold">SCL</text>
  <!-- START / STOP guide lines (SDA が SCL=High 中に動く) -->
  <line x1="95" y1="16" x2="95" y2="150" stroke="#e0c0b8" stroke-width="1" stroke-dasharray="3 3"/>
  <line x1="400" y1="16" x2="400" y2="150" stroke="#e0c0b8" stroke-width="1" stroke-dasharray="3 3"/>
  <!-- SDA: High → START(下げ) → データ → ACK(凹) → STOP(上げ) → High -->
  <path d="M40,32 L95,32 L95,60 L160,60 L160,32 L230,32 L230,60 L300,60 L300,32 L335,32 L335,62 L398,62 L398,60 L400,60 L400,32 L470,32" fill="none" stroke="#2563aa" stroke-width="2"/>
  <!-- SCL: High before START, 8パルス, High after STOP -->
  <path d="M40,95 L120,95 l0,28 l17,0 l0,-28 l17,0 l0,28 l17,0 l0,-28 l17,0 l0,28 l17,0 l0,-28 l17,0 l0,28 l17,0 l0,-28 l17,0 l0,28 l17,0 l0,-28 l17,0 l0,28 l17,0 l0,-28 l17,0 l0,28 l17,0 l0,-28 l17,0 l0,28 l17,0 l0,-28 l17,0 L470,95" fill="none" stroke="#7a5ea8" stroke-width="2"/>
  <!-- labels -->
  <text x="95" y="12" font-size="9" fill="#c2543d" text-anchor="middle">START</text>
  <text x="210" y="166" font-size="9.5" fill="#7d7568" text-anchor="middle">アドレス7bit + R/W</text>
  <text x="335" y="78" font-size="9" fill="#3c7876" text-anchor="middle">ACK</text>
  <text x="365" y="166" font-size="9.5" fill="#7d7568" text-anchor="middle">データ</text>
  <text x="400" y="12" font-size="9" fill="#c2543d" text-anchor="middle">STOP</text>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">I²C のやり取りの骨格（簡略）。SCL が High のまま SDA が下がる＝START、上がる＝STOP。その間に、アドレス（誰に）＋データを SCL のリズムで送る。受け取った側は1ビット分 SDA を Low に引いて「届いたよ（ACK）」を返す。2本で、選んで・送って・確かめる、を全部こなしている。</figcaption>
</figure>

もう一つ I²C 特有の作法に、**ACK** がある。1バイト送るごとに、受け取った側が SDA を1ビット分 Low に引いて「ちゃんと届いた」と返事をする。返事が無ければ（NACK）、その相手は居ないか、手一杯ということ。2本しかない線で、選んで・送って・確かめてを全部やるための、よくできた約束だ。

ちなみに、SDA と SCL は両端から「引っぱり下げる」ことしかできない作り（オープンドレイン）で、High に戻すのは外付けの抵抗（プルアップ）の仕事 ── だから I²C の基板にはたいてい、線を電源に吊る小さな抵抗が2本いる。…と、配線の細かい話に逸れかけたので、戻ろう。要は「2本・アドレス・ACK 付き」が I²C の顔だ、と握っておけばいい。

## 3. コードでは ── 線で選ぶか、アドレスで選ぶか

性格の違いは、コードにそのまま出る。SPI は CS の線で相手を選んで「送る＝受ける」、I²C はアドレスで相手を選んで「そのレジスタを読む」。下の widget で1行ずつ。

<div class="demo-embed">
  <iframe src="/spi-code/" title="SPI / I²C をコードで" loading="lazy"></iframe>
  <div class="cap"><span>spi-code</span><a href="/spi-code/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

I²C の「アドレスで呼ぶ」は、実物だと気持ちがいい。バスにぶら下がっている相手を、総当たりで呼んでみて、返事（ACK）があったアドレスだけ拾えば、**つながっている全員の名簿**ができる ── `i2cdetect` というツールがやっているのは、これだ。

<pre class="code-sample"><span class="cc"># I²C バスに居る相手を、アドレス総当たりで探す</span>
<span class="ck">import</span> smbus
bus = smbus.<span class="cf">SMBus</span>(<span class="cn">1</span>)
<span class="ck">for</span> addr <span class="ck">in</span> <span class="cf">range</span>(<span class="cn">0x03</span>, <span class="cn">0x78</span>):
    <span class="ck">try</span>:
        bus.<span class="cf">read_byte</span>(addr)      <span class="cc"># ACK が返れば…居る</span>
        <span class="cf">print</span>(<span class="cs">f'見つけた: {addr:#04x}'</span>)
    <span class="ck">except</span> OSError:
        <span class="ck">pass</span>                  <span class="cc"># 返事なし＝そのアドレスには誰も居ない</span></pre>
<div class="code-cap">アドレスで呼べる＝総当たりで名簿が作れる。SPI（CS 線で選ぶ）には無い芸当だ。</div>

## 4. どこに居るのか ── 近くて速い、その先へ

SPI と I²C は、どちらも **同期式**（時計を引く）で、得意は **基板の中・近距離**。その上で、二つは性格が分かれる。

- **SPI** ── 速い・全二重・単純。代わりに線が多め（4本＋相手ごとに CS）。ADC やディスプレイ、フラッシュメモリみたいに、速さが欲しい相手に向く。
- **I²C** ── 2本だけ・アドレスで多数。代わりに遅め・作法多め。温度センサや小さな EEPROM みたいに、たくさんの小物をちょい読みする相手に向く。

UART（非同期・1対1・線が少ない）と並べると、三者の住み分けが見えてくる。「時計を共有する／しない」「線で選ぶ／アドレスで選ぶ」── この二つの軸で、だいたい整理できる。

ただし SPI も I²C も、想定しているのは **基板の上の、数センチ〜十数センチ**だ。クロックを共有する以上、線が長くなるとエッジが鈍り、ノイズに弱くなる。基板の外 ── 機械の上のセンサまで、この「点対点」を持ち出したくなると、別の作りが要る。

そこで次は、基板を出る。いつものセンサの3本線をそのまま使いながら、その同じ線でセンサに**しゃべらせる** ── **[IO-Link](/docs/io-link/)** へ進む。面白いことに、その中身は第一歩の UART そのものだ。点対点のまま、ただのスイッチを“賢いセンサ”にする一段。そこまで「1対1」を見届けたら、いよいよ一本のバスに大勢を・長い距離でぶら下げる世界（RS-485）へ向かう。土台に、もう一段を積もう。
