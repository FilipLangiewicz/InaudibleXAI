# Design proposal projektu X2: Explanations of what no one can hear: how much of an audio model's decision, and of its explanation, lies below the masking threshold

**Jaka część decyzji modelu audio i jego wyjaśnienia leży poniżej progu maskowania?**

Zespół: Joanna Kiesiak, Mikołaj Rowicki, Filip Langiewicz

Repozytorium: [https://github.com/FilipLangiewicz/InaudibleXAI](https://github.com/FilipLangiewicz/InaudibleXAI)

## 1\. Harmonogram

|Tydz.|Daty|Planowane postępy|
|-|-|-|
|T0|26.10–01.11.2026|Przygotowanie **design proposal (28.10)**, zebranie feedbacku (30.10). Przygotowanie repozytorium, znalezienie danych i modeli.|
|T1|02.11–08.11.2026|Implementujemy pierwszy model progu maskowania. Testujemy go przez odsłuchanie 10 klipów. Na prototyp (najpóźniej 06.11) pokazujemy jak działa cały pipeline na 100 klipach: liczymy próg, usuwamy energię pod progiem i sprawdzamy, czy model zmienia decyzję. Zaczynamy zbieranie wyników.|
|T2|09.11–15.11.2026|Dodajemy implementację drugiego modelu progu maskowania. Poprzez nasz własny odsłuch i obiektywne miary sprawdzamy, czy usunięcie energii jest niesłyszalne na przykładowych danych ze zbioru. Pobieramy inne modele, zbiory danych i przeprowadzamy eksperymenty.|
|T3|16.11–22.11.2026|Mierzymy, jak bardzo zmieniają się decyzje wszystkich modeli po zastosowaniu thresholdu. Używamy 300 klipów na zadanie, dwóch poziomów głośności i dwóch modeli maskowania. Przeprowadzamy dalsze eksperymenty dla wszystkich wariantów.|
|T4|23.11–29.11.2026|Liczymy mapy atrybucji (feature attribution map), stosując 4 różne techniki wyjaśnialności i rzutujemy je na wspólną siatkę. Sprawdzamy, jaka część masy leży poniżej progu słyszalności i porównujemy wyniki z losową mapą.|
|T5|30.11–06.12.2026|Kodujemy klipy w MP3 i Opus przy trzech przepływnościach i mierzymy, ile dokładności tracą modele.|
|T6|07.12–13.12.2026|Sprawdzamy, czy modele bardziej zależne od niesłyszalnej energii tracą więcej pod kodekami. Weryfikujemy wyjaśnienia dekodera i budujemy ich wariant, który zawiera tylko słyszalne dźwięki.|
|T7|14.12–20.12.2026|Piszemy szkielet artykułu. Zaczynamy przygotowania do deploymentu pakietu.|
|T8|21.12–27.12.2026|Przerwa świąteczna.|
|T9|28.12.2026–03.01.2027|Wydajemy pierwszą wersję pakietu z dokumentacją i testami. Kończymy pełny szkic artykułu.|
|T10|04.01–10.01.2027|Dopracowujemy artykuł, nagrywamy 3–5-minutowy filmik. **10.01.2027 (niedziela) - ustalona przez nas data końca projektu**: kod, dokumentacja, testy, artykuł i filmik są gotowe.|

**Dokumentowanie postępów:** będziemy tworzyli krótkie notatki w notes/YYYY-MM-DD.md (zrobione / blokery / plan), a zadania do wykonania opisywali również jako issues na GitHubie z kamieniami milowymi.

### Czas trenowania i zasoby obliczeniowe

Nie planujemy trenować ani dostrajać badanych modeli. Używamy gotowych, publicznie dostępnych wag i tylko uruchamiamy modele na naszych nagraniach. Jedyny trening w projekcie to opcjonalne dekodery. Przewidujemy, że ich trening zajmie 8–16 godzin.

Na cały projekt wstępnie szacujemy, że potrzebujemy ok. 35–50 godzin pracy karty graficznej (głównie inferencja). Z zapasem na powtórki i błędy planujemy **60–80 godzin** w całym semestrze. Chcielibyśmy skorzystać z zewnętrznych zasobów obliczeniowych (najlepiej uczelnianych), a w razie potrzeby z Kaggle lub Colab.

## 2\. Bibliografia

**Prace kluczowe dla tematu:**

1. L. Schönherr, K. Kohls, S. Zeiler, T. Holz, D. Kolossa. *Adversarial Attacks Against Automatic Speech Recognition Systems via Psychoacoustic Hiding.* NDSS 2019. [arXiv:1808.05665](https://arxiv.org/abs/1808.05665)
2. Y. Qin, N. Carlini, I. Goodfellow, G. Cottrell, C. Raffel. *Imperceptible, Robust, and Targeted Adversarial Examples for Automatic Speech Recognition.* ICML 2019. [arXiv:1903.10346](https://arxiv.org/abs/1903.10346)
3. D. A. Kelly, H. Chockler. *I Guess That’s Why They Call it the Blues: Causal Analysis for Audio Classifiers.* ACM International Conference on Multimedia (ACM MM) 2026, w druku. [arXiv:2601.16675](https://arxiv.org/abs/2601.16675)
4. X. Li, P.-Y. Chen, W. Wei. *Measuring the Robustness of Audio Deepfake Detection under Real-World Corruption.* Proc. ACM CODASPY 2026, s. 145–158. [arXiv:2503.17577](https://arxiv.org/abs/2503.17577)
5. G. Shi. *Clean Accuracy Does Not Guarantee Provenance Robustness: A Prospective Codec-Stress Evaluation of Audio Attribution.* Preprint, 2026. [arXiv:2609.07981](https://arxiv.org/abs/2609.07981)
6. J. Parekh, S. Parekh, P. Mozharovskyi, F. d’Alché-Buc, G. Richard. *Listen to Interpret: Post-hoc Interpretability for Audio Networks with NMF.* NeurIPS 2022. [arXiv:2202.11479](https://arxiv.org/abs/2202.11479)
7. F. Paissan, M. Ravanelli, C. Subakan. *Listenable Maps for Audio Classifiers.* ICML 2024. [arXiv:2403.13086](https://arxiv.org/abs/2403.13086)
8. F. Paissan, L. Della Libera, M. Ravanelli, C. Subakan. *Listenable Maps for Zero-Shot Audio Classifiers.* NeurIPS 2024. [arXiv:2405.17615](https://arxiv.org/abs/2405.17615)
9. P. Kitłowski, D. Wiącek, M. Modrzejewski. *The Perceived Fragility of Explanations in Audio Models: Manipulation of Attribution with Unchanged Predictions.* ICML 2026. [arXiv:2606.14466](https://arxiv.org/abs/2606.14466)
10. A. Buck, G. Cosma, I. Phillips, P. Conway, P. Baker. *A Framework for Evaluating Faithfulness in Explainable AI for Machine Anomalous Sound Detection Using Frequency-Band Perturbation.* Preprint, 2026. [arXiv:2601.19017](https://arxiv.org/abs/2601.19017)

**Psychoakustyka i kodowanie:**

11. ISO/IEC 11172-3:1993. *Information technology — Coding of moving pictures and associated audio for digital storage media at up to about 1,5 Mbit/s — Part 3: Audio* (psychoacoustic models 1 i 2).
12. T. Painter, A. Spanias. *Perceptual coding of digital audio.* Proceedings of the IEEE 88(4), 2000. [DOI: 10.1109/5.842996](https://doi.org/10.1109/5.842996)
13. H. Fastl, E. Zwicker. *Psychoacoustics: Facts and Models.* Springer, 3rd ed., 2007. [DOI: 10.1007/978-3-540-68888-4](https://doi.org/10.1007/978-3-540-68888-4)
14. J.-M. Valin, K. Vos, T. Terriberry. *Definition of the Opus Audio Codec.* RFC 6716, IETF, 2012. [rfc-editor.org](https://www.rfc-editor.org/info/rfc6716)
15. Koder toolame (wersja 0.2l), implementacja modelu psychoakustycznego 1 dla MPEG-1 Layer II wywodząca się z kodu referencyjnego ISO dist10: [*psycho\_1.c*](https://sources.debian.org/src/toolame/02l-3/psycho_1.c)

**Modele i dane:**

16. Y. Gong, Y.-A. Chung, J. Glass. *AST: Audio Spectrogram Transformer.* Interspeech 2021. [arXiv:2104.01778](https://arxiv.org/abs/2104.01778)
17. Q. Kong i in. *PANNs: Large-Scale Pretrained Audio Neural Networks for Audio Pattern Recognition.* IEEE/ACM TASLP 2020. [arXiv:1912.10211](https://arxiv.org/abs/1912.10211)
18. J.-w. Jung i in. *AASIST: Audio Anti-Spoofing using Integrated Spectro-Temporal Graph Attention Networks.* ICASSP 2022. [arXiv:2110.01200](https://arxiv.org/abs/2110.01200)
19. M. A. Rahman i in. *SONICS: Synthetic Or Not: Identifying Counterfeit Songs.* ICLR 2025. [arXiv:2408.14080](https://arxiv.org/abs/2408.14080)
20. A. Radford i in. *Robust Speech Recognition via Large-Scale Weak Supervision* (Whisper). ICML 2023. [arXiv:2212.04356](https://arxiv.org/abs/2212.04356)
21. B. Desplanques, J. Thienpondt, K. Demuynck. *ECAPA-TDNN.* Interspeech 2020. [arXiv:2005.07143](https://arxiv.org/abs/2005.07143)
22. S. Kahl i in. *BirdNET: A deep learning solution for avian diversity monitoring.* Ecological Informatics 61, 2021. [DOI: 10.1016/j.ecoinf.2021.101236](https://doi.org/10.1016/j.ecoinf.2021.101236)
23. K. J. Piczak. *ESC: Dataset for Environmental Sound Classification.* ACM Multimedia 2015. [DOI: 10.1145/2733373.2806390](https://doi.org/10.1145/2733373.2806390)
24. V. Panayotov i in. *LibriSpeech: an ASR corpus based on public domain audio books.* ICASSP 2015. [DOI: 10.1109/ICASSP.2015.7178964](https://doi.org/10.1109/ICASSP.2015.7178964)
25. X. Wang i in. *ASVspoof 2019: A large-scale public database of synthesized, converted and replayed speech.* Computer Speech \& Language 2020. [arXiv:1911.01601](https://arxiv.org/abs/1911.01601)
26. A. Nagrani, J. S. Chung, A. Zisserman. *VoxCeleb: a large-scale speaker identification dataset.* Interspeech 2017. [arXiv:1706.08612](https://arxiv.org/abs/1706.08612)

**Metody wyjaśniania i ewaluacja:**

27. M. Sundararajan, A. Taly, Q. Yan. *Axiomatic Attribution for Deep Networks* (Integrated Gradients). ICML 2017. [arXiv:1703.01365](https://arxiv.org/abs/1703.01365)
28. R. R. Selvaraju i in. *Grad-CAM.* ICCV 2017. [arXiv:1610.02391](https://arxiv.org/abs/1610.02391)
29. S. Bach i in. *On Pixel-Wise Explanations for Non-Linear Classifier Decisions by Layer-Wise Relevance Propagation.* PLoS ONE 2015. [DOI: 10.1371/journal.pone.0130140](https://doi.org/10.1371/journal.pone.0130140)
30. M. D. Zeiler, R. Fergus. *Visualizing and Understanding Convolutional Networks* (occlusion). ECCV 2014. [arXiv:1311.2901](https://arxiv.org/abs/1311.2901)
31. R. Achtibat i in. *AttnLRP: Attention-Aware Layer-Wise Relevance Propagation for Transformers.* ICML 2024. [arXiv:2402.05602](https://arxiv.org/abs/2402.05602)
32. N. Kokhlikyan i in. *Captum: A unified and generic model interpretability library for PyTorch.* 2020. [arXiv:2009.07896](https://arxiv.org/abs/2009.07896)
33. C. J. Anders i in. *Software for Dataset-wide XAI: From Local Explanations to Global Insights with Zennit, CoRelAy, and ViRelAy.* 2021. [arXiv:2106.13200](https://arxiv.org/abs/2106.13200)
34. J. Adebayo i in. *Sanity Checks for Saliency Maps.* NeurIPS 2018. [arXiv:1810.03292](https://arxiv.org/abs/1810.03292)
35. B. Efron, R. J. Tibshirani. *An Introduction to the Bootstrap.* Chapman \& Hall, 1993.

## 3\. Planowany zakres eksperymentów

Chcemy przebadać 15 par model–zadanie: pięć zadań, w każdym trzy architektury, po 300 klipów na zadanie. Dla każdej pary zmierzymy zmianę decyzji modelu po zastosowaniu maskowania. Zmierzymy również udział masy map atrybucji leżący poniżej progu maskowania, przy dwóch poziomach odtwarzania i dwóch modelach maskowania. Następnie sprawdzimy, czy niesłyszalna zależność przewiduje spadek jakości modeli pod kodekami MP3 i Opus dla trzech przepływności. Na koniec przeprowadzimy weryfikację uzyskanych wyników pod kątem udziału niesłyszalnej energii. 

W poniższej tabeli przedstawiamy pary model-zadanie, na których chcemy testować nasze rozwiązanie.

|#|Zadanie|Model|Architektura|Checkpoint / kod|
|-|-|-|-|-|
|1|ASR (LibriSpeech)|Whisper|Transformer enc-dec, log-mel|[openai/whisper-small](https://huggingface.co/openai/whisper-small)|
|2|ASR (LibriSpeech)|wav2vec 2.0 CTC|Samonadzorowany, waveform|[facebook/wav2vec2-base-960h](https://huggingface.co/facebook/wav2vec2-base-960h)|
|3|ASR (LibriSpeech)|Conformer (SpeechBrain)|Conformer, fbank|[speechbrain/asr-conformer-transformerlm-librispeech](https://huggingface.co/speechbrain/asr-conformer-transformerlm-librispeech)|
|4|Weryfikacja mówcy (VoxCeleb)|ECAPA-TDNN|CNN 1D, fbank|[speechbrain/spkrec-ecapa-voxceleb](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb)|
|5|Weryfikacja mówcy (VoxCeleb)|ResNet34 (WeSpeaker)|CNN 2D, fbank|[Wespeaker/wespeaker-voxceleb-resnet34-LM](https://huggingface.co/Wespeaker/wespeaker-voxceleb-resnet34-LM)|
|6|Weryfikacja mówcy (VoxCeleb)|WavLM-sv|Samonadzorowany, waveform|[microsoft/wavlm-base-plus-sv](https://huggingface.co/microsoft/wavlm-base-plus-sv)|
|7|Tagowanie (ESC-50 / AudioSet)|PANNs CNN14|CNN, log-mel|[Zenodo 3987831](https://zenodo.org/record/3987831) · [kod](https://github.com/qiuqiangkong/audioset_tagging_cnn)|
|8|Tagowanie (ESC-50 / AudioSet)|AST|Transformer na patchach spektrogramu|[MIT/ast-finetuned-audioset-10-10-0.4593](https://huggingface.co/MIT/ast-finetuned-audioset-10-10-0.4593)|
|9|Tagowanie (ESC-50 / AudioSet)|BEATs|Samonadzorowany transformer|[microsoft/unilm/beats](https://github.com/microsoft/unilm/tree/master/beats)|
|10|Ptaki|BirdNET|CNN, spektrogram (TF/TFLite)|[birdnet-team/BirdNET-Analyzer](https://github.com/birdnet-team/BirdNET-Analyzer)|
|11|Ptaki (BirdSet)|AST|Transformer na spektrogramie|[DBD-research-group/AST-BirdSet-XCL](https://huggingface.co/DBD-research-group/AST-BirdSet-XCL)|
|12|Ptaki (BirdSet)|Wav2Vec2|Samonadzorowany, waveform|[DBD-research-group/Wav2Vec2-Base-BirdSet-XCL](https://huggingface.co/DBD-research-group/Wav2Vec2-Base-BirdSet-XCL)|
|13|Deepfake mowy (ASVspoof 2019)|AASIST|Raw waveform + graph attention|[clovaai/aasist](https://github.com/clovaai/aasist)|
|14|Deepfake mowy (ASVspoof 2019)|XLS-R + AASIST|Samonadzorowany front-end|[TakHemlata/SSL\_Anti-spoofing](https://github.com/TakHemlata/SSL_Anti-spoofing) · [HF](https://huggingface.co/ash56/ssl-aasist)|
|15|Deepfake muzyki (SONICS)|SpecTTTra|Transformer na spektrogramie|[awsaf49/sonics-spectttra-alpha-120s](https://huggingface.co/awsaf49/sonics-spectttra-alpha-120s) · [kod](https://github.com/awsaf49/sonics)|

## 4\. Planowana funkcjonalność programu

Wynikiem projektu będzie pakiet w Pythonie, który dla dowolnego modelu audio sprawdzi, w jakim stopniu jego decyzje i wyjaśnienia opierają się na dźwiękach niesłyszalnych dla człowieka. Pakiet będzie można zainstalować przez `pip` i użyć na własnym modelu. Repozytorium będzie zawierało też skrypty, które będą odtwarzały wszystkie wyniki z naszego artykułu.

### 4.1 Główne funkcje

* **Wyznaczanie progu maskowania.** Program określa, które fragmenty nagrania są słyszalne, a które zagłuszają głośniejsze dźwięki. Obsługuje dwa modele progu i pozwala ustawić głośność odtwarzania.
* **Usuwanie niesłyszalnych fragmentów.** Program usuwa z nagrania energię poniżej progu i odtwarza z niej sygnał audio. Sprawdza też, czy ta zmiana jest rzeczywiście niesłyszalna.
* **Pomiar zmiany decyzji modelu.** Program porównuje decyzję modelu przed usunięciem i po nim, odnosi wynik do grupy kontrolnej i podaje go z przedziałem niepewności.
* **Analiza map wyjaśnień.** Program generuje mapy atrybucji kilkoma metodami i liczy, jaka ich część wskazuje na fragmenty niesłyszalne. Wynik porównuje z mapami kontrolnymi.
* **Test odporności na kompresję.** Program koduje nagrania w MP3 i Opus przy różnej jakości, mierzy spadek skuteczności modeli i sprawdza, czy jest powiązany z wynikami wcześniejszych pomiarów.
* **Audyt słyszalnych wyjaśnień.** Program sprawdza, jaka część wyjaśnień w postaci dźwięku jest dla człowieka niesłyszalna, i tworzy ich wersję zawierającą tylko słyszalne fragmenty.
* **Raportowanie.** Program generuje tabele i wykresy do artykułu bezpośrednio z zapisanych wyników.

### 4.2 Sposób użycia

Z pakietu będzie można korzystać na dwa sposoby: jako biblioteki w kodzie Pythona albo z linii poleceń, gdzie każdy eksperyment będzie się dało uruchomić jedną komendą z plikiem konfiguracyjnym. Dodanie nowego modelu będzie wymagało napisania jednej krótkiej klasy, która opisuje, jak model przyjmuje dane i jak zwraca decyzję.

### 4.3 Reprodukowalność

Parametry każdego eksperymentu będziemy zapisywali w osobnym pliku konfiguracyjnym, a nie w kodzie. Listy użytych nagrań będą przechowywane w repozytorium, więc zbiór danych będzie zawsze ten sam. Oryginalne dane nie będą modyfikowane. Każde uruchomienie będzie zapisywało parametry i wyniki w systemie śledzenia eksperymentów, więc każdą liczbę w artykule będzie się dało powiązać z konkretnym uruchomieniem. Notatniki Jupyter wykorzystamy wyłącznie do eksploracji i prezentacji wyników, a cała logika eksperymentów trafi do kodu w `src/` - notatniki jedynie będą go importować.

### 4.4 Testy i dokumentacja

Każdy moduł będzie miał testy na prostych sygnałach o znanym wyniku, np. sprawdzenie, czy cichy dźwięk obok głośnego zostaje poprawnie uznany za niesłyszalny. Test całego procesu na kilku nagraniach i małym modelu będzie uruchamiany automatycznie. Dokumentacja, budowana w MkDocs z mkdocstrings, obejmie opis funkcji pakietu oraz instrukcję użycia go na własnym modelu.

## 5\. Stack technologiczny

|Obszar|Narzędzia|
|-|-|
|Język, środowisko|Python 3.11/3.12, poetry (środowisko wirtualne, lockfile, budowa paczki)|
|Struktura projektu|szablon cookiecutter, układ z src/, docs/, tests/|
|Audio, DSP|NumPy, SciPy, torchaudio, librosa, soundfile, ffmpeg (libmp3lame, libopus)|
|Modele|PyTorch, Hugging Face Transformers, panns\_inference, AASIST, SONICS, SpeechBrain, birdnetlib i inne|
|Wyjaśnialność|Captum (IG, Grad-CAM, occlusion), Zennit (LRP), LXT/AttnLRP (LRP dla transformerów)|
|Konfiguracja|Konfiguracja eksperymentów oddzielona od kodu, jeden plik YAML na eksperyment|
|Śledzenie eksperymentów|MLflow lokalnie (parametry, metryki, artefakty)|
|Statystyka, wykresy|pandas, SciPy (bootstrap), matplotlib/seaborn|
|Jakość kodu|ruff (formatowanie i lint), mypy (moduły rdzenia), pre-commit|
|Testy|pytest, tox (3.11, 3.12)|
|Dokumentacja|MkDocs (Material), mkdocstrings|
|Automatyzacja|just/Makefile|
|Wersjonowanie|Git, Conventional Commits, Semantic Versioning|



