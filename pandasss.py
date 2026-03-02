import pandas as pd

df = pd.read_excel("PENDING ICARD  DATA  OTHER COLLEGE STUDENT.xlsx")

print(df.head())
print(df.keys())

df.to_excel("output.xlsx", index=True)