# TMC5240 ステッピングモータ駆動 子基板 — 設計書 Rev.2

JLCPCB 発注（PCBA、LCSC 在庫部品）前提。ホストは Raspberry Pi Pico（3.3V / SPI）。

**Rev.2 変更点:** エンコーダ後付け対応（J4 追加、ENCA/B/N を GND 直結→ヘッダ＋10k プルダウンに変更）、UART_EN を GND 直結→ハンダジャンパ SJ1（既定 GND=SPI）に変更。

| 項目 | 値 |
|---|---|
| モータ | バイポーラ2相、定格 1.5 A/相、巻線 2.8 Ω |
| 電源 VS | 24 V 単一入力、想定最大 2 A |
| ホスト I/F | 4線 SPI（UART_EN = GND で選択） |
| VCC_IO | 3.3 V（Pico 3V3） |
| コイル電流 | 1.5 A RMS（R_IREF 12 kΩ + GLOBALSCALER=181 + IRUN=31） |
| モード | StealthChop2 ＋ StallGuard4 センサレス原点出し |
| 成果物 | `schematic.svg`（回路図）, `bom_jlcpcb.csv`（JLCPCB用BOM）, 本書 |

## Rev.0 ドラフトからの訂正（データシート・実設計クロスチェックの結果）

初版の一般論ベースの想定から、以下を**訂正**した。根拠は ADI 公式データシート（検索抽出）、公式 TMC-API レジスタ定義、および独立した2つの公開リファレンス設計（KiCad ネットリストを直接照合）。

1. **VSA ピンは存在しない** → VSA 用 RC/フェライトフィルタを削除。アナログ系は AGND ピンのみ分離。
2. **内蔵レギュレータは 1.8V コア（VDD1V8 ピン）**であり 5V ではない → 2.2 µF を AGND へ。出力専用・負荷接続禁止。
3. **チャージポンプのリザーバは VCP–VS 間 1.0 µF**（100nF ではない）。フライングは CPO–CPI 間 22 nF/50V。
4. **SD_MODE / SPI_MODE ピンは存在しない**。インターフェース選択は UART_EN のみ（GND=SPI）。STEP/DIR ピン自体が無い（内蔵ランプジェネレータ専用）。
5. **SLEEPN（内部プルダウン）を H に吊る必要がある**。唯一の高電圧トレラント制御ピン。本設計では 3V3 へ直結。
6. **CSN は内部プルダウン**（UART アドレスストラップ兼用）→ MCU ブート中の誤選択防止に 10 kΩ プルアップを追加。
7. RDSon 実測値（HS 0.12 Ω + LS 0.11 Ω @3A レンジ）により**損失見積を 2.7 W → 約 1.0〜1.5 W に下方修正**。
8. パッケージは **TQFN-32 5×5（TMC5240ATJ+）と TSSOP-38（AUU+）のみ**。TQFP32 は存在しない。JLCPCB 在庫があるのは TQFN-32 リール品。

## 1. 電流設計（計算根拠）

```
IFS = KIFS / R_IREF            KIFS: 1Aレンジ 11.75, 2Aレンジ 24, 3Aレンジ 36 [A·kΩ]
I_RMS = (GLOBALSCALER/256) × ((CS+1)/32) × IFS/√2
```

- 目標 1.5 A RMS → ピーク 1.5×√2 = **2.12 A** → 2A レンジ（最大 2.0 A ピーク）では不足 → **3A レンジ**。
- **R_IREF = 12 kΩ ±1%** → IFS = 36/12 = **3.0 A**（IREF ピン電圧 ≈0.9 V、許容 12–60 kΩ※下記「要確認」参照）。
- CS(IRUN) = 31 固定（CoolStep の動作余地を確保）、GLOBALSCALER で合わせ込み:
  `1.5 = (GS/256) × 1 × 3.0/√2 → GS = 256×0.7071 ≈ 181 (0xB5)` — 推奨帯 128–255 内。
- IFS 3.0 A はデバイス定格（2 A RMS / 3 A ピーク）の範囲内、運転 1.5 A RMS も連続定格内。

**レジスタ初期値（TMC-API 名）**

