This notebook walks you through fine-tuning a text classifier on your annotated dataset and comparing it to a zero-shot baseline.

What this notebook does for you (infrastructure):

Tokenizes your dataset and prepares it for training
Runs the fine-tuning pipeline with DistilBERT
Computes evaluation metrics and generates a confusion matrix
Runs the Groq baseline and compares both models
What you do (the actual work):

Collect and annotate your 200+ examples (done before opening this notebook)
Define your label map and upload your CSV
Write your Groq classification prompt using your label definitions
Analyze the output and write your evaluation report
