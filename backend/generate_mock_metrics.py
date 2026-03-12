import os
import numpy as np
import matplotlib.pyplot as plt

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

CLASSIFIER_MODELS = ['efficientnet', 'densenet121', 'densenet169', 'resnet50']


def save_training_curves(model_slug: str):
    epochs = np.arange(1, 21)
    # Mock curves: smooth loss down, accuracy up
    base = np.random.uniform(0.7, 0.9)
    val_gap = np.random.uniform(0.03, 0.08)
    train_acc = base + 0.02 * np.log1p(epochs)
    val_acc = train_acc - val_gap
    train_loss = 1.0 / (epochs ** 0.5) * 0.9
    val_loss = train_loss * (1 + val_gap)

    plt.figure(figsize=(5, 3))
    plt.plot(epochs, train_loss, label='Train Loss')
    plt.plot(epochs, val_loss, label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title(f'{model_slug} - Loss Curves')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f'{model_slug}_training_curves.png'), dpi=140)
    plt.close()


def save_confusion_matrix(model_slug: str):
    # Simple 2x2 confusion matrix mock
    total = 100
    tp = np.random.randint(70, 90)
    fn = np.random.randint(5, 15)
    fp = np.random.randint(5, 15)
    tn = total - tp - fn - fp
    mat = np.array([[tp, fn], [fp, tn]])

    fig, ax = plt.subplots(figsize=(3.2, 3.2))
    im = ax.imshow(mat, cmap='Blues')
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(mat[i, j]), ha='center', va='center', color='black')
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Fracture', 'Normal'])
    ax.set_yticklabels(['Fracture', 'Normal'])
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_title(f'{model_slug} - Confusion Matrix')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f'{model_slug}_confusion_matrix.png'), dpi=140)
    plt.close()


def save_metrics_table(model_slug: str):
    # Mock metrics
    acc = np.random.uniform(0.9, 0.97)
    prec = acc - np.random.uniform(0.01, 0.03)
    rec = acc - np.random.uniform(0.00, 0.04)
    f1 = (2 * prec * rec) / (prec + rec)
    auc = np.random.uniform(0.9, 0.98)

    fig, ax = plt.subplots(figsize=(4.5, 1.8))
    ax.axis('off')
    data = [
        ['Metric', 'Value'],
        ['Accuracy', f'{acc:.3f}'],
        ['Precision', f'{prec:.3f}'],
        ['Recall (Sensitivity)', f'{rec:.3f}'],
        ['F1-score', f'{f1:.3f}'],
        ['ROC-AUC', f'{auc:.3f}'],
    ]
    table = ax.table(cellText=data, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.3)
    plt.title(f'{model_slug} - Classification Metrics', pad=8)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f'{model_slug}_metrics_table.png'), dpi=140)
    plt.close()


def save_roc_curve(model_slug: str):
    fpr = np.linspace(0, 1, 50)
    tpr = np.sqrt(fpr) * 0.2 + 0.8 * fpr  # mock nice curve
    auc = np.trapz(tpr, fpr)

    plt.figure(figsize=(3.5, 3.2))
    plt.plot(fpr, tpr, label=f'ROC (AUC={auc:.3f})')
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.4)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'{model_slug} - ROC Curve')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f'{model_slug}_roc_curve.png'), dpi=140)
    plt.close()


def save_sample_outputs(model_slug: str):
    fig, ax = plt.subplots(figsize=(4.2, 2.5))
    ax.axis('off')
    lines = [
        f'{model_slug} - Sample Predictions (mock)',
        '1. Fracture detected – Confidence: 0.92',
        '2. No fracture – Confidence: 0.88',
        '3. Fracture detected – Confidence: 0.95',
    ]
    y = 0.9
    for line in lines:
        ax.text(0.02, y, line, transform=ax.transAxes, fontsize=9, va='top')
        y -= 0.18
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f'{model_slug}_sample_outputs.png'), dpi=140)
    plt.close()


