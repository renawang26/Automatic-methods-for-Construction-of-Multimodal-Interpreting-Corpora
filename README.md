# Automatic-methods-for-Construction-of-Multimodal-Interpreting-Corpora

In the realm of Automatic Speech Recognition (ASR), seminal research by Sharp et al. (1997) and Santiago et al. (2017) has underscored the technology's burgeoning prevalence and recognition across a spectrum of disciplines, culminating in its findings being deemed worthy of academic publication. The focal point of this study is to scrutinize the potential of leveraging ASR confidence scores as predictors for the intensity of human post-editing intervention. ASR frameworks assign a probabilistic confidence metric to each discerned word, indicative of the likelihood of its accurate recognition, a concept thoroughly expounded by Wessel et al. (2001). These confidence indices are quantified on a continuum from 0 to 1.

In alignment with this theoretical framework, we have formulated an R-based algorithmic script, expressly for examining the correlation between the post-editing ratio and the ASR-derived confidence indices. This analytical endeavor employs a logistic regression model to quantitatively delineate this relationship.

The code included the following functionalities:

- Utilization of IBM's cloud-based services for converting speech to text.
- Processing and analysis of the transcribed output to identify paraverbal elements.
- Quantitative assessment of the correlation between post-editing requirements and the ASR confidence scores.
