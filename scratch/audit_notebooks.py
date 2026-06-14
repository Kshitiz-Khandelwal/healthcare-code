import json, os, re

nb_dir = r"c:\Users\Admin\Desktop\Kshitiz\healthcare project\healthcare project\notebooks"

notebooks_to_check = [
    # Blank ones
    "03_preprocessing_and_scalograms.ipynb",
    "04_efficientnet_embeddings.ipynb",
    "05_hybrid_feature_training.ipynb",
    "ecg_analysis.ipynb",
    "ecg_analysis_phase_workflow.ipynb",
    # Executed ones
    "03_preprocessing_and_scalograms_executed.ipynb",
    "04_efficientnet_embeddings_executed.ipynb",
    "05_hybrid_feature_training_executed.ipynb",
    "ecg_analysis_professional.ipynb",
]

for fname in notebooks_to_check:
    path = os.path.join(nb_dir, fname)
    if not os.path.exists(path):
        print(f"\n{'='*70}\n  MISSING: {fname}\n{'='*70}")
        continue
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    all_code = ""
    for c in cells:
        if c.get("cell_type") == "code":
            all_code += "".join(c.get("source", []))

    # Check what model references exist
    has_b0 = "efficientnet_b0" in all_code or "b0" in all_code.lower()
    has_b4 = "efficientnet_b4" in all_code or "EfficientNet_B4" in all_code
    has_config = "CONFIG" in all_code or "config" in all_code
    has_deep = "deep_features" in all_code or "embedding" in all_code.lower()
    has_handcrafted = "handcrafted" in all_code
    has_hybrid = "hybrid" in all_code
    has_scalogram = "scalogram" in all_code or "cwt" in all_code.lower()
    has_pca = "PCA" in all_code or "pca" in all_code
    
    # Check outputs for B0/B4 references
    output_text = ""
    output_count = 0
    image_count = 0
    for c in cells:
        for o in c.get("outputs", []):
            output_count += 1
            if "text" in o:
                output_text += "".join(o["text"])
            if "data" in o:
                if "text/plain" in o["data"]:
                    output_text += "".join(o["data"]["text/plain"])
                if "image/png" in o["data"]:
                    image_count += 1

    b0_in_output = "efficientnet_b0" in output_text or "b0" in output_text.lower()
    b4_in_output = "efficientnet_b4" in output_text or "b4" in output_text.lower()
    
    print(f"\n{'='*70}")
    print(f"  {fname}")
    print(f"{'='*70}")
    print(f"  Code references:")
    print(f"    B0: {'YES' if has_b0 else 'no'}  |  B4: {'YES' if has_b4 else 'no'}  |  CONFIG: {'YES' if has_config else 'no'}")
    print(f"    Scalogram: {'YES' if has_scalogram else 'no'}  |  Deep/Embedding: {'YES' if has_deep else 'no'}")
    print(f"    Handcrafted: {'YES' if has_handcrafted else 'no'}  |  Hybrid: {'YES' if has_hybrid else 'no'}  |  PCA: {'YES' if has_pca else 'no'}")
    print(f"  Outputs: {output_count} cells  |  Images: {image_count}")
    if output_count > 0:
        print(f"  Output references:  B0: {'YES' if b0_in_output else 'no'}  |  B4: {'YES' if b4_in_output else 'no'}")
