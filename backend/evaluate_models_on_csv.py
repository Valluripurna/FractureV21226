import os
import argparse
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

import torch

from model import load_model, preprocess_image, predict_fracture


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")


MODEL_CONFIGS: List[Dict] = [
    {
        "key": "efficientnet_fracture_model",
        "display_name": "EfficientNet Fracture Model",
        "slug": "efficientnet",
        "path": os.path.join(MODELS_DIR, "efficientnet_fracture_model.pth"),
    },
    {
        "key": "densenet121_fracture_model",
        "display_name": "DenseNet121 Fracture Model",
        "slug": "densenet121",
        "path": os.path.join(MODELS_DIR, "densenet121_fracture_model.pth"),
    },
    {
        # Uses the MURA DenseNet169-based model file
        "key": "mura_model_pytorch",
        "display_name": "DenseNet169 (MURA) Fracture Model",
        "slug": "densenet169",
        "path": os.path.join(MODELS_DIR, "mura_model_pytorch.pth"),
    },
    {
        "key": "resnet50_fracture_model",
        "display_name": "ResNet50 Fracture Model",
        "slug": "resnet50",
        "path": os.path.join(MODELS_DIR, "resnet50_fracture_model.pth"),
    },
    {
        "key": "fracnet_model",
        "display_name": "FracNet Fracture Model",
        "slug": "fracnet",
        "path": os.path.join(MODELS_DIR, "fracnet_model.pth"),
    },
]


def to_binary_label(raw) -> int:
    """Convert a raw CSV label into binary 0/1.

    This is intentionally permissive so it works for 0/1, True/False,
    and simple strings like "fracture" / "normal".
    """

    if isinstance(raw, str):
        v = raw.strip().lower()
        if v in {"1", "true", "yes", "y", "fracture", "fractured", "positive"}:
            return 1
        return 0

    try:
        return 1 if int(raw) == 1 else 0
    except Exception:
        return 0


def resolve_image_path(path_from_csv: str, image_root: str | None) -> str:
    """Resolve the actual image path from CSV value and optional root."""

    if os.path.isabs(path_from_csv):
        return path_from_csv

    path_from_csv = path_from_csv.strip().lstrip("./\\")

    if image_root:
        return os.path.abspath(os.path.join(image_root, path_from_csv))

    # Default: treat paths as relative to project root
    return os.path.abspath(os.path.join(PROJECT_ROOT, path_from_csv))


def evaluate_single_model(
    config: Dict,
    df: pd.DataFrame,
    image_col: str,
    label_col: str,
    image_root: str | None = None,
    limit: int | None = None,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
    """Run evaluation for a single model and return y_true, y_score, metrics."""

    model_path = config["path"]
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    print(f"\n=== Evaluating {config['display_name']} ===")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(model_path).to(device)

    y_true: List[int] = []
    y_score: List[float] = []

    rows = df.itertuples(index=False)
    if limit is not None:
        rows = list(rows)[:limit]

    total = len(rows) if isinstance(rows, list) else len(df) if limit is None else limit
    processed = 0

    for row in rows:
        try:
            image_path_val = getattr(row, image_col)
        except AttributeError:
            raise KeyError(f"Column '{image_col}' not found in CSV")

        try:
            label_val = getattr(row, label_col)
        except AttributeError:
            raise KeyError(f"Column '{label_col}' not found in CSV")

        full_path = resolve_image_path(str(image_path_val), image_root)
        if not os.path.exists(full_path):
            print(f"[WARN] Missing image, skipping: {full_path}")
            continue

        try:
            with open(full_path, "rb") as f:
                image_bytes = f.read()

            tensor = preprocess_image(image_bytes).to(device)
            prob = predict_fracture(model, tensor)
        except Exception as e:
            print(f"[WARN] Failed to process {full_path}: {e}")
            continue

        y_true.append(to_binary_label(label_val))
        y_score.append(float(prob))

        processed += 1
        if processed % 50 == 0:
            print(f"  Processed {processed}/{total} images...")

    if not y_true:
        raise RuntimeError("No valid samples were evaluated. Check CSV paths and labels.")

    y_true_arr = np.array(y_true)
    y_score_arr = np.array(y_score)

    y_pred_arr = (y_score_arr >= 0.5).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_true_arr, y_pred_arr)),
        "precision": float(precision_score(y_true_arr, y_pred_arr, zero_division=0)),
        "recall": float(recall_score(y_true_arr, y_pred_arr, zero_division=0)),
        "f1": float(f1_score(y_true_arr, y_pred_arr, zero_division=0)),
    }

    try:
        metrics["auc"] = float(roc_auc_score(y_true_arr, y_score_arr))
    except Exception:
        metrics["auc"] = float("nan")

    print(f"  Accuracy : {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall   : {metrics['recall']:.4f}")
    print(f"  F1       : {metrics['f1']:.4f}")
    if not np.isnan(metrics["auc"]):
        print(f"  AUC      : {metrics['auc']:.4f}")

    return y_true_arr, y_score_arr, metrics


