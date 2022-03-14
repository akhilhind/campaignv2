from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import plotly

file = open("static/uploads/file.txt","r")
file1 = open("static/uploads/data.txt","r")
content = file.readlines()
content1 = file1.readlines()
test_control_file = content[0][:-1]
performance_file = content[1][:-1]
cost = int(content1[0][:-1])
period = int(content1[1])
file.close()
file1.close()
test_cnt=pd.read_csv('./static/uploads/{}'.format(test_control_file))
performance=pd.read_csv('./static/uploads/{}'.format(performance_file))

test_cnt.head()
performance.head()

cust_in_camp_value = len(test_cnt)
print(cust_in_camp_value)

df1 = performance.copy()
df1.drop(['custid'],axis=1,inplace=True)

df2 = df1.groupby(['flag']).mean()

df3=df2.T
df3['Time(Week)']=df3.index
print(df3)

fig = px.line(df3, x="Time(Week)", y=df3.columns[:-1],title='Performance Test vs Control on aggregate level')
fig.update_layout(yaxis_title="Sales($)")

# fig.show()

fig.write_html("templates/graph_evaluate.html")
# plotly.offline.plot(fig, filename='templates/graph_evaluate.html')

# Calculate KPIs
df3['uplift']=df3['T']-df3['C']

df4=df3.loc['t':]
df5=df4.iloc[:period]
df5

kpi=pd.DataFrame([(df5['uplift'].sum())],columns=['Uplift per customer'])
kpi['#customers in campaign']=len(test_cnt)
kpi['Total uplift']=(df5['uplift'].sum())*len(test_cnt)


kpi['campaign cost']=cost
kpi['ROI']=(kpi['Total uplift']-cost)/cost
kpi['performance window']=str(period )+' weeks'

print(kpi)

import json
data = dict()
data['uplift_value'] = str(kpi['Uplift per customer'][0])
data['scr_value'] = str(kpi['ROI'][0])
data['total_uplift_value'] = str(kpi['Total uplift'][0])
data['campaign_cost_value'] = str(kpi['campaign cost'][0])
data['performance_wind_value'] = str(kpi['performance window'][0].split()[0])
data['cust_in_camp_value'] = str(cust_in_camp_value)
f = open ('static/uploads/eval.txt','w')
f.write(json.dumps(data))
f.close()