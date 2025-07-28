# African ASR Benchmarking

This repository contains scripts for automated evaluation of ASR models on [Next Voices Africa](https://huggingface.co/datasets/dsfsi-anv/za-african-next-voices) dataset.

## ✅ Evaluated Languages and Models (WER/CER %)

| Language   | MMS-1B-All | MMS-1B-FL102 | MMS-1B-L1107 | SeamlessM4T | Whisper | Xeus |
|------------|------------|--------------|--------------|-------------|---------|------|
| Zulu       | 39.30/8.73 | 40.47/9.53   | ⚠️[^1]       |   ⏳        | ❌      |  ⏳    |
| Luo        |            |              |              |             | ❌      |      |
| Kikuyu     |            |              |              |             | ❌      |      |
| Yoruba     |            |              |              |             |         |      |
| Igbo       |            |              |              |             | ❌      |      |
| Hausa      |            |              |              |             |         |      |
| Amharic    |            |              |              |             |         |      |
| Tigrinya   |            |              |              |             | ❌      |      |
| Sidama     |            |              |              |             | ❌      |      |
| Oromo      |            |              |              |             | ❌      |      |
| Wolaytta   |            |              |              |             | ❌      |      |

[^1]: `facebook/mms-1b-l1107` claims to support Zulu but raises a runtime error when 'zul' is specified.

## 📁 Files in this Repo

| File                          | Description                                                  |
|-------------------------------|--------------------------------------------------------------|
| `ZA_African_Next_Voices_benchmarking.ipynb` | Notebook used for model inference and evaluation |
| `asr_language_support_matrix.csv`           | CSV matrix of ASR model support across selected African languages |
| `hf_asr_scraper.py`                         | Script to scrape Hugging Face for ASR model support      |

## 🔧 Dependencies
This project uses:
- Hugging Face Transformers
- jiwer (for WER/CER computation)
- torchaudio
- pandas, tqdm, etc.

## ✅ TODO

- [x] Evaluate MMS-1B-All on Zulu  
- [x] Evaluate MMS-1B-FL102 on Zulu  
- [ ] Fix or work around `mms-1b-l1107` runtime error for Zulu  
- [ ] Add support for SeamlessM4T model variants  
- [ ] Extend evaluation to more languages in the Next Voices dataset  
- [ ] Add evaluation for Whisper and Xeus models  
- [ ] Compare with commercial APIs (Google STT, Microsoft Azure)  
- [ ] Publish summary report and plots  