def plot_training_like_curves(slug: str, display_name: str, y_true: np.ndarray, y_score: np.ndarray) -> None:
    """Plot evaluation-based curves (accuracy/F1 vs threshold).

    Saved as <slug>_training_curves.png so the frontend can show it
    under the existing "Accuracy & Loss" tile.
    """

    thresholds = np.linspace(0.0, 1.0, 101)
    accuracies = []
    f1s = []

    for t in thresholds:
        y_pred = (y_score >= t).astype(int)
        accuracies.append(accuracy_score(y_true, y_pred))
        f1s.append(f1_score(y_true, y_pred, zero_division=0))

    plt.figure(figsize=(6, 4))
    plt.plot(thresholds, accuracies, label="Accuracy", color="#007bff")
    plt.plot(thresholds, f1s, label="F1-score", color="#28a745")
    plt.xlabel("Decision Threshold")
    plt.ylabel("Score")
    plt.title(f"Validation Metrics vs Threshold\n{display_name}")
    plt.legend(loc="lower left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out_path = os.path.join(RESULTS_DIR, f"{slug}_training_curves.png")
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_confusion_matrix(slug: str, display_name: str, y_true: np.ndarray, y_score: np.ndarray) -> None:
    y_pred = (y_score >= 0.5).astype(int)
    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(4.5, 4))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(f"Confusion Matrix\n{display_name}")
    plt.colorbar()
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ["No Fracture", "Fracture"], rotation=45)
    plt.yticks(tick_marks, ["No Fracture", "Fracture"])

    thresh = cm.max() / 2.0 if cm.max() > 0 else 0.5
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(
                j,
                i,
                format(cm[i, j], "d"),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
            )

    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()

    out_path = os.path.join(RESULTS_DIR, f"{slug}_confusion_matrix.png")
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_metrics_table(slug: str, display_name: str, metrics: Dict[str, float]) -> None:
    fig, ax = plt.subplots(figsize=(4.8, 2.4))
    ax.axis("off")

    rows = [
        ["Accuracy", f"{metrics['accuracy']:.4f}"],
        ["Precision", f"{metrics['precision']:.4f}"],
        ["Recall", f"{metrics['recall']:.4f}"],
        ["F1-score", f"{metrics['f1']:.4f}"],
    ]

    if not np.isnan(metrics.get("auc", np.nan)):
        rows.append(["AUC", f"{metrics['auc']:.4f}"])

    table = ax.table(
        cellText=rows,
        colLabels=["Metric", "Value"],
        loc="center",
        cellLoc="center",
    )
    table.scale(1, 1.3)
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    ax.set_title(f"Evaluation Metrics\n{display_name}")

    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, f"{slug}_metrics_table.png")
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_curve(slug: str, display_name: str, y_true: np.ndarray, y_score: np.ndarray, auc_val: float) -> None:
    fpr, tpr, _ = roc_curve(y_true, y_score)

    plt.figure(figsize=(4.5, 4))
    plt.plot(fpr, tpr, color="#007bff", lw=2, label=f"ROC curve (AUC = {auc_val:.3f})")
    plt.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--", label="Chance")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC Curve\n{display_name}")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out_path = os.path.join(RESULTS_DIR, f"{slug}_roc_curve.png")
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_sample_outputs(
    slug: str,
    display_name: str,
    df: pd.DataFrame,
    y_true: np.ndarray,
    y_score: np.ndarray,
    image_col: str,
    image_root: str | None,
) -> None:
    from PIL import Image

    y_pred = (y_score >= 0.5).astype(int)

    indices = {
        "TP": np.where((y_true == 1) & (y_pred == 1))[0],
        "TN": np.where((y_true == 0) & (y_pred == 0))[0],
        "FP": np.where((y_true == 0) & (y_pred == 1))[0],
        "FN": np.where((y_true == 1) & (y_pred == 0))[0],
    }

    selected_rows = []
    for kind, idxs in indices.items():
        if len(idxs) == 0:
            continue
        # Take up to 2 examples from each bucket
        for i in idxs[:2]:
            selected_rows.append((kind, i))

    if not selected_rows:
        return

    n = len(selected_rows)
    cols = min(4, n)
    rows_n = int(np.ceil(n / cols))

    fig, axes = plt.subplots(rows_n, cols, figsize=(3 * cols, 3 * rows_n))
    if rows_n == 1:
        axes = np.array([axes])

    for ax in axes.ravel():
        ax.axis("off")

    for ax_idx, (kind, idx) in enumerate(selected_rows):
        r = ax_idx // cols
        c = ax_idx % cols
        ax = axes[r, c]

        row = df.iloc[idx]
        image_path_val = row[image_col]
        full_path = resolve_image_path(str(image_path_val), image_root)
        if not os.path.exists(full_path):
            continue

        try:
            img = Image.open(full_path).convert("L")
            ax.imshow(img, cmap="gray")
            ax.set_title(
                f"{kind}\nP={y_score[idx]:.2f}, Y={y_true[idx]}",
                fontsize=8,
            )
            ax.axis("off")
        except Exception:
            continue

    plt.suptitle(f"Sample Predictions\n{display_name}", fontsize=11)
    plt.tight_layout(rect=[0, 0, 1, 0.92])

    out_path = os.path.join(RESULTS_DIR, f"{slug}_sample_outputs.png")
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_overall_comparison(all_metrics: List[Dict[str, float]]) -> None:
    """Create a comparison figure and save it under each model slug.

    Frontend expects <slug>_comparison.png for each model; we generate one
    comparison chart and save it multiple times.
    """

    if not all_metrics:
        return

    labels = [m["display_name"] for m in all_metrics]
    accs = [m["metrics"]["accuracy"] for m in all_metrics]
    f1s = [m["metrics"]["f1"] for m in all_metrics]
    aucs = [m["metrics"].get("auc", float("nan")) for m in all_metrics]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(1.6 + 1.4 * len(labels), 4.2))

    ax.bar(x - width, accs, width, label="Accuracy")
    ax.bar(x, f1s, width, label="F1-score")
    ax.bar(x + width, aucs, width, label="AUC")

    ax.set_ylabel("Score")
    ax.set_title("Model Comparison (Evaluation Metrics)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="lower right")
    ax.grid(True, axis="y", alpha=0.3)

    plt.tight_layout()

    # Save the same comparison chart under each slug so the
    # frontend tiles can use <slug>_comparison.png.
    for m in all_metrics:
        slug = m["slug"]
        out_path = os.path.join(RESULTS_DIR, f"{slug}_comparison.png")
        plt.savefig(out_path, dpi=150)

    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate fracture models on a labeled CSV and generate real "
            "PNG plots into the 'results' folder for the frontend Outputs panel."
        )
    )

    parser.add_argument("--csv_path", required=True, help="Path to CSV file with labels")
    parser.add_argument(
        "--image_root",
        default=None,
        help=(
            "Optional root folder for relative image paths in the CSV. "
            "If omitted, paths are treated as relative to the project root."
        ),
    )
    parser.add_argument(
        "--image_col",
        default="image_path",
        help="Column name in CSV that contains image paths (default: image_path)",
    )
    parser.add_argument(
        "--label_col",
        default="label",
        help="Column name in CSV that contains labels (default: label)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of rows to evaluate (for quick tests)",
    )

    args = parser.parse_args()

    csv_path = os.path.abspath(args.csv_path)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Models dir   : {MODELS_DIR}")
    print(f"Results dir  : {RESULTS_DIR}")
    print(f"CSV path     : {csv_path}")
    if args.image_root:
        print(f"Image root   : {os.path.abspath(args.image_root)}")

    df = pd.read_csv(csv_path)

    if args.image_col not in df.columns:
        raise KeyError(f"Column '{args.image_col}' not found in CSV columns: {list(df.columns)}")
    if args.label_col not in df.columns:
        raise KeyError(f"Column '{args.label_col}' not found in CSV columns: {list(df.columns)}")

    all_metrics: List[Dict[str, object]] = []

    for config in MODEL_CONFIGS:
        try:
            y_true, y_score, metrics = evaluate_single_model(
                config,
                df,
                image_col=args.image_col,
                label_col=args.label_col,
                image_root=args.image_root,
                limit=args.limit,
            )

            plot_training_like_curves(config["slug"], config["display_name"], y_true, y_score)
            plot_confusion_matrix(config["slug"], config["display_name"], y_true, y_score)
            plot_metrics_table(config["slug"], config["display_name"], metrics)
            if not np.isnan(metrics.get("auc", np.nan)):
                plot_roc_curve(config["slug"], config["display_name"], y_true, y_score, metrics["auc"])
            plot_sample_outputs(
                config["slug"],
                config["display_name"],
                df,
                y_true,
                y_score,
                image_col=args.image_col,
                image_root=args.image_root,
            )

            all_metrics.append(
                {
                    "slug": config["slug"],
                    "display_name": config["display_name"],
                    "metrics": metrics,
                }
            )
        except FileNotFoundError as e:
            print(f"[SKIP] {config['display_name']}: {e}")
        except Exception as e:
            print(f"[ERROR] Failed evaluating {config['display_name']}: {e}")

    if all_metrics:
        plot_overall_comparison(all_metrics)
        print("\nAll evaluation plots saved to:", RESULTS_DIR)
    else:
        print("\nNo models were successfully evaluated. Check paths and CSV configuration.")


if __name__ == "__main__":
    main()