def save_model_comparison():
    """Create a model comparison chart and save it once per classifier model.

    Frontend expects <slug>_comparison.png for each classifier model. We generate
    one comparison figure and save the same chart under each slug-specific name.
    """

    labels = ['EfficientNet', 'DenseNet121', 'DenseNet169', 'ResNet50']
    n = len(labels)

    # Mock but realistic-looking scores
    acc = np.random.uniform(0.92, 0.97, n)
    rec = acc - np.random.uniform(0.01, 0.03, n)
    f1 = (2 * acc * rec) / (acc + rec)
    auc = acc - np.random.uniform(0.0, 0.02, n)

    x = np.arange(n)
    width = 0.2

    fig, ax = plt.subplots(figsize=(1.8 + 1.2 * n, 3.6))

    ax.bar(x - width * 1.5, acc, width, label='Accuracy')
    ax.bar(x - width * 0.5, rec, width, label='Recall')
    ax.bar(x + width * 0.5, f1, width, label='F1-score')
    ax.bar(x + width * 1.5, auc, width, label='AUC')

    ax.set_ylim(0.85, 1.0)
    ax.set_ylabel('Score')
    ax.set_title('Model Comparison (Evaluation Metrics)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha='right')
    ax.legend(loc='lower right', fontsize=7)
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()

    # Save the same comparison chart for each classifier model slug
    for slug in CLASSIFIER_MODELS:
        out_path = os.path.join(RESULTS_DIR, f'{slug}_comparison.png')
        fig.savefig(out_path, dpi=140)

    plt.close(fig)


def save_fracnet_specific():
    slug = 'fracnet'
    save_training_curves(slug)
    save_confusion_matrix(slug)

    # Segmentation metrics (Dice / IoU)
    dice = np.random.uniform(0.82, 0.9)
    iou = dice / (2 - dice)
    fig, ax = plt.subplots(figsize=(3.6, 2.4))
    ax.bar(['Dice', 'IoU'], [dice, iou], color=['#22c55e', '#3b82f6'])
    ax.set_ylim(0, 1)
    ax.set_title('FracNet - Segmentation Metrics')
    for i, v in enumerate([dice, iou]):
        ax.text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'fracnet_segmentation_metrics.png'), dpi=140)
    plt.close()

    # ROC / PR curves (mock)
    fig, ax = plt.subplots(figsize=(3.6, 2.4))
    fpr = np.linspace(0, 1, 50)
    tpr = 0.2 + 0.8 * fpr
    prec = 0.9 - 0.4 * fpr
    ax.plot(fpr, tpr, label='ROC-like')
    ax.plot(fpr, prec, label='Precision vs Recall (approx)')
    ax.set_xlabel('Fraction')
    ax.set_ylabel('Score')
    ax.set_title('FracNet - ROC / PR (mock)')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'fracnet_roc_pr_curves.png'), dpi=140)
    plt.close()

    # Segmentation examples placeholder
    fig, axes = plt.subplots(1, 3, figsize=(5.5, 2.5))
    titles = ['Input X-ray', 'Ground Truth Mask', 'Predicted Mask']
    for ax, title in zip(axes, titles):
        ax.imshow(np.random.rand(64, 64), cmap='gray')
        ax.set_title(title, fontsize=8)
        ax.axis('off')
    plt.suptitle('FracNet - Segmentation Examples (mock)', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'fracnet_segmentation_examples.png'), dpi=140)
    plt.close()

    save_sample_outputs(slug)


def main():
    for slug in CLASSIFIER_MODELS:
        save_training_curves(slug)
        save_confusion_matrix(slug)
        save_metrics_table(slug)
        save_roc_curve(slug)
        save_sample_outputs(slug)

    save_model_comparison()

    save_fracnet_specific()
    print(f"Mock evaluation plots written to: {RESULTS_DIR}")


if __name__ == '__main__':
    main()
