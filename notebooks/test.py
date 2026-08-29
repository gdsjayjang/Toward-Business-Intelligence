from src.raw_loader import load_raw_customers
from src.segmentation import assign_segments

df = assign_segments(load_raw_customers())
print(df["segment"].value_counts())
print(df["segment"].value_counts(normalize=True).round(3))

'''
결과
segment
일반      607196
충성      304200
이탈위험    193465
VIP     181310
신규       76110

segment
일반      0.446
충성      0.223
이탈위험    0.142
VIP     0.133
신규      0.056
'''