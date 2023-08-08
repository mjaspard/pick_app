#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import sys
from matplotlib.dates import DateFormatter



csv_file = sys.argv[1]

df = pd.read_csv(csv_file, parse_dates=['img_date'])

plt.plot(df['img_date'], df['shadow1_depth'], label="shadow 1")
plt.plot(df['img_date'], df['shadow2_depth'], label="shadow 2")
plt.xlabel('Date')
plt.ylabel('Value')
plt.title('Your Plot Title')
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.tight_layout()  # Adjust layout for better appearance
# plt.show()



plt.xlabel('Date')
plt.ylabel('Value')
plt.title('Shadow')

date_format = DateFormatter('%Y-%d-%m')  # Customize the date format
plt.gca().xaxis.set_major_formatter(date_format)
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend()
plt.show()