from PIL import Image
from pathlib  import Path
import numpy as np

from feature_extractor import FeatureExtractor


if __name__ == "__main__":
  fe = FeatureExtractor()
  for img_path in sorted(Path("project/static/f-images").glob("*.jpg")):
    print(img_path)
    feature = fe.extract(img=Image.open(img_path))

    feature_path = Path("project/static/feature") / (img_path.stem + ".npy")
    print(feature_path)
    print('here4')
    np.save(feature_path, feature)

