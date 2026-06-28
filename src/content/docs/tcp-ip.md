---
title: "TCP/IP ── 世界中とつながる、落ちても届く"
description: "Ethernet は隣近所（MAC）までだった。その枠の中身を IP にすると、世界中どこへでも届く『住所と経路』が手に入り、さらに TCP を重ねると『落ちても届く・順番も守る』信頼が乗る。握手・再送・並べ直しの仕組みと、その代償＝“いつ届くかが揺れる”を開けてみる。これが、EtherCAT がわざわざ TCP/IP を積まなかった理由でもある。"
pubDate: 2026-06-29
tags: ["通信", "TCP/IP", "IP", "TCP", "EtherNet/IP", "ネットワーク"]
demo: "/tcp-reliable/"
demoLabel: "TCP の信頼性ラボを全画面で開く"
series: "communication"
order: 6
---

<style>
.code-sample{background:#fbf8f2;border:1px solid #e3dbd0;border-radius:8px;padding:.85rem 1rem;margin:1.3rem 0;font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.8;overflow-x:auto;color:#3a3835;white-space:pre;}
.code-sample .ck{color:#7a5ea8;}.code-sample .cf{color:#2563aa;}.code-sample .cs{color:#3c7876;}.code-sample .cn{color:#c9761f;}.code-sample .cc{color:#aaa49b;font-style:italic;}
.code-cap{font-size:.74rem;color:#aaa49b;font-family:'JetBrains Mono',monospace;margin:-.7rem 0 1.3rem;}
</style>

[Ethernet](/docs/ethernet/) の回で、フレームに「宛先 MAC」を書いて、スイッチがそれを運ぶところまで来た。でも MAC で届くのは、同じネットワークの中 ── いわば隣近所まで、だ。世界の反対側のサーバには、MAC だけでは届かない。

そこで、フレームの中身（EtherType `0x0800` の中身）に **IP** を入れる。すると「世界中での住所と、そこへ至る経路」が手に入る。さらにその上に **TCP** を重ねると、「途中で落ちても最終的に届く、順番も守る」信頼が乗る。── この二段重ね **TCP/IP** が、いまの世界中のネットワークの背骨だ。今日はこれを開けて、最後に「じゃあ、なぜ EtherCAT はこれを積まなかったのか」まで、ひと続きで見ていく。

## 1. IP ── 世界中の住所と、経路

MAC アドレスが「機器に焼かれた、変わらない番地」だったのに対し、**IP アドレス**（例 `192.168.1.10` や、いまは `2001:db8::1` のような長いやつ）は、「いま、どのネットワークのどこに居るか」を表す住所だ。引っ越せば変わる、住民票みたいなもの。

IP のえらいところは **経路（ルーティング）**だ。宛先 IP を見て、「自分のネットワークの外なら、とりあえず出口（ルータ）へ渡す」を繰り返すと、世界中のルータがバケツリレーして、最終的に相手まで届く。各ルータは世界全体の地図を持っているわけじゃなく、「次にどっちへ渡すか」だけを知っていればいい ── この“ご近所の判断の連鎖”だけで地球の裏側まで届くのが、私はけっこう不思議で、好きなところだ。

ここで大事なのが、**層が層を包む**という構造だ。アプリのデータを TCP が包み、それを IP が包み、さらにそれを Ethernet フレームが包む ── 入れ子の弁当箱みたいになっている。

<figure style="margin:1.6rem 0;text-align:center;">
<svg viewBox="0 0 480 150" width="480" style="max-width:100%;height:auto;font-family:'JetBrains Mono',monospace;">
  <rect x="10" y="20" width="460" height="110" rx="8" fill="#eef3ee" stroke="#3c7876" stroke-width="1.6"/>
  <text x="20" y="36" font-size="9.5" fill="#3c7876" font-weight="bold">Ethernet フレーム</text>
  <text x="20" y="118" font-size="8" fill="#7d7568">宛先/送信元 MAC・EtherType=0x0800・…・FCS</text>
  <rect x="40" y="44" width="400" height="64" rx="7" fill="#eaf1f0" stroke="#2563aa" stroke-width="1.5"/>
  <text x="50" y="59" font-size="9.5" fill="#2563aa" font-weight="bold">IP パケット</text>
  <text x="50" y="100" font-size="8" fill="#7d7568">送信元/宛先 IP（住所と経路）</text>
  <rect x="70" y="66" width="340" height="34" rx="6" fill="#f3eef7" stroke="#7a5ea8" stroke-width="1.5"/>
  <text x="80" y="80" font-size="9" fill="#7a5ea8" font-weight="bold">TCP</text>
  <text x="135" y="80" font-size="8" fill="#7d7568">ポート・seq・ack（再送と順番）</text>
  <rect x="250" y="71" width="152" height="24" rx="5" fill="#fdf3e3" stroke="#c9761f" stroke-width="1.4"/>
  <text x="326" y="86" font-size="9" fill="#c9761f" text-anchor="middle" font-weight="bold">データ（HTTP 等）</text>
</svg>
<figcaption style="font-size:.8rem;color:#aaa49b;margin-top:.3rem;">層が層を包む（カプセル化）。アプリのデータを TCP が包み（ポート・順番）、それを IP が包み（世界中の住所）、いちばん外を Ethernet フレームが包んで（MAC で隣へ）運ぶ。受け取った側は、外から順に開けていく。各層は「自分の仕事」だけして、中身には口を出さない ── この分業が、巨大な仕組みを見通しよく保っている。</figcaption>
</figure>

受け取った側は、外側から順に開けていく ── Ethernet が「自分宛だ」と確かめて中の IP を取り出し、IP が「自分宛だ」と確かめて中の TCP を取り出し、TCP が順番を整えてアプリにデータを渡す。各層は自分の札（MAC／IP／ポート）だけ見て、中身には口を出さない。この潔い分業が、ネットワークを見通しよくしている。

## 2. TCP ── 落ちても届く、順番も守る

IP は「とりあえず宛先へ向けて投げる」までしか約束しない。途中で落ちても、順番が入れ替わっても、知らんぷり（これを「ベストエフォート」という）。その上に乗って、**信頼**を作るのが TCP だ。

TCP のやることは三つ。**① 握手して接続を張り（3ウェイ・ハンドシェイク）、② 1つずつ通し番号(seq)をつけて送り、受け手は「ここまで届いた」と ACK を返し、③ ACK が返らなければ、時間切れで送り直す（再送）。** 番号のおかげで順番も保証できる。下の widget で、握手・番号つき送信・再送までを、シーケンス図で一歩ずつ追ってみてほしい。

<div class="demo-embed">
  <iframe src="/tcp-reliable/" title="TCP の信頼性ラボ" loading="lazy"></iframe>
  <div class="cap"><span>tcp-reliable</span><a href="/tcp-reliable/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

この再送こそが、TCP が「信頼できる」理由だ。だけど ── ここに、産業の世界では効いてくる落とし穴がある。**再送が起きると、その分だけ到達が遅れる。** ふだんは速くても、たまたまパケットが落ちた回だけ、タイムアウトを待って送り直すぶん、ぐっと遅くなる。つまり TCP は「**必ず届くが、いつ届くかは状況で揺れる**」。この“揺れ”が、後で EtherCAT の話につながる。

なお、信頼より速さが欲しい用途（音声・動画・ゲーム）では、再送しない **UDP** を使う。落ちたら落ちたまま、でも遅れない。TCP と UDP は「信頼を取るか、即時性を取るか」の二択だ、と握っておけばいい。

## 3. コードでは ── socket だけ書けばいい

これだけ大層な仕組みなのに、コードから触ると拍子抜けする。Python の `socket` で、繋いで・送って・受け取るだけ。握手も再送も並べ直しも、ぜんぶ下の層がやってくれる。下の widget で1行ずつ。

<div class="demo-embed">
  <iframe src="/tcp-code/" title="TCP/IP をコードで" loading="lazy"></iframe>
  <div class="cap"><span>tcp-code</span><a href="/tcp-code/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

`connect` を呼べば握手が走り、`sendall` は送り切るまで面倒を見て、`recv` では順番のそろったバイトの流れだけが返ってくる。下でどれだけ苦労していても、アプリから見えるのは「信頼できる、まっすぐな土管」だ。層が苦労を引き受けてくれるから、上が素っ気なくいられる ── これが TCP/IP の、いちばんありがたい設計だと思う。

## 4. EtherNet/IP と、EtherCAT の分かれ道

産業の世界にも、この TCP/IP の上に乗る通信がある。代表が **EtherNet/IP**（IP は Internet Protocol でなく *Industrial Protocol* の略、というややこしい命名だ）。中身は **CIP** という産業用の言葉で、それを普通の TCP/UDP/IP に載せている。だから普通の Ethernet 機器・スイッチがそのまま使えて、柔軟で、導入しやすい。

でも、ここまで来たら、もう分かるはずだ。TCP/IP に乗るということは、あの **“いつ届くか揺れる”を引き受ける**ということ。再送やバッファや経路の都合で、到達時刻がばらつく。多くの用途ではそれで十分だけど、「1ミリ秒ごとに、髪の毛一本のズレもなく全軸を動かす」みたいな硬いリアルタイムには、向かない。

そこで [EtherCAT](/docs/ethercat/) は、逆を選んだ。**IP も TCP も積まず**、Ethernet の物理層だけ借りて、その上に薄い専用層を一枚（EtherType `0x88A4`）載せ、処理を ESC のハードに焼いた。柔らかさ（世界中とつながる・経路を選ぶ・落ちても届く）を捨てて、速さと固さ（決定論）を取った ── TCP/IP が積み上げた「便利さ」を、あえて全部降ろした選択だったわけだ。同じ Ethernet の物理の上で、片や世界中へ柔らかく、片や工場で硬く正確に。どちらが上でも下でもなく、目的が違う。

これで、通信の梯子は、いちばん素朴な一本の線（UART）から、世界中をつなぐ TCP/IP、そして硬い産業ネット（EtherCAT）まで、ひと続きに見渡せる高さに来た。次は、その産業 Ethernet の世界をもう少し広げて（PROFINET など、EtherCAT の隣人たち）、この長い梯子を締めくくろう。下の石は、もう全部、君の手の内にある。