| レジスタ | 値 | 意味 |
|---|---|---|
| DRV_CONF.CURRENT_RANGE | 2 (=3A) | フルスケールレンジ |
| GLOBALSCALER | 181 | 3.0A×0.707 → 2.12A ピーク |
| IHOLD_IRUN.IRUN | 31 | 1.5 A RMS |
| IHOLD_IRUN.IHOLD | 10 | 保持 ≈0.5 A RMS（発熱低減、要調整） |
| GCONF.en_pwm_mode | 1 | StealthChop2 |
| GCONF.diag0_int_pushpull / diag1_poscomp_pushpull | 0 | オープンドレイン（外部10kプルアップ前提） |

## 2. 回路各部（`schematic.svg` 対応）

### ① 電源入力・保護
- J2(+24V) → F1 PPTC 3A/33V → Q1 P-MOSFET 逆接保護（D=入力, S=負荷, G=R8 10k→GND, D2 BZT52C12 で |VGS| を 12V にクランプ）→ VS。
- D1 SMBJ33A（33V standoff）で VS–GND をクランプ。C1 100 µF/35V バルク。
- Q1 は SOT-23 で −40V/−3A（60 mΩ）。24V系で −30V 品（AO3401A 等）は TVS クランプ時に耐圧不足になるため不可。電流余裕が欲しい場合は AOD4185（TO-252, −40V/−40A）へ差し替え。

### ② デカップリング
- VS: 1 µF + 100 nF を VS ピン2グループ（pin17 側 / pin20-21-24 側）の直近に各1組（C2/C4, C3/C5）。
- VCC_IO: 100 nF（C9）。VDD1V8: 2.2 µF（C8, AGND へ）。
- モータ出力 OUT1A/2A/1B/2B に 1 nF（C10–13, EMC対策, DNP可）。

### ③ チャージポンプ
- CPO–CPI: 22 nF/50V（C6）。VCP–VS: 1 µF（C7, **VS ピン直近に配置** — 誘導性ピーク回避のためデータシート指示）。

### ④ ロジック
- UART_EN → **SJ1（3パッドハンダジャンパ、既定 GND側ブリッジ = 4線SPI）**。3V3 側に付け替えると1線UARTモード。CLK=GND（内蔵発振 12.5 MHz ±5%、SPI クロック上限 10 MHz）。
- AIN 未使用 → GND。OV ピン未使用 → 開放（過電圧クランプFETは未実装）。
- プルアップ 10k×4: CSN / ENN(DRV_ENN) / DIAG0 / DIAG1（DIAG はオープンドレイン既定のため必須）。
- プルダウン 10k×2: REFL / REFR（未接続時のレベル確定。SW_MODE で極性設定可）。

### ⑤ エンコーダ（後付け対応）
- ENCA/ENCB/ENCN を J4（2.54mm 1×5: 3V3 / A / B / N / GND）へ引き出し。**未接続時は R9〜R11 の 10k プルダウンでレベル確定**（フロート禁止のため）。
- 対応エンコーダは **3.3V ロジック（VCC_IO ドメイン）の ABN インクリメンタル**。5V 出力品はレベル変換が必要。
- 使うときのレジスタ: `ENCMODE`(0x38) で極性/クリア条件、`ENC_CONST`(0x3A) にエンコーダ分解能↔マイクロステップ換算、実位置は `X_ENC`(0x39)。N チャネルで StallGuard 原点出しより高精度なホーミングも可能。

### UART について（設計判断）
- Pico と1対1の本構成では **SPI を正式採用**。全二重・10MHz・毎応答ステータス付きで、StealthChop2/StallGuard4 の全機能が使える。
- TMC5240 の UART は1線半二重で、利点は配線削減と多軸デイジーチェーン（CSN/SCK/SDI がアドレスストラップ AD2/AD1/AD0 兼用）。単基板では利点なし。
- ただし選択は UART_EN ピン1本なので、**SJ1 により追加部品ゼロで将来切替可能**にした。UART に切り替えた場合、J1 の SDI ピンが1線データ、CSN/SCK のプルアップ/プルダウン状態がノードアドレスになる点に注意。

### コネクタ

**J1 2.54mm 1×12（Pico 接続）**

