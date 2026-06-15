# 視窗長度對 EEG Welch 頻譜解析度、帶功率 CV 與 Relax/Focus Cohen's d 之取捨

本研究以單通道 EEG 資料，在固定前處理下掃描 Welch 視窗長度，比較頻譜解析度、$\alpha$ 帶相對功率變異係數（CV）以及 Relax 與 Focus 間 Cohen's $d$ 效應量之變化。

## 環境與安裝

- Python 3.10+
- 依賴見 `requirements.txt`

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

## 資料說明（自備）

本 repo **不提供**真實腦波下載。請自行準備下列目錄結構：

```
data/
├── {subject}/
│   └── {subject}_{class}_{segment}.txt
```

- `class`：1 = Relax、2 = Focus、3 = Blink（主實驗僅用 1、2）
- 每檔為單通道浮點數，長度 10240 樣本（取樣率 512 Hz，約 20 秒）

範例檔名：`b12901014_1_01.txt`（受試者 b12901014、Relax、第 1 段）

## 一鍵重現

```bash
python -m pytest tests/ -q
python -m ruff check src/ tests/
python -m src.experiments.window_sweep
```

## 產出

執行 `window_sweep` 後，`figures/` 目錄將產生：

- 五張 PDF 圖表
- `summary.json`（各視窗長度之彙整數值）

## 專案結構

```
src/
├── config.py       # 常數（取樣率、頻帶定義）
├── io.py           # 資料載入
├── preprocess.py   # 前處理
├── spectral.py     # Welch PSD、帶功率
├── stats.py        # Cohen's d、CV
└── experiments/
    └── window_sweep.py
tests/              # pytest 單元測試
figures/          # 實驗圖表與 summary.json
```

## 授權與學術誠信

本專題為課程作業。資料須由使用者自行取得並遵守相關倫理與隱私規範。引用他人成果時請於書面報告中註明出處。
