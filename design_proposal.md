# Design proposal: InaudibleXAI (projekt X2)

**Pytanie badawcze.** Jaka część decyzji modelu audio i jego wyjaśnienia opiera się na energii poniżej progu maskowania? Czy ta zależność przewiduje spadek jakości modelu po kompresji kodekiem?

Termin oddania: 14.01.2027. Zespół: 3 osoby.

## 1. Zakres eksperymentów

1. **Próg maskowania** dla każdego binu STFT: dwa modele psychoakustyczne (MPEG-1 model 1 i model 2), dwa poziomy odsłuchu (np. 60 i 80 dB SPL).
2. **Usunięcie energii pod progiem**: zerujemy biny pod progiem, zachowujemy fazę, robimy iSTFT. Próg liczymy na oryginalnym sygnale, resampling do częstotliwości modelu dopiero potem. Każde zadanie sprawdzamy na słuch.
3. **Zmiana decyzji** po usunięciu, porównana ze zmianą między dwoma różnymi klipami (kontrola). 300 klipów na zadanie, przedziały bootstrap.
   - ASR: log-prob transkrypcji referencyjnej i WER.
   - Weryfikacja mówcy: zmiana podobieństwa cosinusowego, zmiany decyzji przy progu EER.
   - Klasyfikatory: zmiana prawdopodobieństwa klasy.
4. **Masa atrybucji pod progiem** dla Integrated Gradients, Grad-CAM, LRP i okluzji, na wspólnej siatce STFT, z kontrolą losowej mapy. Modele na surowym sygnale dostają iSTFT z wejścia STFT, więc gradienty trafiają na tę samą siatkę.
5. **Kodeki**: MP3 i Opus, po trzy bitrate'y. Sprawdzamy korelację rang między zależnością od energii niesłyszalnej a spadkiem jakości.
6. **Audyt L-MAC**: jaka część energii wyjaśnienia jest niesłyszalna w miksie. Do tego wariant z maską tylko na słyszalnych binach i jego koszt dla wierności wyjaśnienia.

**Pierwszy eksperyment:** odsłuch 10 klipów po usunięciu, potem PANNs CNN14 na 100 klipach przed i po usunięciu, porównanie z kontrolą.

**Wynik obalający hipotezę:** zmiana decyzji i masa atrybucji pod progiem mieszczą się w kontrolach dla wszystkich modeli i zadań, przy obu poziomach odsłuchu i obu modelach maskowania.

### Modele

Wszystkie checkpointy sprawdziliśmy 27.10.2026.

| # | Zadanie (dane) | Model | Typ | fs / pasmo | Checkpoint |
|---|---|---|---|---|---|
| 1 | ASR (LibriSpeech test-clean) | Whisper small | transformer, log-mel | 16 kHz / 0–8 kHz | `openai/whisper-small` |
| 2 | ASR | wav2vec 2.0 CTC | SSL, waveform | 16 kHz / 0–8 kHz | `facebook/wav2vec2-base-960h` |
| 3 | ASR | Conformer, bez LM | Conformer, fbank | 16 kHz / 0–8 kHz | `speechbrain/asr-conformer-transformerlm-librispeech` |
| 4 | Weryfikacja mówcy (VoxCeleb1-O) | ECAPA-TDNN | CNN 1D, fbank | 16 kHz / 0–8 kHz | `speechbrain/spkrec-ecapa-voxceleb` |
| 5 | Weryfikacja mówcy | ResNet34-LM | CNN 2D, fbank | 16 kHz / 0–8 kHz | `Wespeaker/wespeaker-voxceleb-resnet34-LM` |
| 6 | Weryfikacja mówcy | WavLM Base+ SV | SSL, waveform | 16 kHz / 0–8 kHz | `microsoft/wavlm-base-plus-sv` |
| 7 | Tagowanie (AudioSet eval) | PANNs CNN14 | CNN, log-mel | 32 kHz / 50 Hz–14 kHz | Zenodo 3987831 |
| 8 | Tagowanie | AST | transformer, spektrogram | 16 kHz / 0–8 kHz | `MIT/ast-finetuned-audioset-10-10-0.4593` |
| 9 | Tagowanie | BEATs iter3+ AS2M | SSL, transformer | 16 kHz / 0–8 kHz | `microsoft/unilm/beats` |
| 10 | Ptaki (BirdSet test) | ConvNeXt-Base | CNN, spektrogram | 32 kHz / 0–16 kHz | `DBD-research-group/ConvNeXT-Base-BirdSet-XCL` |
| 11 | Ptaki | AST | transformer, spektrogram | 32 kHz / 0–16 kHz | `DBD-research-group/AST-BirdSet-XCL` |
| 12 | Ptaki | wav2vec 2.0 | SSL, waveform | 32 kHz / 0–16 kHz | `DBD-research-group/Wav2Vec2-Base-BirdSet-XCL` |
| 13 | Deepfake mowy (ASVspoof 2019 LA) | AASIST | waveform, graph attention | 16 kHz / 0–8 kHz | `clovaai/aasist` |
| 14 | Deepfake mowy | XLS-R + AASIST | SSL front-end | 16 kHz / 0–8 kHz | `TakHemlata/SSL_Anti-spoofing` |
| 15 | Deepfake muzyki (SONICS) | SpecTTTra-α 120 s | transformer, spektrogram | 16 kHz / 20 Hz–8 kHz | `awsaf49/sonics-spectttra-alpha-120s` |
| 16 | Ptaki | BirdNET | TFLite, bez gradientów | 48 kHz / 0–15 kHz | BirdNET-Analyzer |

