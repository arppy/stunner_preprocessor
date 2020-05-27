#! /usr/bin/python
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

#filenamePrefix='1-1'
#filenamePrefix='0-1'
filenamePrefix='1-0'

#pd.options.display.float_format = '{:,.2f}'.format
df = pd.read_csv(filenamePrefix+'SessionLengthDist_v1.csv',index_col='Length (ln)',skipfooter=1)
df = df.apply(pd.to_numeric)
#df.replace(to_replace="np.nan", value=np.nan, regex=False)
print(df.columns)
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(df)
    
dfmask = df.isnull()    
ax = sns.heatmap(df,mask=dfmask,cmap="plasma")
ax.invert_yaxis()
#titleStr="FC - Full cone | RC - Restricted cone\nPRC - Port restricted cone | SC - Symmetric cone";
#titleStr="OA - Open access | FC - Full cone | RC - Restricted cone\nPRC - Port restricted cone | SC - Symmetric cone\nSF - Symmetric UDP firewall | FB - Firewall blocks | N/A - NAT type is missing";
#legen = ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(-0.15,1.17),title=titleStr)
#legen._legend_box.align = "right"
#ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%f'))
ax.xaxis.set_minor_formatter(ticker.FormatStrFormatter('%f'))
if filenamePrefix == '1-1' :
    plt.ylabel('available session length (ln)')
    plt.xlabel('available session length (ln)')
elif filenamePrefix == '0-1' :
    plt.ylabel('unavailable session length (ln)')
    plt.xlabel('available session length (ln)')
elif filenamePrefix == '1-0' :
    plt.ylabel('available session length (ln)')
    plt.xlabel('unavailable session length (ln)')
#loc, labels = plt.xticks()
#for label in labels :
#  xticStr=float(label.get_text())
#  xticStr='{:06.2f}'.format(xticStr)
#  label.set_text(xticStr)
#for label in labels:
#  print(label)
plt.show()