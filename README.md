# 視窗長度對 EEG Welch 頻譜解析度、帶功率 CV 與 Relax/Focus Cohen's d 之取捨

本研究以單通道 EEG 資料，在固定前處理下掃描 Welch 視窗長度，比較頻譜解析度、α 帶相對功率變異係數（CV）以及 Relax 與 Focus 間 Cohen's d 效應量之變化。

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

範例檔名：`S1_1_01.txt`（報告與 `summary.json` 以 S1、S2 標記受試者）

## 一鍵重現

```bash
python -m pytest tests/ -q
python -m ruff check src/ tests/
python -m src.experiments.window_sweep
```

## 產出

執行 `window_sweep` 後，`figures/` 目錄將產生：

- 六張 PDF 圖表
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
figures/            # 實驗圖表與 summary.json
report/             # 書面報告（XeLaTeX；執行 compile.ps1 編譯）
```

## 授權與學術誠信

本專題為 ADSP 課程作業。本 repo **不提供**真實腦波下載；資料須由使用者自行準備。公開分析僅涵蓋**經知情同意**提供之兩名受試者（S1、S2）；其餘組員或未經同意之紀錄未納入。原始 `.txt` 資料**不隨 GitHub 散布**；本 repo 僅含可重現之分析程式。本專案僅供 ADSP 課程作業與 DSP 方法示範，**不作**臨床診斷或群體推論。書面報告第 2.1 節「資料倫理與使用範圍」有更完整說明。引用他人成果時請於書面報告中註明出處。
