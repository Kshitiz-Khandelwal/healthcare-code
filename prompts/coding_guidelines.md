# Coding Guidelines & Standards

This document establishes the development conventions, style guides, and coding patterns to be used in the ECG hybrid classification codebase.

---

## 📌 1. Path Management
- **Standard**: Always use `pathlib.Path` objects for path manipulations. Do not concatenate strings or use `os.path`.
- **Reasoning**: Ensures paths compile successfully across Windows and Unix platforms.
- **Examples**:
  ```python
  # ❌ BAD
  IMAGE_PATH = PROJECT_DIR + "/outputs/deep_features/" + str(record_id) + ".png"

  #   GOOD
  IMAGE_PATH = PROJECT_DIR / "outputs" / "deep_features" / f"{record_id}.png"
  ```

---

## 📌 2. Random Seed Consistency
- **Standard**: Use a constant seed (`SEED = 42`) for all random splits, cross-validation runs, and classifier initializations.
- **Reasoning**: Ensures results are fully reproducible across notebooks, model checkpoints, and different runs.
- **Examples**:
  ```python
  # ❌ BAD
  X_train, X_test = train_test_split(X, test_size=0.20)
  model = LGBMClassifier()

  #   GOOD
  SEED = 42
  X_train, X_test = train_test_split(X, test_size=0.20, random_state=SEED, stratify=y)
  model = LGBMClassifier(random_state=SEED)
  ```

---

## 📌 3. Programmatic Notebook Modifications
- **Standard**: Do not perform direct string replacements on `.ipynb` files. Since notebook files are serialized JSON formats, editing them directly is error-prone.
- **Rules**:
  1. For complex updates, write a script to load the JSON structure, search for cells containing target code prefixes, rewrite the source lines, and save the JSON back to disk (e.g. following the pattern in `fix_05_notebook.py`).
  2. Put heavy utility logic in helper modules within `src/` and import them in the notebook cells. Keep notebook code cells lightweight.

---

## 📌 4. Model Training & Evaluation Logic
- **Standard**:
  - Split data into train and test indexes before training/evaluation begins.
  - Standard scaling parameters must only be fit on the training split, and then applied to the test split.
  - Do not compute PCA projections on the full dataset before splitting.
- **Reasoning**: Avoids information leakage, ensuring honest performance metrics.
- **Examples**:
  ```python
  # ❌ BAD: fitting scaling on the entire dataset leaks test-set distribution statistics to the model
  scaler = StandardScaler()
  X_scaled = scaler.fit_transform(X_all)
  X_train, X_test = train_test_split(X_scaled, test_size=0.2)

  #   GOOD: Fit ONLY on training splits
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=SEED, stratify=y)
  
  scaler = StandardScaler()
  X_train_scaled = scaler.fit_transform(X_train)
  X_test_scaled = scaler.transform(X_test)
  ```

---

## 📌 5. Code Style & Logging
- **Standard**: Use descriptive print statements or standard logging to report execution times and shape progress of operations.
- **Example**:
  ```python
  import time
  t0 = time.time()
  # process...
  print(f"Extraction completed in {time.time() - t0:.2f} seconds.")
  ```