| ピン | 信号 | Pico |
|---|---|---|
| 1 | GND | GND |
| 2 | 3V3 | 3V3(OUT) — VCC_IO 用。モータ電源とは別系統 |
| 3 | SCK | GP18 (SPI0 SCK) |
| 4 | SDI (MOSI) | GP19 (SPI0 TX) |
| 5 | SDO (MISO) | GP16 (SPI0 RX) |
| 6 | CSN | GP17 |
| 7 | ENN | 任意 GPIO（L=駆動許可） |
| 8 | DIAG0 | 任意 GPIO（割込/StallGuard） |
| 9 | DIAG1 | 任意 GPIO |
| 10 | REFL | 原点SW（任意） |
| 11 | REFR | 原点SW（任意） |
| 12 | GND | GND |

**J2** 5.08mm 2P: +24V / GND　**J3** 5.08mm 4P: OUT1A / OUT2A（コイルA）, OUT1B / OUT2B（コイルB）

**J4 2.54mm 1×5（エンコーダ、後付け可）**

| ピン | 信号 | 備考 |
|---|---|---|
| 1 | 3V3 | エンコーダ電源（3.3V ロジック品のみ） |
| 2 | ENCA | A相 |
| 3 | ENCB | B相 |
| 4 | ENCN | N（インデックス） |
| 5 | GND | — |

## 3. ネットリスト

| ネット | 接続 |
|---|---|
| +24V_IN | J2.1, F1.1 |
| 24V_F | F1.2, Q1.D |
| VS | Q1.S, D2.K, D1.K, C1.+, C2.1, C3.1, C4.1, C5.1, C7.2, U1.17, U1.20, U1.21, U1.24 |
| Q1_G | Q1.G, R8.1, D2.A |
| 3V3 | J1.2, J4.1, U1.5(VCC_IO), U1.25(SLEEPN), R2.1, R3.1, R4.1, R5.1, C9.1, SJ1.1 |
| SCK | J1.3, U1.27 |
| SDI | J1.4, U1.28 |
| SDO | J1.5, U1.29 |
| CSN | J1.6, U1.26, R2.2 |
| ENN | J1.7, U1.9(DRV_ENN), R3.2 |
| DIAG0 | J1.8, U1.11, R4.2 |
| DIAG1 | J1.9, U1.12, R5.2 |
| REFL | J1.10, U1.31, R6.1 |
| REFR | J1.11, U1.32, R7.1 |
| ENCA | J4.2, U1.8, R9.1 |
| ENCB | J4.3, U1.7, R10.1 |
| ENCN | J4.4, U1.6, R11.1 |
| UART_EN | U1.10, SJ1.2（中央パッド） |
| IREF | U1.1, R1.1 |
| VDD1V8 | U1.3, C8.1 |
| CPO | U1.15, C6.1 |
| CPI | U1.14, C6.2 |
| VCP | U1.16, C7.1 |
| OUT1A | U1.23, J3.1, C10.1 |
| OUT2A | U1.22, J3.2, C11.1 |
| OUT1B | U1.18, J3.3, C12.1 |
| OUT2B | U1.19, J3.4, C13.1 |
| GND | J2.2, J1.1, J1.12, J4.5, D1.A, C1.−, C2–C5.2, C8.2(AGND経由), C9.2, C10–C13.2, R1.2, R6.2, R7.2, R8.2, R9.2, R10.2, R11.2, SJ1.3（既定ブリッジ側）, U1.2(AIN), U1.4(AGND), U1.30(CLK), U1.EP |

## 4. 発熱見積

- 導通損: 2相 × 1.5² × (0.12+0.11) Ω ≈ **1.04 W**。スイッチング・コア込みで **約 1.3〜1.5 W**。
- θJA を 35 K/W（EP 半田付け＋4層、要確認）とすると ΔT ≈ 45〜55 ℃ → 室温で Tj ≈ 80 ℃。連続 1.5 A RMS は成立するが、**EP 直下サーマルビア 3×3 以上＋両面 GND ベタ**を必須とし、停止時は IHOLD=10 で電流を落とす。

## 5. レイアウト注意