- BirdNET służy tylko jako czarna skrzynka: zmiana decyzji, kodeki, okluzja.
- Modele 7–9 mają etykiety AudioSet, więc mierzymy je na AudioSet. ESC-50 służy tylko do audytu L-MAC (`speechbrain/cnn14-esc50`).
- Przed pomiarami odtwarzamy wynik każdego modelu na czystych danych.
- Licencje: kod i modele głównie Apache-2.0, MIT lub BSD. WeSpeaker ma CC BY 4.0, BirdNET CC BY-NC-SA 4.0. Dane BirdSet i SONICS mają CC BY-NC 4.0, co pozwala na użycie badawcze. Modele BirdSet nie podają licencji, więc pytamy autorów.

**Dane:** LibriSpeech test-clean, VoxCeleb1-O, podzbiór AudioSet eval, ESC-50, BirdSet test, ASVspoof 2019 LA eval, SONICS. Oryginalnych danych nie zmieniamy.

## 2. Funkcjonalność programu

Pakiet Pythona `inaudible`, który liczy metrykę dla dowolnego modelu:

- `threshold`: dwa modele maskowania, poziom odsłuchu jako parametr,
- `deletion`: usunięcie energii pod progiem z zachowaniem fazy,
- `metrics`: zmiana decyzji, masa atrybucji pod progiem, kontrole, bootstrap,
- `models`: adapter dla każdego modelu (miara decyzji, różniczkowalne wejście STFT),
- `attribution`: Captum i Zennit, rzutowanie map na wspólną siatkę,
- `codecs`: MP3 i Opus przez ffmpeg,
- `lmac`: audyt listenable maps,
- CLI (`typer`), które uruchamia eksperyment z pliku konfiguracyjnego i zapisuje tabele do `results/`.

## 3. Stack technologiczny

- Python 3.11, `uv`, `ruff`, `just`, `pytest` z `tox`, MkDocs, semantic versioning
- PyTorch, torchaudio, `transformers`, SpeechBrain, WeSpeaker, kod BirdSet i SONICS, `fairseq` (tylko model 14)
- Captum, Zennit, NumPy, SciPy, ffmpeg (libmp3lame, libopus)
- Hydra (konfiguracja), Weights & Biases (śledzenie eksperymentów)
- Artykuł w szablonie Interspeech. Prompty i sesje agentów trzymamy w `agent_logs/`.

## 4. Harmonogram i zasoby

Jedno GPU (min. 16 GB). Prawie wszystko to inferencja: ok. 50 GPU-h na atrybucje (głównie Integrated Gradients) i ok. 10 GPU-h na trening interpretera L-MAC i jego wariantu. Dane zajmują ok. 60 GB.

