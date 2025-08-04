# Anime-Recommendation-System
A content-based Anime Recommendation System using the MyAnimeList dataset with tag vectorization and metadata preprocessing.

## Dataset

The dataset is publicly available on Kaggle: [MyAnimeList Dataset](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset?select=final_animedataset.csv)

Make sure to download `final_animedataset.csv` and place it in your project directory. Update the notebook path if needed.

## Features

- Anime metadata cleaning and sampling
- Tag vectorization using TF-IDF
- Content-based filtering using cosine similarity
- Visualizations with Seaborn and Matplotlib
- Optional classification with K-Nearest Neighbors (KNN)


## Getting Started

### Option 1: Run Locally

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/anime-recommendation-system.git
cd anime-recommendation-system
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

3. Run the Notebook
Launch Jupyter Notebook or VS Code and open:

```bash
animeml.ipynb
```
Update this line in the notebook if needed to point to the correct dataset path:

```python
df = pd.read_csv('final_animedataset.csv')
```

---

### Option 2: Use Google Colab or Kaggle (No Install Required)
#### Google Colab

1. Upload the notebook and dataset to your Google Drive or Colab session.

2. Mount your drive or upload the CSV directly in the session.

#### Kaggle Kernels

4. Create a new Kaggle notebook and attach the dataset via the "Add Data" sidebar.

5. Ensure this line reflects the dataset path:

```python
df = pd.read_csv('/kaggle/input/myanimelist-dataset/final_animedataset.csv')
# Using Colab or Kaggle is recommended for quick setup without installing anything locally.
```
