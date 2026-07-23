# Training data

`flights_sample.csv` is a **50,000-row deterministic training subset** of the 2015 U.S. flight-delay data referenced by the Figshare `flights.csv` article. It contains the original 31 analytical columns and is committed with the repository so every learner, Codespace and GitHub Actions run uses the same observations.

For the Day 2 data-quality practical, **25 exact duplicate rows were deliberately added**. Students are expected to detect and remove them rather than assume the file is already clean.

The packaged subset covers the month values recorded in `DATA_SOURCE.json`. October is not represented in this training subset, so students must not infer October performance from it. This limitation is useful for discussing sampling coverage and responsible interpretation.

The full upstream file is approximately 565 MB. For full-scale or independent research, download it from <https://figshare.com/articles/dataset/flights_csv/9820139>.

`DATA_SOURCE.json` records the subset size, seed, provenance, coverage and deliberate modifications.
