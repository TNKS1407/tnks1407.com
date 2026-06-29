---
title: "EtherCAT を開ける ── 線の上のビットから、マスタのループまで"
description: "産業用の高速ネットワーク EtherCAT を、ブラックボックスのまま使うんじゃなく、一層ずつ開けてみる。線の上のビット（君が知ってる波形）から、バイトの並び、マスタのループ、そして“通り抜けながら書き換える”専用チップまで ── ハードの勘が、そのままプログラミングの勘につながるように。触れる widget と、短いサンプルコードを所々に置いた。"
pubDate: 2026-06-29
tags: ["通信", "EtherCAT", "フィールドバス", "リアルタイム", "プロトコル", "産業ネットワーク"]
demo: "/ethercat/"
demoLabel: "EtherCAT の概念ラボを全画面で開く"
series: "communication"
order: 9
---

<style>
.code-sample{background:#fbf8f2;border:1px solid #e3dbd0;border-radius:8px;padding:.85rem 1rem;margin:1.3rem 0;font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.8;overflow-x:auto;color:#3a3835;white-space:pre;}
.code-sample .ck{color:#7a5ea8;}.code-sample .cf{color:#2563aa;}.code-sample .cs{color:#3c7876;}.code-sample .cn{color:#c9761f;}.code-sample .cc{color:#aaa49b;font-style:italic;}
.code-cap{font-size:.74rem;color:#aaa49b;font-family:'JetBrains Mono',monospace;margin:-.7rem 0 1.3rem;}
</style>

工場の制御盤の中に、一台のコントローラ（マスタ）と、サーボや I/O が一本のケーブルで数珠つなぎになっている ── そんな絵を思い浮かべてほしい。電源を入れると、全部のモータが、1ミリ秒ごとに、髪の毛一本ぶんのズレもなく一斉に動く。速くて、正確で、たくさんつないでも遅くならない。これが EtherCAT だ。

ハードを触ってきた人なら、線も、電圧も、チップも知っている。でも「プロトコル」や「マスタのプログラム」と聞くと、急に別世界の魔法に思えてくる ── その気持ちはよく分かる。だから、ここでは魔法にしない。**この箱を、一層ずつ開けていく。** 各層は、君がもう知っているハードの話の、ほんの少し上だ。線の上のビットから始めて、バイトの並び、マスタのループ、専用チップの中身まで降りていくと、最後には「自分でも実装できそうだ」と思えるところまで来る。

触れる widget を各層に一つずつ、短いサンプルコードも所々に置いた。読んで、つまみを回して、確かめながら進もう。

## 1. まず勘所 ── 通り抜けながら、全員ぶん

EtherCAT の一番の勘所は、たった一文だ。**一枚のフレームが鎖を通り抜けて、各機器が“自分のぶん”だけ、通りすがりに読み書きする。**

普通、たくさんの機器とやり取りするなら、こうする ── マスタが S1 に「データちょうだい」と聞いて、返事を待って、次に S2 に聞いて、待って……。機器が N 台なら N 回の往復だ。台数が増えるほど遅くなる（[RS-485 / Modbus](/docs/rs485-modbus/) で見た、あのポーリングだ）。

EtherCAT は、ここをひっくり返す。マスタは、全機器ぶんの欄をまとめて持った **一枚のフレーム** を流すだけ。フレームが鎖を端まで走り抜けるあいだに、各スレーブが「自分の番地の欄」だけを、流れの中で抜き取り・書き込む。一周で、全員ぶんが済む。N 台でも、フレームは一枚。

下の widget で、その“通り抜け”を手で動かしてみてほしい。列車（フレーム）が駅（スレーブ）を通過しながらバイトを出し入れする様子、台数を変えても一枚で済む様子、受け切り方式との速さ比べ、そして全軸が同じ時刻で動く様子まで、一通り触れる。

<div class="demo-embed">
  <iframe src="/ethercat/" title="EtherCAT の概念ラボ" loading="lazy"></iframe>
  <div class="cap"><span>ethercat</span><a href="/ethercat/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

「通り抜けながら書き換える」── これがどうやって物理的に可能なのかは、この記事の山場（§5）で開ける。まずは「一枚で全員ぶん」という勘所だけ、握っておこう。

## 2. 線の上では ── バイトは、時間で流れる波形

いちばん下の階から始めよう。フレームとは、結局なんだろう。

フレームは **バイトの列** だ。そしてバイトは **ビット** で、ビットは線の上では **電圧の高い／低いが、時間で並んだもの** ── つまり波形だ。ここはハードの人がいちばん安心できる場所だと思う。オシロで見てきた、あの波形。

たとえば 1 バイト `0x0C` は、ビットで書けば `0000 1100`。これが線の上では、低・低・低・低・高・高・低・低、という電圧の段々になって流れていく。バイトが紙の上の記号じゃなく、線を走る信号だ、というのが目で掴める。

ここで一つ、後で効いてくる話をしておく。**エンディアン**だ。複数バイトの数 ── たとえばアドレス `0x1000` ── を線に流すとき、どっちのバイトから先に出すか、という順番がある。EtherCAT（と Ethernet）は **リトルエンディアン**＝下位バイトが先。だから `0x1000` は、線の上では `00 10 00 00` の順に流れる。数の `0x1000` と、線の `00 10 00 00`。波形にすると、この“バイトの順番”が、そのまま“時間の左→右”として見えてくる。

<div class="demo-embed">
  <iframe src="/ethercat-wave/" title="バイトを波形で見る" loading="lazy"></iframe>
  <div class="cap"><span>ethercat-wave</span><a href="/ethercat-wave/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

ひとつ正直に言っておくと ── ここで見せている素朴な「高/低の2値（NRZ）」は、筋を掴むための姿だ。本物の 100BASE-TX のケーブルは、3つの電圧（MLT-3）を使い、4ビットを5ビットに化かす符号化（4B5B）やスクランブルもかけている（直流が偏らないように・同期が保てるように）。でも安心してほしい。**「バイト＝信号が、時間で流れる」という芯は、本当だ。** ここはさらに一段下の“符号化”の層、というだけ ── その中身（MLT-3 の3値と 4B5B が何をしているか）は、[Ethernet](/docs/ethernet/) の回でちゃんと開けた。ここでは、その一枚上で話を進める。

## 3. バイトの並びに、意味を約束する ── プロトコル

波形が「バイトの列」だと分かった。次は、**そのバイトの、どの位置が何の意味か** を決める段だ。これが「プロトコル」── 仰々しい言葉だけど、中身は *位置と意味の対応表* でしかない。

EtherCAT のフレームを、頭から開けるとこうなっている。

- **宛先／送信元 MAC**（各6バイト）── Ethernet の枠。ここは普通のネットと同じ。
- **EtherType `0x88A4`**（2バイト）── 「これは EtherCAT だ」という合図。普通のネットが IP を載せる位置に、EtherCAT は自分の印を置く。
- **ECAT ヘッダ** ── 中身の長さなど。
- そして **データグラム**（一つ以上）── ここが本体。`コマンド`（例 `0x0C` = LRW＝論理リードライト）、`インデックス`、`アドレス`（4バイト）、`長さ`、`データ`（各スレーブの欄）、最後に **WKC**（ワーキングカウンタ）。

WKC だけ補っておく。これは「何台のスレーブがこの欄を処理したか」の数で、フレームが鎖を通るたびに、処理した分だけ +1 されていく。帰ってきたフレームの WKC を見れば、期待した台数が応えたかが分かる ── 通信が生きているかの、いちばん素朴な健康診断だ。

下の widget で、実フレームを1バイトずつ色分けして開けられる。流すとデータ欄が埋まって WKC が増える様子も見られる。

<div class="demo-embed">
  <iframe src="/ethercat-frame/" title="フレームを1バイトずつ開ける" loading="lazy"></iframe>
  <div class="cap"><span>ethercat-frame</span><a href="/ethercat-frame/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

「位置と意味の対応表」を、コードで書くとどうなるか。Python の `struct.pack` を使うと、こうだ ── これがさっきのバイト列を、本当に組み立てるコードになる。

<pre class="code-sample"><span class="ck">import</span> struct

cmd, idx, addr, length = <span class="cn">0x0C</span>, <span class="cn">1</span>, <span class="cn">0x1000</span>, <span class="cn">3</span>   <span class="cc"># 0x0C = LRW（読んで書く）</span>
outputs = <span class="cf">bytes</span>([<span class="cn">0</span>, <span class="cn">0</span>, <span class="cn">0</span>])                  <span class="cc"># 各スレーブへの出力（最初は0）</span>

frame  = struct.<span class="cf">pack</span>(<span class="cs">'&lt;BBIH'</span>, cmd, idx, addr, length)   <span class="cc"># ヘッダ部</span>
frame += outputs + struct.<span class="cf">pack</span>(<span class="cs">'&lt;H'</span>, <span class="cn">0</span>)             <span class="cc"># データ + WKC欄(0)</span></pre>
<div class="code-cap">書式 '&lt;BBIH' は“詰め方のレシピ”。1文字＝1つの値のバイト幅で、B=1, H=2, I=4。頭の '&lt;' がリトルエンディアン（§2 の話）。</div>

`struct.pack('<BBIH', ...)` の `B B I H` は、それぞれの値を何バイトに詰めるかの指定だ（B=1バイト、H=2バイト、I=4バイト）。頭の `'<'` が、§2 で見たリトルエンディアン。アドレス `0x1000` がちゃんと `00 10 00 00` の順でバイトになる。プロトコルって、こういう「数を、約束した幅と順で、バイトに並べる」だけのことなんだ。

## 4. マスタは、埋めて・送って・読むループ ── 実装

フレームの作り方が分かれば、マスタのプログラムは、もう半分できている。マスタがやるのは、毎周期これだけだ ── **箱（フレーム）を埋めて、送って、帰りを待って、読む。** これを繰り返す。魔法はどこにもない。

<pre class="code-sample"><span class="ck">while</span> <span class="ck">True</span>:
    nic.<span class="cf">send</span>(frame)                          <span class="cc"># 送る</span>
    reply = nic.<span class="cf">recv</span>()                       <span class="cc"># 帰りを待つ</span>
    (wkc,) = struct.<span class="cf">unpack</span>(<span class="cs">'&lt;H'</span>, reply[<span class="cn">-2</span>:])   <span class="cc"># WKC を読む = 何台処理した?</span>
    inputs = reply[<span class="cn">8</span>:<span class="cn">8</span>+<span class="cn">3</span>]                       <span class="cc"># スレーブからの入力</span>

    outputs = <span class="cf">decide_next</span>(inputs)             <span class="cc"># 次の出力を決めて…</span>
    frame   = header + outputs + struct.<span class="cf">pack</span>(<span class="cs">'&lt;H'</span>, <span class="cn">0</span>)  <span class="cc"># また詰めて、回す</span></pre>
<div class="code-cap">マスタの芯。unpack は pack の逆＝バイトを数に戻す。これを 1kHz 等で回し続ける。</div>

`unpack` は `pack` の逆で、バイトを数に戻す操作だ。送ったフレームが帰ってきたら、末尾の WKC を読んで、ちゃんと全員処理したか確かめる。

<pre class="code-sample"><span class="ck">if</span> wkc != expected_wkc:
    <span class="cc"># 期待した台数が処理してない = どこか切れた / 応答がない</span>
    handle_error()</pre>

これだけ。コードとバイトとハードは、同じものの別の顔だ ── このことを下の widget で、コードの行を1行ずつ光らせながら、作られるバイトと並べて確かめられる。

<div class="demo-embed">
  <iframe src="/ethercat-code/" title="コードで書くと" loading="lazy"></iframe>
  <div class="cap"><span>ethercat-code</span><a href="/ethercat-code/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

ただし正直に言うと、この「毎周期のループ」は、*立ち上げが済んだ後* の話だ。電源を入れてから運転までには、もう少し長い段取りがある（§6）。実際には SOEM のようなライブラリが、その段取りと足回りを肩代わりしてくれるから、君の書くループはこんなに短く済む。

## 5. なぜスレーブだけ、特別なチップが要るのか ── ESC

ここが、この記事の山場だ。§1 で「通り抜けながら書き換える」と言った ── あれは、どうやって物理的に可能なんだろう。

答えは、スレーブの中の専用チップ **ESC**（EtherCAT Slave Controller）にある。普通の Ethernet チップ（MAC）と、何が違うのか。

普通の MAC は **store-and-forward** ── フレームを丸ごとバッファに受け切って、CRC を確かめてから、次へ送る。だから ①各機器で全長ぶん待つ（遅い）②受け切るまで、流れの中身に触れない。

ESC は **cut-through** ── 止めない。フレームのビットが片方のポートから入って、もう片方から出ていく、その通り抜ける *最中* に、ハードの専用ロジックが：

- 自分の番地（あらかじめ設定済み）の出力バイトが流れてきたら、抜き取って自分のメモリへ＝**読み**
- 入力の番地が来たら、そのバイトを自分のセンサ値で **上書き** して差し替え＝**書き**
- **WKC を +1**
- バイトを書き換えたぶん、末尾の **CRC も流れの中で計算し直す**

これを全部、線速（100Mbps）で、ns 級の遅れだけでやってのける。普通の MAC が同じことをできないのは、「流れているフレームから自分のバイトを止めずに見つける／途中で差し替える／CRC を流れの中で直す／いつも同じごく小さい遅れを保つ」── この回路を、持っていないからだ。だから EtherCAT スレーブには、必ず ESC（Beckhoff の ET1100、Microchip の LAN9252、あるいは FPGA）という専用シリコンが載っている。

> **EtherCAT の“速さ”の正体は、ソフトの工夫じゃなく、ハードに焼かれている。** 通り抜けながら処理する回路の差が、そのまま速さと同期の差になっている。

下の widget で、MAC（受け切ってから）と ESC（通り抜けながら）を並べて見られる。ESC の中で、バイトがセンサ値に差し替わり、WKC が増える瞬間がいちばんの見どころだ。

<div class="demo-embed">
  <iframe src="/ethercat-esc/" title="ESC ── 通り抜けながら書き換える" loading="lazy"></iframe>
  <div class="cap"><span>ethercat-esc</span><a href="/ethercat-esc/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

§2 の波形と、ここがつながる。ESC は文字どおり“流れている信号（波形）”を相手に、ビットが通過する瞬間に読んで・差し替えて・また線へ送り出している。普通の MAC は、波形が全部届くのを待ってから動く。ESC は、波形を通りすがりに書き換える ── これが「on the fly」の、信号レベルでの正体だ。

## 6. ループが回り出す前に ── 立ち上げと、時刻合わせ

§4 のループは“運転中”の姿だった。じゃあ、電源を入れてから運転までに、マスタは何をしているのか。ここが実装の“本体の長さ”で、ライブラリが肩代わりしてくれる部分でもある。

大きく三つ。**数えて、設定して、段を上げる。**

1. **数え上げ＆同定** ── 起動直後、マスタは位置アドレス（鎖の順番）で1台ずつ当てて数える。同時に各 ESC の EEPROM から「ベンダ／製品コード／版」を読み、ESI ファイルと突き合わせて「これは○○のサーボだ」と同定する。何台・どこに・何者か、をまず掴む。
2. **設定** ── 各スレーブの **FMMU** に「マスタの大きな論理アドレス空間の、この一切れが自分の番地」と割り当てる。これのおかげで、運転中は §1 のように *1個のデータグラムが全員ぶんを一度に* 出し入れできる。あわせて同期マネージャやメールボックスも設定する。
3. **状態の階段** ── 全スレーブを **Init → Pre-Op → Safe-Op → Op** と上らせる。段を上がるごとに「できること」が増える ── Pre-Op で設定（メールボックス経由）、Safe-Op で入力が見え、**Op で出力も動いて、毎周期のプロセスデータ（あのループ）が流れ出す。**

<div class="demo-embed">
  <iframe src="/ethercat-startup/" title="立ち上げ ── 数えて、名乗らせて、段を上げる" loading="lazy"></iframe>
  <div class="cap"><span>ethercat-startup</span><a href="/ethercat-startup/" target="_blank" rel="noopener noreferrer">全画面で開く ↗</a></div>
</div>

この段取りを、自分でゼロから書くのは大変だ。だから普通は SOEM（Simple Open EtherCAT Master）のようなライブラリを使う。雰囲気だけ見せると、こんな粒だ。

<pre class="code-sample"><span class="cc"># SOEM 風の擬似コード（立ち上げ）</span>
ec_config_init()          <span class="cc"># 数え上げ & 同定</span>
ec_config_map(io_map)     <span class="cc"># FMMU 設定 = 全 I/O を1枚のメモリに対応づけ</span>
ec_configdc()             <span class="cc"># 分散クロックを合わせる</span>

ec_slave[<span class="cn">0</span>].state = EC_STATE_OPERATIONAL
ec_writestate(<span class="cn">0</span>)          <span class="cc"># 全員を Op へ</span>
<span class="ck">while</span> <span class="ck">True</span>:
    ec_send_processdata()   <span class="cc"># ← ここから先が §4 のループ</span>
    ec_receive_processdata()</pre>
<div class="code-cap">立ち上げ（config_init→map→dc→Op）が済むと、あとは send/receive を回すだけ。芯は §4 と同じ。</div>

### 同じ時刻で動く ── 分散クロック

ひとつ、鋭い人が引っかかる点がある。「フレームは鎖を順に通るんだから、S1 と S10 では、データが届く時刻がズレるはずだ。なのに、なぜ全軸が一斉に動けるの？」── いい疑問だ。

種明かしはこう。**EtherCAT は「データが届く瞬間」と「実際に動く瞬間」を、切り離している。** マスタは立ち上げ時に、各スレーブまでのケーブル遅延を測って、全員の時計を合わせる（**分散クロック**、DC）。そして運転中、スレーブは *フレームが届いた時刻* ではなく、*みんなで合わせた共通の SYNC 時刻* に出力を適用する。だから、データの配達が多少バラついても、動く瞬間は全員そろう ── 軸が10個あっても、100ns 以内で一斉だ。

配達（バラつく）と、行動の合図（そろえる）を分ける。この一手が、EtherCAT の同期の核なんだ。私は、この「届くこと」と「動くこと」を別々に扱う割り切りが、けっこう美しいと思う。

## 7. どこに居るのか ── デイジーチェーンとも、TCP/IP とも違う

最後に、EtherCAT が通信の地図のどこに立っているかを置いておこう。両隣と比べると、輪郭がはっきりする。

**[RS-485](/docs/rs485-modbus/) のデイジーチェーン（Modbus など）と。** こちらは、共有の半二重バスに機器がぶら下がっていて、マスタが1台ずつポーリングする ── 「S1 さん？」「はい」「S2 さん？」「はい」…。N 台なら N 往復で、遅いし、時刻を合わせる仕組みもない。EtherCAT は、点対点の全二重を *1枚のフレームが通過処理* で1パス完了、しかも DC で同期。§1 でひっくり返した、と言ったのは、この古いやり方のことだ。

**[TCP/IP](/docs/tcp-ip/)・[EtherNet/IP](/docs/industrial-ethernet/) と。** こちらは Ethernet の上に IP（住所と経路）→ TCP（再送と順序）を積んだ、柔らかくて賢いネットだ。でも、その賢さ（再送・バッファ・経路）が、時刻の固さとは相性が悪い ── いつ届くかが、状況で変わる。EtherCAT は逆を行く。**IP も TCP も積まず**、Ethernet の物理層だけ借りて、その上に薄い専用層を一枚（EtherType `0x88A4`）載せ、処理は ESC のハードに焼く。柔らかさを捨てて、速さと固さ（決定論）を取った、という選択だ。

ここで「イーサネット」という言葉のモヤを一つ晴らしておくと ── EtherCAT が借りているのは Ethernet の **物理層**（線・PHY・100Mbps・フレームの枠）だけだ。「Ethernet の上で動く」と言っても、IP や TCP の世界とは別物で、store-and-forward のスイッチも通さない。同じ「イーサ」でも、中身はずいぶん違う ── この「“イーサ”と名のつくものたち」の地図は、[イーサって、結局なに？](/docs/ether-naming/) で一枚に描いた。EtherType も、EtherNet/IP の "IP" の正体も、あそこでほどける。

---

ここまでで、EtherCAT を六層 ── 勘所・波形・バイトの並び・コード・専用チップ・立ち上げ ── に開けてきた。一番下の線の上のビットから、一番上のマスタのループまで、ひと続きの坂としてつながったと思う。「通り抜けながら書き換える」という一行が、ESC のハードに支えられ、FMMU と分散クロックで全員ぶん・同時刻になり、たった数行のループから回る。

そして ── この記事は、[UART](/docs/uart/) の一本の線から始まった「通信のしくみ」の梯子を登りきった君が、いちばん最初にブラックボックスだった EtherCAT へ戻ってきて、その底（シリコン）まで開け切った、シリーズの締めくくりだ。下から積んできた石 ── start/stop の枠、アドレスで選ぶ、差動、エンディアン、層が層を包む ── が、ぜんぶこの一枚の中で、当たり前の顔をして使われていたことに、気づいただろうか。最初は魔法に見えた箱が、もう君の知っているものの延長として見えているなら、この梯子は役目を果たせたんだと思う。線の上のビットは、もう君の手の内にある。
