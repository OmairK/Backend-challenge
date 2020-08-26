import csv
import pandas as pd

df = pd.read_csv("dummy.csv")
df.to_json("dummy.json")