| Termin | Plan |
|---|---|
| 28.10–03.11 | Design proposal, szablon repo, środowisko, CI, pobranie danych |
| 04.11–10.11 | Próg maskowania (model 1), usunięcie energii, odsłuch, pierwszy eksperyment. Adaptery modeli, odtworzenie wyników na czystych danych |
| 11.11–17.11 | Model maskowania 2, testy względem kodu referencyjnego, tabela literatury |
| 18.11–24.11 | **Prototyp**: cały pipeline na 30 klipach dla wszystkich modeli |
| 25.11–01.12 | Zmiana decyzji: 300 klipów, 2 poziomy, 2 modele maskowania, kontrole |
| 02.12–08.12 | Atrybucje i masa pod progiem (ok. 50 GPU-h), eksperymenty z kodekami |
| 09.12–15.12 | Audyt L-MAC, trening wariantu słyszalnego (ok. 10 GPU-h) |
| 16.12–22.12 | Bootstrap, tabele, dokumentacja i testy pakietu |
| 23.12–03.01 | Bufor (przerwa świąteczna) |
| 04.01–10.01 | Artykuł, instrukcja użytkowania, filmik |
| 11.01–14.01 | Sprawdzenie, czy każda liczba w artykule pochodzi z pliku w `results/`, oddanie |

Postępy notujemy co tydzień w `docs/worklog.md`.

**Ryzyka:** model 14 wymaga starej wersji `fairseq` i wag z Google Drive. Jeśli instalacja się nie uda, bierzemy inny detektor wav2vec 2.0 albo trenujemy RawNet2. Wagi BEATs pobieramy raz z OneDrive i zapisujemy ich sumę kontrolną.

## 5. Bibliografia

1. Schönherr et al., Adversarial Attacks Against ASR Systems via Psychoacoustic Hiding, arXiv:1808.05665
2. Qin et al., Imperceptible, Robust, and Targeted Adversarial Examples for ASR, arXiv:1903.10346
3. I Guess That's Why They Call it the Blues: Causal Analysis for Audio Classifiers, arXiv:2601.16675
4. Measuring the Robustness of Audio Deepfake Detection under Real-World Corruptions, arXiv:2503.17577
5. Clean Accuracy Does Not Guarantee Provenance Robustness, arXiv:2609.07981
6. Parekh et al., Listen to Interpret, arXiv:2202.11479
7. Paissan et al., Listenable Maps for Audio Classifiers, arXiv:2403.13086
8. Listenable Maps for Zero-Shot Audio Classifiers, arXiv:2405.17615
9. The Perceived Fragility of Explanations in Audio Models, arXiv:2606.14466
10. A Framework for Evaluating Faithfulness in XAI for Machine Anomalous Sound Detection, arXiv:2601.19017
11. ISO/IEC 11172-3 (MPEG-1 Audio), modele psychoakustyczne 1 i 2
12. Painter, Spanias, Perceptual Coding of Digital Audio, Proc. IEEE, 2000
13. Radford et al., Whisper, arXiv:2212.04356
14. Baevski et al., wav2vec 2.0, arXiv:2006.11477
15. Gulati et al., Conformer, arXiv:2005.08100
16. Desplanques et al., ECAPA-TDNN, arXiv:2005.07143
17. Wang et al., WeSpeaker, arXiv:2210.17016
18. Chen et al., WavLM, arXiv:2110.13900
19. Kong et al., PANNs, arXiv:1912.10211
20. Gong et al., AST, arXiv:2104.01778
21. Chen et al., BEATs, arXiv:2212.09058
22. Rauch et al., BirdSet, arXiv:2403.10380
23. Kahl et al., BirdNET, Ecological Informatics, 2021
24. Jung et al., AASIST, arXiv:2110.01200
25. Tak et al., Spoofing and Deepfake Detection Using wav2vec 2.0 and Data Augmentation, arXiv:2202.12233
26. Rahman et al., SONICS, arXiv:2408.14080
27. Wang et al., ASVspoof 2019, arXiv:1911.01601
28. Sundararajan et al., Integrated Gradients, arXiv:1703.01365
29. Selvaraju et al., Grad-CAM, arXiv:1610.02391
30. Bach et al., Layer-wise Relevance Propagation, PLoS ONE, 2015
31. Kokhlikyan et al., Captum, arXiv:2009.07896
32. Anders et al., Zennit, arXiv:2106.13200
