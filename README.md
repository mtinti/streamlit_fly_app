# 🧬 Peptide Detectability Predictor

A web application for predicting peptide detectability in mass spectrometry experiments using deep learning.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 🎯 Overview

This tool helps researchers predict which peptides from a protein sequence are likely to be detected by mass spectrometry. It uses a deep learning model trained on large-scale proteomics datasets to classify peptides into detectability categories.

### Features

- ✅ FASTA format input support
- ✅ In silico trypsin digestion
- ✅ Deep learning-based detectability prediction
- ✅ Interactive protein visualization
- ✅ Detailed peptide-level results
- ✅ Downloadable CSV and HTML reports
- ✅ Real-time statistics and coverage analysis

## 🚀 Quick Start

### Online (Recommended)

Visit the deployed app: **[https://your-app-url.streamlit.app](https://your-app-url.streamlit.app)**

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wilhelm-lab/dlomix.git
   cd dlomix/streamlit_app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser:**
   The app will automatically open at `http://localhost:8501`

## 📋 Usage

### Input Format

Provide your protein sequence in FASTA format:

```
>sp|P69905|HBA_HUMAN Hemoglobin subunit alpha
MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGH
GKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEF
TPAVHASLDKFLASVSTVLTSKYR
```

### Workflow

1. **Input**: Enter or paste your protein sequence
2. **Digest**: The tool performs in silico trypsin digestion
3. **Predict**: Each peptide is classified using the trained model
4. **Visualize**: View results in an interactive protein map
5. **Download**: Export results as CSV or HTML

### Output

The tool provides:

- **Protein Detectability Map**: Color-coded visualization showing which regions are detectable
  - 🟢 Green: Flyer peptides (detectable)
  - 🟣 Purple: Non-Flyer peptides (low detection)
  - ⚪ Gray: Not covered

- **Peptide Table**: Detailed predictions for each peptide including:
  - Sequence and position
  - Predicted class (Non-Flyer, Weak, Intermediate, Strong Flyer)
  - Probability scores for each class

- **Statistics**: Summary metrics including:
  - Total peptides found
  - Flyer vs Non-Flyer counts
  - Sequence coverage percentage

## 🤖 Model Information

### Architecture

- **Type**: Bidirectional GRU with Attention
- **Input**: Peptide sequences (max 40 amino acids)
- **Output**: 4-class classification
- **Framework**: TensorFlow 2.15

### Training Data

The model was trained on:
- **ProteomeTools**: Synthetic peptide library (PXD004732, PXD010595, PXD021013)
- **MAssIVE Dataset**: Large-scale proteomics data (PXD024364)

### Classes

- **Non-Flyer** (Class 0): Low or no MS detection
- **Weak Flyer** (Class 1): Moderate detection probability
- **Intermediate Flyer** (Class 2): Good detection probability
- **Strong Flyer** (Class 3): High detection probability

### Performance

- Training Accuracy: ~65%
- Validation Accuracy: ~65%
- Binary Accuracy (Flyer vs Non-Flyer): ~94%

## 📁 Project Structure

```
streamlit_app/
├── streamlit_app.py          # Main application
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── models/
│   └── detectability_model/  # Trained TensorFlow model
└── utils/
    ├── __init__.py
    ├── sequence_processing.py # FASTA parsing, trypsin digestion
    ├── prediction.py          # Model loading and inference
    └── visualization.py       # HTML generation and stats
```

## ⚙️ Configuration

### Model Loading

The app uses a weights-only approach for model loading:
- Model architecture is created from dlomix's `DetectabilityModel`
- Weights are loaded from the training checkpoint
- This avoids Keras SavedModel serialization issues

### Parameters

You can adjust these parameters in the app sidebar:

- **Min Peptide Length**: Minimum peptide length to include (default: 6)
- **Max Peptide Length**: Maximum peptide length to include (default: 40)

### Trypsin Digestion

The tool simulates trypsin digestion by:
- Cleaving after **K** (Lysine) or **R** (Arginine)
- **Not** cleaving before **P** (Proline)

## 🔧 Development

### Adding New Features

1. Create a new branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. Make your changes

3. Test locally:
   ```bash
   streamlit run streamlit_app.py
   ```

4. Commit and push:
   ```bash
   git add .
   git commit -m "Add new feature"
   git push origin feature/my-new-feature
   ```

### Testing

Run the app with test data:

```python
# In Python console
from utils import parse_fasta, trypsin_digest, load_model, predict_batch

# Test sequence parsing
protein_id, seq = parse_fasta(">Test\nMVLSPADK")
print(protein_id, seq)

# Test digestion
peptides = trypsin_digest(seq)
print(peptides)

# Test model
model = load_model()
predictions = predict_batch(peptides, model)
print(predictions)
```

## 🚢 Deployment

### Streamlit Cloud (Free)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository: `your-username/dlomix`
   - Set main file path: `streamlit_app/streamlit_app.py`
   - Click "Deploy!"

3. **Configure** (if needed):
   - Python version: 3.9
   - Advanced settings: Add secrets if required

### Alternative Deployments

- **Heroku**: Use Dockerfile
- **AWS**: Deploy with ECS/Lambda
- **Google Cloud**: Use Cloud Run
- **Docker**: See `Dockerfile` (to be created)

## 📊 Resource Usage

### Streamlit Cloud Free Tier

- **Memory**: 1 GB RAM (sufficient for this app)
- **CPU**: 1 core shared
- **Storage**: Model size ~8 MB
- **Bandwidth**: Unlimited (fair use)

### Performance

- **Model load time**: ~2-3 seconds (cached after first load)
- **Prediction time**: ~0.1-0.5 seconds per peptide
- **Page load**: ~1-2 seconds

## 🐛 Troubleshooting

### Common Issues

**Issue**: Model not found error
```
Solution: Ensure models/detectability_model/ exists and contains all model files
```

**Issue**: Import errors
```
Solution: Make sure all dependencies are installed: pip install -r requirements.txt
```

**Issue**: Slow predictions
```
Solution: Model caching should help. If still slow, reduce max peptide length.
```

**Issue**: App crashes on large proteins
```
Solution: Split very large proteins or increase memory limits
```

### Getting Help

- Check the [Issues](https://github.com/wilhelm-lab/dlomix/issues) page
- Read the [DLOmix Documentation](https://dlomix.readthedocs.io)
- Contact: dlomix@tum.de

## 📚 Citation

If you use this tool in your research, please cite:

```bibtex
@article{dlomix2024,
  title={DLOmix: A Deep Learning Framework for Proteomics},
  author={Wilhelm Lab},
  journal={Bioinformatics},
  year={2024}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- **Wilhelm Lab** at TU Munich for developing DLOmix
- **ProteomeTools** project for training data
- **MAssIVE** repository for proteomics datasets
- **Streamlit** for the amazing web app framework

## 🔗 Links

- **DLOmix GitHub**: https://github.com/wilhelm-lab/dlomix
- **Documentation**: https://dlomix.readthedocs.io
- **Streamlit**: https://streamlit.io
- **TensorFlow**: https://tensorflow.org

## 📝 Changelog

### Version 1.0 (2024-11-24)

- ✅ Initial release
- ✅ FASTA input support
- ✅ Trypsin digestion
- ✅ Detectability prediction
- ✅ Interactive visualization
- ✅ CSV/HTML export

---

**Made with ❤️ by the DLOmix Team**