- EP（露出パッド）= パワー GND。直下にサーマルビア ≥9 本、裏面ベタへ。
- C7（VCP–VS）と C6（CPO–CPI）は該当ピン直近・最短ループ。
- R1（IREF）はピン1直近、GND リターン最短、モータ配線から離す（電流精度に直結）。
- C2/C4 と C3/C5 は VS ピンの2グループにそれぞれ配置。C1 はその外側。
- AGND（pin4）と C8 のリターンは静かな GND 経由で EP ベタへ（モータ電流経路と分ける）。
- OUT 配線は太く短く。J2/J3（24V系）と J1（3.3V系）は物理的に分離。

## 6. JLCPCB 発注メモ

- **U1 の在庫が薄い**（2026-07 時点 約240個）→ 発注前に JLCPCB のプライベートライブラリで部品確保推奨。
- TMC2240（C7429724, 在庫潤沢・安価）は**ピン互換ではない**（STEP/DIR 型でランプジェネレータ非搭載）。代替にする場合は回路・ソフト両方の再設計が必要。
- パッシブはほぼ Basic 部品（実装費安）。Extended は U1/Q1/D1/D2/F1/C1/コネクタ類。
- J1/J2/J3 は THT → JLCPCB の「Standard PCBA (THT対応)」を選択するか、手半田にするなら BOM から除外。
- Basic/Extended 区分と在庫は変動する。**発注直前に JLCPCB の BOM ツールで再確認**。

## 7. 設計レビュー チェックリスト

- [ ] R_IREF=12kΩ 1% / CURRENT_RANGE=3A / GLOBALSCALER=181 / IRUN=31 → 1.5 A RMS の整合
- [ ] CPO–CPI 22nF・VCP–VS 1µF がピン直近か
- [ ] VDD1V8 に 2.2µF（AGND へ）、負荷を繋いでいないか
- [ ] SLEEPN が 3V3 に接続されているか（内部プルダウンのため開放不可）
- [ ] SJ1 が GND 側ブリッジ（SPI）で製造されるか（銅箔ブリッジ or 製造時ハンダ指示）、CLK=GND（内蔵OSC）か
- [ ] DIAG0/1・CSN・ENN に 10k プルアップ、REFL/REFR・ENCA/B/N に 10k プルダウン
- [ ] エンコーダは 3.3V ロジック品か（5V 品はレベル変換要）
- [ ] TVS クランプ電圧が VS 絶対最大（≈38V, 要確認）未満か／Q1 耐圧 −40V 以上か
- [ ] EP サーマルビア・GND ベタ・IHOLD 低減の放熱3点セット
- [ ] 発注直前の在庫・Basic/Extended 再確認（特に U1）

## 8. 未確認事項（発注前に PDF 原本で確認）

データシート PDF 原本（analog.com）は取得環境の制約で全文確認できておらず、以下は検索抽出＋リファレンス設計からの照合値。**発注前に PDF で最終確認すること。**

1. VS 絶対最大定格（≈38 V と推定）
2. θJA / θJC（TQFN-32 EP 実装時）
3. R_IREF の許容帯（12–60 kΩ か 12–24 kΩ か。本設計は 12 kΩ なのでどちらでも適合）
4. VS バルク容量の推奨値（本設計 100 µF は TMC 系の慣例値）
5. C10–13（1nF）の LCSC C1588 の Basic 区分

### 根拠資料

- [TMC5240 データシート (ADI)](https://www.analog.com/media/en/technical-documentation/data-sheets/tmc5240.pdf)（検索抽出）
- [TMC-API TMC5240 レジスタ定義 (ADI 公式 GitHub)](https://github.com/analogdevicesinc/TMC-API/blob/master/tmc/ic/TMC5240/TMC5240_HW_Abstraction.h)
- [電流設定の考え方 (ADI EngineerZone)](https://ez.analog.com/other-products/w/documents/32673/)
- リファレンス設計: [benjibst/equilibot](https://github.com/benjibst/equilibot), [mitmedialab/generic-pan-tilt-pcb](https://github.com/mitmedialab/generic-pan-tilt-pcb)（KiCad ネットリスト照合）
- [TMC5240ATJ+T @LCSC C7494373](https://www.lcsc.com/product-detail/Motor-Driver-ICs_TRINAMIC-Motion-Control-GmbH-TMC5240ATJ-T_C7494373.html) / [@JLCPCB](https://jlcpcb.com/partdetail/8557215-TMC5240ATJT/C7494373)
