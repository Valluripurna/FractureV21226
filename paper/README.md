# FractureDetect AI Conference Paper

This directory contains the LaTeX source files for the conference paper titled "FractureDetect AI: A Deep Learning System for Automated Bone Fracture Detection in X-Ray Images".

## Files Included

- `fracturedetect_ai_paper.tex` - Main LaTeX source file
- `references.bib` - Bibliography file in BibTeX format
- `figures/` - Directory for figure files (currently empty, to be populated)

## Compilation Instructions

To compile the paper, you will need a LaTeX distribution such as TeX Live or MiKTeX. Use the following commands:

```bash
pdflatex fracturedetect_ai_paper.tex
bibtex fracturedetect_ai_paper.aux
pdflatex fracturedetect_ai_paper.tex
pdflatex fracturedetect_ai_paper.tex
```

Alternatively, you can use a LaTeX editor like TeXstudio or Overleaf for easier compilation.

## Paper Abstract

Bone fractures are among the most common injuries worldwide, requiring prompt and accurate diagnosis for effective treatment. Traditional fracture detection relies heavily on radiologists' expertise, which can be time-consuming and subject to human error. This paper presents FractureDetect AI, a novel deep learning system designed to automatically detect bone fractures in X-ray images. Our system employs an ensemble of five state-of-the-art convolutional neural networks, including ResNet50, DenseNet121, EfficientNet-B0, FracNet, and a specialized MURA model. The system integrates MongoDB for persistent data storage, implements secure JWT-based authentication, and provides comprehensive PDF reporting with medical recommendations. Experimental results demonstrate that our system achieves up to 95% accuracy in fracture detection, with EfficientNet-B0 performing as the best individual model. The system offers significant potential for clinical applications, particularly in resource-limited settings where radiology expertise may be scarce.

## Keywords

deep learning, bone fracture detection, X-ray analysis, computer vision, medical imaging, convolutional neural networks

## Citation

If you use this work in your research, please cite our paper:

```
@inproceedings{valluri2025fracturedetect,
  title={FractureDetect AI: A Deep Learning System for Automated Bone Fracture Detection in X-Ray Images},
  author={Valluri, Purna},
  booktitle={Proceedings of the International Conference on Medical Imaging and Artificial Intelligence},
  year={2025}
}
```