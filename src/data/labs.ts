// 触れる実験（widget）の正本。工房(/workshop/)とトップページの両方がここを import する。
// 2026-07-14: workshop/index.astro のインライン定義から切り出し（二重管理で棚から漏れる事故の再発防止）。
// 同日、棚卸しで見つかった未登録9点のうち8点を収容（/living/ は私的な生成アートのため意図的に非掲載）。

export type Lab = { name: string; url: string };
export type LabGroup = { label: string; items: Lab[] };

export const labGroups: LabGroup[] = [
  {
    label: '通信（しくみを開ける）',
    items: [
      { name: 'EtherCAT（通り抜けながら）', url: '/ethercat/' },
      { name: 'EtherCAT・バイトを波形で', url: '/ethercat-wave/' },
      { name: 'EtherCAT・フレームを開ける', url: '/ethercat-frame/' },
      { name: 'EtherCAT・コードで書くと', url: '/ethercat-code/' },
      { name: 'EtherCAT・ESC（専用チップ）', url: '/ethercat-esc/' },
      { name: 'EtherCAT・立ち上げ', url: '/ethercat-startup/' },
      { name: 'UART・一本の線に乗せる', url: '/uart/' },
      { name: 'UART・コードで', url: '/uart-code/' },
      { name: 'SPI・時計の線を引く', url: '/spi/' },
      { name: 'SPI / I²C・コードで', url: '/spi-code/' },
      { name: 'RS-485・差でノイズが消える', url: '/rs485/' },
      { name: 'Modbus・コードで', url: '/modbus-code/' },
      { name: 'CAN・衝突しない調停', url: '/can-arbitration/' },
      { name: 'CAN・コードで', url: '/can-code/' },
      { name: 'スイッチの MAC 学習', url: '/eth-switch/' },
      { name: 'Ethernet・コードで', url: '/eth-code/' },
      { name: 'TCP・落ちても届く', url: '/tcp-reliable/' },
      { name: 'TCP/IP・コードで', url: '/tcp-code/' },
      { name: 'パケットの旅・どこまで開ける', url: '/packet-journey/' },
      { name: '産業Ethernet・三者くらべ', url: '/industrial-eth/' },
      { name: '受信機をぜんぶ開ける（IQ→音）', url: '/rx/' },
    ],
  },
  {
    label: '波と音',
    items: [
      { name: '波の遊び場（進行波・定在波・共鳴管）', url: '/waves/' },
      { name: '伝達行列でフォルマントを解く', url: '/dlab/' },
      { name: '位相が形を運ぶ', url: '/phase/' },
      { name: 'RCローパスの記憶（畳み込み）', url: '/rc-impulse/' },
      { name: '部屋の残響（くし形応答）', url: '/echo-comb/' },
    ],
  },
  {
    label: '電磁気',
    items: [
      { name: '電場プローブ', url: '/efield-probe/' },
      { name: '等電位の地図', url: '/equipotential/' },
      { name: '対称性とガウス面', url: '/gauss-symmetry/' },
      { name: '羽根車と循環', url: '/circulation/' },
      { name: 'マクスウェルの遊輪', url: '/maxwell-idler/' },
      { name: '節点と連続の式', url: '/continuity/' },
      { name: 'コレクタ共振ラボ（自励発振・πVin）', url: '/collector-resonance/' },
      { name: '自励起動ステップ実行（回路図で一歩一歩）', url: '/collector-startup/' },
      { name: '共振の顔（直列の谷・並列の山・Q倍の内側）', url: '/resonance-face/' },
    ],
  },
  {
    label: '場と保存',
    items: [
      { name: '波紋（点源と干渉）', url: '/ripple/' },
      { name: 'ばね玉の鎖', url: '/chain/' },
      { name: 'フラックス（正方形⇄球面）', url: '/flux/' },
      { name: 'フラックス・ラボ', url: '/fluxlab/' },
      { name: 'フラックスを一歩ずつ', url: '/fluxstep/' },
      { name: '源を足して場を作る', url: '/field/' },
      { name: '場の3D地形', url: '/field3d/' },
      { name: '緩和ラボ（ポアソン）', url: '/relax/' },
      { name: '遅れて届く場', url: '/delay/' },
    ],
  },
  {
    label: '力学と数',
    items: [
      { name: '位相空間の散歩（振り子）', url: '/phase-space/' },
      { name: 'オイラーの式（回転）', url: '/euler-rotation/' },
      { name: '面積＝エネルギー（仕事の図解）', url: 'https://work.tnks1407.com' },
    ],
  },
  {
    label: '結晶と対称',
    items: [
      { name: '回すと増える（n回対称）', url: '/nfold/' },
      { name: '鏡で増える', url: '/mirror/' },
      { name: 'らせんと映進', url: '/glide/' },
      { name: '心（centering）', url: '/centering/' },
      { name: '系統的消滅', url: '/reflection/' },
      { name: '準結晶（ペンローズ）', url: '/penrose/' },
    ],
  },
  {
    label: '画像・データ・色',
    items: [
      { name: 'PixLab（画像処理の入口）', url: '/pixlab/' },
      { name: '1次元の微分（明るさ→エッジ）', url: '/pixlab1d/' },
      { name: '画像フォーマットを開ける（JPEG/PNG）', url: '/image-formats/' },
      { name: '図に、だまされない（騙さない可視化）', url: '/honest-charts/' },
      { name: '色空間3Dビューア', url: '/color/' },
      { name: 'ポアソン分布（数え上げ）', url: '/poisson-counts/' },
    ],
  },
  {
    label: '光で測る',
    items: [
      { name: 'パルスの旅（ToF原理）', url: '/tof-pulse/' },
      { name: '熱放射ラボ（プランク曲線）', url: '/glow/' },
      { name: '深度ビューア 8×8（実機対応）', url: '/tof/' },
      { name: 'サーマルビューア 32×24（実機対応）', url: '/thermal/' },
      { name: '熱深度（ToF×サーマル実機）', url: '/duo/' },
      { name: '分光 11ch ビューア（AS7341・実機対応）', url: '/spectro/' },
    ],
  },
  {
    label: '畑の自動化',
    items: [
      { name: '畑の計器盤（土壌水分・給水履歴）', url: '/garden/' },
    ],
  },
];

export const labCount = labGroups.reduce((n, g) => n + g.items.length, 0);
