from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import pandas as pd
from scipy import stats
import plotly.graph_objects as go
import dataframe_image as dfi
import warnings
warnings.filterwarnings('ignore')

test = pd.read_csv('./files/test.csv')
population = pd.read_csv('./files/population.csv')

test.index=test['custid']
test.drop(['custid'],axis=1,inplace=True)
df_test = test.head()
df_test.dfi.export('./files/df_test.png')

population.index=population['custid']
population.drop(['custid'],axis=1,inplace=True)
population.head()

test_unique=list(test.index.unique())
population_1=population.drop(test_unique)
df_pop = population_1.head()
df_pop.dfi.export('./files/df_pop.png')

stats_pop = population.describe()
df_styled_stats_pop = stats_pop.style.background_gradient()
dfi.export(df_styled_stats_pop,'./files/stats_pop.png')


def pair_algo(treated_df, non_treated_df):
    treated_x = treated_df.values
    non_treated_x = non_treated_df.values

    scaler = StandardScaler()

    scaler.fit(treated_x)
    treated_x = scaler.transform(treated_x)
    non_treated_x = scaler.transform(non_treated_x)

    nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(non_treated_x)
    distances, indices = nbrs.kneighbors(treated_x)
    indices = indices.reshape(indices.shape[0])
    matched = non_treated_df.iloc[indices]
    return matched


matched_df = pair_algo(test, population_1)

final_test_cnt=pd.concat([pd.DataFrame(list(test.index),columns=['Test']),
                         pd.DataFrame(list(matched_df.index),columns=['Control'])],axis=1)

final_test_cnt.to_csv("./static/output.csv", index=False)

test_control_pair = final_test_cnt.head(10)
test_control_pair = test_control_pair.style.hide_index()
dfi.export(test_control_pair,'./files/test_control_pair.png')


scaler = StandardScaler()
scaler.fit(test)
test_scaled= scaler.transform(test)
test_scaled=pd.DataFrame(test_scaled)
test_scaled

scaler = StandardScaler()
scaler.fit(matched_df)
matched_scaled= scaler.transform(matched_df)
matched_scaled=pd.DataFrame(matched_scaled)
matched_scaled


fig = go.Figure()
# Add traces

fig.add_trace(go.Scatter(x=test_scaled[0], y=test_scaled[1],
                    mode='markers',hovertext=test_scaled.index,
                    name='Test',marker_symbol='square'))

fig.add_trace(go.Scatter(x=matched_scaled[0], y=matched_scaled[1],
                    mode='markers',hovertext=matched_scaled.index,
                    name='Control',marker_symbol='x'))

# fig.show()
# plotly.offline.plot(fig,filename='positives.html',config={'displayModeBar': False})

fig.write_html("templates/graph.html")

matched = matched_df.describe()
df_styled_matched = matched.style.background_gradient()
dfi.export(df_styled_matched,'./files/stats_control.png')

stats_test = test.describe()
df_styled_test = stats_test.style.background_gradient()
dfi.export(df_styled_test,'./files/stats_test.png')

# x = list(test.columns)
# l = len(x)
# stats_data = []
# for i in range(l):
#     t_value, p_value = stats.ttest_ind(test[x[i]], matched_df[x[i]])
#     stats_data.append([x[i], t_value, p_value])
#
# stats_data = pd.DataFrame(stats_data, columns=['var', 't-test', 'p-value'])

x = list(test.columns)
l = len(x)
stats_data = []
for i in range(l):
    t_value, p_value = stats.ttest_ind(test[x[i]], matched_df[x[i]])
    stats_data.append([x[i], t_value, p_value])
stats_data = pd.DataFrame(stats_data, columns=['var', 't-test', 'p-value'])
def f1(x):
    if x > 0.05:
        return ('Pass at 95% confidence interval')
    elif x > 0.1:
        return ('Pass at 90% confidence interval')
    elif x > 0.15:
        return ('Pass at 80% confidence interval')
    else:
        return ('Fail')
stats_data['Result'] = stats_data['p-value'].apply(f1)
df_styled_data = stats_data.style.background_gradient()
dfi.export(df_styled_data, './files/t_test.png',
          )


# test.index=test['custid']
# test.drop(['custid'],axis=1,inplace=True)
# df_test = test.head()
# df_test.dfi.export('./static/df_test.png')
#
# population.index=population['custid']
# population.drop(['custid'],axis=1,inplace=True)
# df_pop = population.head()
# df_pop.dfi.export('./static/df_pop.png')
#
# def pair_algo(treated_df, non_treated_df):
#     treated_x = treated_df.values
#     non_treated_x = non_treated_df.values
#
#     scaler = StandardScaler()
#
#     scaler.fit(treated_x)
#     treated_x = scaler.transform(treated_x)
#     non_treated_x = scaler.transform(non_treated_x)
#
#     nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(non_treated_x)
#     distances, indices = nbrs.kneighbors(treated_x)
#     indices = indices.reshape(indices.shape[0])
#     matched = non_treated_df.iloc[indices]
#     return matched
#
# matched_df = pair_algo(test, population)
#
# final_test_cnt=pd.concat([pd.DataFrame(list(test.index),columns=['test']),
#                          pd.DataFrame(list(matched_df.index),columns=['matched'])],axis=1)
#
# test_control_pair = final_test_cnt.head(10)
# test_control_pair.dfi.export('./static/test_control_pair.png')
#
# fig = go.Figure()
# # Add traces
# fig.add_trace(go.Scatter(x=population['spend_1m'], y=population['visit_6m'],
#                     mode='markers',
#                     name='Population',hovertext=population.index))
# fig.add_trace(go.Scatter(x=test['spend_1m'], y=test['visit_6m'],
#                     mode='markers',hovertext=population.index,
#                     name='Test',marker_symbol='square'))
#
# fig.add_trace(go.Scatter(x=matched_df['spend_1m'], y=matched_df['visit_6m'],
#                     mode='markers',hovertext=population.index,
#                     name='Control',marker_symbol='x'))
# # fig.show()
# fig.write_html("templates/graph.html")
#
# matched = matched_df.describe()
# df_styled_matched = matched.style.background_gradient()
# dfi.export(df_styled_matched,'./static/stats_control.png')
#
# stats_test = test.describe()
# df_styled_test = stats_test.style.background_gradient()
# dfi.export(df_styled_test,'./static/stats_test.png')
#
# x = list(test.columns)
# l = len(x)
# stats_data = []
# for i in range(l):
#     t_value, p_value = stats.ttest_ind(test[x[i]], matched_df[x[i]])
#     stats_data.append([x[i], t_value, p_value])
#
# stats_data = pd.DataFrame(stats_data, columns=['var', 't-test', 'p-value'])
#
#
# def f1(x):
#     if x > 0.05:
#         return ('Pass')
#     else:
#         return ('Fail')
#
#
# stats_data['Result'] = stats_data['p-value'].apply(f1)
# df_styled_data = stats_data.style.background_gradient()
# dfi.export(df_styled_data, './static/t_test.png',
#           )


