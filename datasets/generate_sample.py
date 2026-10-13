import numpy as np
import pandas as pd


def generate_sample_dataset(n_row:int = 500, seed: int = 42)->pd.DataFrame:
    rng=np.random.default_rng(seed)
    x1 = rng.normal(0,1,n_row)
    x2 = rng.normal(0,1,n_row)
    x3 = rng.normal(0,1,n_row)
    label = (x1+x2-x3>0).astype(int)
    return pd.DataFrame({"x1":x1,"x2":x2,"x3":x3,"label":label})


if __name__=="__main__":
    df = generate_sample_dataset()
    df.to_csv("dataset/sample.csv",index=False)
    print(f"Wrote {len(df)} row to dataset/sample.csv")