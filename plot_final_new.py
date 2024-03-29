from typing import final


def plotly(df):
    #Required packages
    import pandas as pd
    import numpy as np
    import re
    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    from dash.dependencies import Input, Output
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    import warnings
    warnings.filterwarnings("ignore")

    # Copying the data to a new DataFrame Variable
    dataframe = df

    #. Data Cleaning
    #.. In few matches some of the points scores in a set information is missing,
    #.. so adding some predefined scores for those points
    tournment_name = list(dataframe.tournament.unique())
    new_df = dataframe[dataframe['points'].isnull()]
    new_df = new_df[new_df['set_index'].isin(list(dataframe['set_index'].unique()))]

    if not new_df.empty:
        dataframe.drop(new_df.index[0], inplace=True)
        points_if_1player_winner = ['0-0','15-0','30-0','40-0']
        points_if_2player_winner = ['0-0','0-15','0-30','0-40']
        if new_df['player1_game_score'].tolist()[0] > new_df['player2_game_score'].tolist()[0]:
            x = (points_if_1player_winner)
        else:
            x = (points_if_2player_winner)
        new_df = new_df.append([new_df]*3)
        #.. But for few Melborne Matches in Set three there will be only one set which does not have any scores
        #.. Contains only points, so we are skiping that data and applying this on remaining.
        if tournment_name == 'Melbourne' and new_df.set_index.unique()[0] != 3:
            new_df['points'] = x
            dataframe = dataframe.append(new_df)
            dataframe.reset_index(inplace=True)
            dataframe.drop(['index'], axis=1, inplace=True)


    #. Renaming the round column name to 'round_'
    dataframe.rename(columns={'round':'round_'}, inplace = True)

    #. the Tournament name
    tournament_name = dataframe.tournament.unique()

    #. the Round name 
    round_number = dataframe.round_.unique()

    #. Dropping unrequired columns
    dataframe.drop(['tournament','round_','break_point','result','surface','date'], axis=1, inplace=True)

    #. the players name
    playernames = list(dataframe.player1_name.unique())
    playernames_ = list(dataframe.player2_name.unique())
    playernames.extend(playernames_)

    #. Title for the graph with Color coded for the players name
    if pd.isna(round_number[0]):
        title = " Players: <b style='color:red'>"+playernames[0]+"</b> and <b style='color:green'>"+playernames[1] +"</b> Tournament: "+tournament_name
    else:
        title = " Players: <b style='color:red'>"+playernames[0]+"</b> and <b style='color:green'>"+playernames[1] +"</b> Tournament: "+tournament_name+" Round: "+round_number

    #. Sets a new column as servernumber denotes 0 or 1 on basis of who is the server.
    dataframe['server_number'] = np.where(dataframe['server'] == playernames[0], 0, 1)

    #. In a set for a match there was no points mentioned we could see just scores so adding the scores as points.
    dataframe['points'] = dataframe.apply(lambda x:fill_nan_in_points(x['points'],x['player1_game_score'],x['player2_game_score']),axis = 1)

    #. Split the points from (40-50) to two seperate data like 40, 50 and storing them seperately in two new columns
    #. points_of_1, points_of_2
    dataframe['points_to_list'] = dataframe['points'].apply(split_it)
    dataframe['points_of_1'] = dataframe['points_to_list'].apply(lambda x: x[0])
    dataframe['points_of_2'] = dataframe['points_to_list'].apply(lambda x: x[1])

    #. rename few columns name set_index to set_details for further operations 
    dataframe.rename(columns={'set_index':'set_details'}, inplace = True)

    #. No of sets in the match to use them in plots.
    no_of_sets = dataframe.set_details.unique()

    #. Determining match number for every match in a set.
    dataframe['set_number']= 0
    global i,set_no
    i = 0
    set_no = 0
    dataframe['set_number'] = dataframe.apply(lambda x: set_number_(x['points_to_list'],x['set_details']), axis = 1)

    #. list of no of matches in every set.
    columns_ = []
    for k in no_of_sets:
        set_details_unique_ = dataframe.where(dataframe['set_details']==k).set_number.unique()
        cleanedList = [int(x) for x in set_details_unique_ if str(x) != 'nan']
        columns_.append(max(cleanedList))

    #. Data for the full set Graph.
    game_graph = dataframe[['set_details','player1_game_score','player2_game_score','set_number']]
    dicti = {}
    for i in list(game_graph.set_details.unique()):
        data = game_graph[game_graph['set_details'] == i]
        records = ((data).set_number.unique())
        x=[]
        y=[]
        for j in records:
            data2 = ((data[data['set_number'] == j]).drop_duplicates())
            x.append(data2['player1_game_score'].values[0])
            y.append(data2['player2_game_score'].values[0])
        d1 = dataframe[dataframe['set_details'] == i]
        s2 = d1[d1['set_number'] == records[-1]]
        p1 = s2.at[s2.index[-1],'points_of_1']
        p2 = s2.at[s2.index[-1],'points_of_2']
        if int(p1)>int(p2):
            x.append(x[-1]+1)
            y.append(y[-1])
        elif int(p1)==0 and int(p2)==0:
            x.append(x[-1])
            y.append(y[-1])
        else: 
            x.append(x[-1])
            y.append(y[-1]+1)
        dicti[i] = {'x':x,'y':y}

    #. Adding +5 to every match record for winner to show difference in graph.
    set_numbers_ = list(dataframe['set_details'].unique())
    for r in set_numbers_:
        data_ = dataframe[dataframe['set_details'] == r]
        set_details_ = list(data_['set_number'].unique())
        for rr in set_details_:
            data__ = data_[data_['set_number']  ==rr]
            content = data__.iloc[-1]
            p1 = int(content['points_of_1'])
            p2 = int(content['points_of_2'])
            if rr==13:
                if int(p1) >= 6 or int(p2) >= 6:
                    if int(p1) > int(p2):
                        p1 = int(p1+1)
                    else:
                        p2 = int(p2+1)
                    content['points_of_1'] = p1
                    content['points_of_2'] = p2
                    dataframe = dataframe.append(content,ignore_index = True)
            if int(p1) >= 40 or int(p2) >= 40:
                if int(p1) > int(p2):
                    p1 = int(p1+5)
                else:
                    p2 = int(p2+5)
                content['points_of_1'] = p1
                content['points_of_2'] = p2
                dataframe = dataframe.append(content,ignore_index = True)
    

    #plot    
    dataframe = dataframe[dataframe.points.notnull()]
    
    #Converting tennis points system for equal intervals on the graph by replacing the data in dataframe. 
    dataframe = dataframe.astype({'points_of_1':'string', 'points_of_2':'string' })
    dataframe['points_of_1'] = dataframe['points_of_1'].str.strip()
    dataframe['points_of_2'] = dataframe['points_of_2'].str.strip()

    dataframe['points_of_1'] = dataframe['points_of_1'].replace(['15','30','40','45','50'],['1','2','3','4','5'])
    dataframe['points_of_2'] = dataframe['points_of_2'].replace(['15','30','40','45','50'],['1','2','3','4','5'])

    
    #. Defining subplots rows and columns
    fig = make_subplots(rows=len(no_of_sets) , cols=max(columns_)+ 1)
    #fig.update_layout(yaxis=dict(color="#FFFFFF"))
    xref_value=[]
    yref_value=[]
    y1_value = []
    x1_value = []
    bgcolor_value = 1
    tie_break_xvalue=[]
    tie_break_yvalue=[]

    tie_break_Xaxes=[]
    tie_break_Yaxes=[]
    number=0
    for k in columns_:
        number+=max(columns_)+1
        if k==13:
            tie_break_Xaxes.append('x'+str(number))
            tie_break_Yaxes.append('y'+str(number))



    for k in no_of_sets:
        if k!= 1:
            bgcolor_value = bgcolor_value+max(columns_)+1
        xref_value_ = 'x'+str(bgcolor_value)
        yref_value_ = 'y'+str(bgcolor_value)
        xref_value.append(xref_value_)
        yref_value.append(yref_value_)
        df= dataframe[dataframe['set_details']==k]
        # Identifiying if a match has tie break
        if columns_[k-1]+1 <= 13:
            for r in range(0,columns_[k-1]+1):
                if r==0:

                    # Set Graph
                    max_x = len(dicti[k]['x'])
                    x_ = np.arange(0,max_x,1)
                    y_ = dicti[k]['x']
                    max_1= max(y_)
                    fig.add_trace(go.Scatter(x=x_, y=y_,line_color ="red"),row=k, col=1)
                    max_x= (len(dicti[k]['y']))
                    x_ = x_ = np.arange(0, max_x,1)
                    y_ = dicti[k]['y']
                    max_2 = max(y_)
                    max_= max_1
                    if max_2>max_1:
                        max_= max_2
                    ax = fig.add_trace(go.Scatter(x=x_, y=y_,line_color ="green"),row=k, col=1)

                    #. Annotation used to display a name (set 1) on the set graph
                    fig.add_annotation(dict(font = dict(color = 'black')),
                        x=0, y=max_,
                                text='Set:'+str(k), 
                                showarrow=False,
                                row=k, col=1)
                    x1_value.append(x_[-1])
                    y1_value.append(max_)   
                else:
                    #. Matches Graphs
                    final_df = (df[df['set_number'] == r])
                    max_x= (len(final_df['set_number']))
                    x_ = np.arange(0, max_x,1)
                    fig.add_trace(
                        go.Scatter(x=x_,y=final_df['points_of_1'],line_color = "red"),row=k, col=r+1)
                    fig.add_trace(
                        go.Scatter(x=x_, y=final_df['points_of_2'],line_color ="green"),row=k, col=r+1)
                    lis=[]
                    p2=final_df['points_of_2'].tolist()
                    p1=final_df['points_of_1'].tolist()
                    for i in range(0,len(p2)):
                        if int(p2[i]) >= 3 and int(p1[i]) >= 3:
                            lis.append(5)
                        else:
                            lis.append(4)
                    fig.add_trace(
                        go.Scatter(x=x_, y=lis, line_color="deepskyblue"),row=k, col=r+1)


        else:
            for r in range(0,columns_[k-1]):
                if r==0:

                    # Set Graph
                    max_x = len(dicti[k]['x'])
                    x_ = np.arange(0,max_x,1)
                    y_ = dicti[k]['x']
                    max_1= max(y_)
                    fig.add_trace(go.Scatter(x=x_, y=y_,line_color ="red"),row=k, col=1)
                    max_x= (len(dicti[k]['y']))
                    x_ = x_ = np.arange(0, max_x,1)
                    y_ = dicti[k]['y']
                    max_2 = max(y_)
                    max_= max_1
                    if max_2>max_1:
                        max_= max_2
                    ax = fig.add_trace(go.Scatter(x=x_, y=y_,line_color ="green"),row=k, col=1)

                    #. Annotation used to display a name (set 1) on the set graph
                    fig.add_annotation(dict(font = dict(color = 'black')),
                        x=0, y=max_,
                                text='Set:'+str(k), 
                                showarrow=False,
                                row=k, col=1)
                    x1_value.append(x_[-1])
                    y1_value.append(max_)   
                else:
                    #. Matches Graphs
                    final_df = (df[df['set_number'] == r])
                    max_x= (len(final_df['set_number']))
                    x_ = np.arange(0, max_x,1)
                    fig.add_trace(
                        go.Scatter(x=x_,y=final_df['points_of_1'],line_color = "red"),row=k, col=r+1)
                    fig.add_trace(
                        go.Scatter(x=x_, y=final_df['points_of_2'],line_color ="green"),row=k, col=r+1)
                    lis=[]
                    p2=final_df['points_of_2'].tolist()
                    p1=final_df['points_of_1'].tolist()
                    for i in range(0,len(p2)):
                        if int(p2[i]) >= 3 and int(p1[i]) >= 3:
                            lis.append(5)
                        else:
                            lis.append(4)
                    fig.add_trace(
                        go.Scatter(x=x_, y=lis, line_color="deepskyblue"),row=k, col=r+1)
                    

            # Adding traces for tie break Match
            
            final_df = (df[df['set_number'] == 13])
            max_x= (len(final_df['set_number']))
            x_ = np.arange(0, max_x,1)
            fig.add_trace(
                go.Scatter(x=x_,y=final_df['points_of_1'],line_color = "red"),row=k, col=13+1)
            fig.add_trace(
                go.Scatter(x=x_, y=final_df['points_of_2'],line_color ="green"),row=k, col=13+1)
            lis1=[]
            p2=final_df['points_of_2'].tolist()
            p1=final_df['points_of_1'].tolist()
            
            tie_break_xvalue.append(x_[-1])
            max_tie_break_score = int(p1[-1])
            if int(p2[-1])>max_tie_break_score:
                max_tie_break_score = int(p2[-1])
            tie_break_yvalue.append(max_tie_break_score)

            for i in range(0,len(p2)):
                if int(p1[i])<6 and int(p2[i])<6:
                    lis1.append(7)
                elif int(p1[i])>=6 and int(p2[i])>=6 and int(p1[i])==int(p2[i]):
                    lis1.append(int(p2[i])+2)
                else:
                    lis1.append(lis1[i-1])
            fig.add_trace(
                go.Scatter(x=x_, y=lis1, line_color="deepskyblue"),row=k, col=14)
            fig.add_annotation(dict(font = dict(color = 'white')),xref="x domain",yref="y domain",x=0.5, y=1.2, showarrow=False,
                        text="<b>TB</b>", row=k, col=14)
    
    # Setting y axis labels for all the graphs     
    set_yaxis=[]
    for i in yref_value:
        set_yaxis.append('yaxis'+i[1:])
    set_yaxis[0]='yaxis'

    for ax in fig['layout']:
        if ax[:5]=='yaxis':
            if ax not in set_yaxis:
                fig['layout'][ax]['tickmode'] = 'array'
                fig['layout'][ax]['tickvals'] = [0, 1, 2, 3, 4]
                fig['layout'][ax]['ticktext'] = ['0', '15', '30', '40', 'AD']

    # Setting y axis labels for tie break match
    for ax in tie_break_Yaxes:
        fig['layout']['yaxis'+ax[1:]]['tickmode'] = 'array'
        fig['layout']['yaxis'+ax[1:]]['tickvals'] = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        fig['layout']['yaxis'+ax[1:]]['ticktext'] = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15']
    
    #. Update height, width and title
    fig.update_layout(autosize=False,height=300*len(no_of_sets), width=270*max(columns_),title_text=title[0],title_font_color ="#FFFFFF", paper_bgcolor='rgb(0,0,0)',plot_bgcolor='#d1edd8')
    if len(no_of_sets) == 1 and max(columns_) < 5:
        fig.update_layout(autosize=False,height=500,width=1500)
    #. Update y axis labels to color white.
    fig.update_yaxes(color="#FFFFFF")
    #. Make labels disappear on x axis
    fig.update_xaxes(showticklabels=False)
    #. Remove legend
    fig.update_layout(showlegend=False)
    #. Make x axes disappear
    fig.update_xaxes(showgrid=False,zeroline=False)
    #. Make y axes disappear
    fig.update_yaxes(showgrid=False,zeroline=False)

    #. creating a shape of the same size of set graph and make it transparent white color with a border.
    b =[]
    for i in range(0,len(xref_value)):
        b1 = dict(
                                                    type="rect",
                                                    xref=xref_value[i],
                                                    yref=yref_value[i],
                                                    x0 = -1.5,y0= -1.2,y1=y1_value[i]+1.7,x1=x1_value[i]+2,
                                                    line=dict(color="blue",width=4),
                                                    fillcolor="lightgray",
                                                    opacity=1,
                                                    layer="below",
                                                )
        b.append(b1)
    
    
    #. creating a shape of the same size of Tie Break graph and make it transparent white color with a border.
    for i in range(0,len(tie_break_Xaxes)):
        b2 = dict(
                                                    type="rect",
                                                    xref=tie_break_Xaxes[i],
                                                    yref=tie_break_Yaxes[i],
                                                    x0 = -1.2,y0= -1.2,y1=tie_break_yvalue[i]+1.7,x1=tie_break_xvalue[i]+2,
                                                    line=dict(color="orange",width=4),
                                                    opacity=1,
                                                    layer="below",
                                                )
        b.append(b2)

    
    fig.update_layout(shapes=b)
    return fig

def split_it(point):
    x = point.split('-')
    import pandas as pd
    if len(x) == 2:
        if x[0] == ' A':
            x[0] = '45'
        elif x[1] == 'A':
            x[1] = '45'
    return x

def set_number_(lis,set_):
    global i,set_no
    import pandas as pd
    if set_no != set_:
        i = 0
        set_no = set_
    if lis == ['0','0']:
        i = i+1
    return i

def fill_nan_in_points(point, p1_score,p2_score):
    import pandas as pd
    #print(point, type(point))
    if pd.isnull(point) or len(point) > 6:
        #print(len(point))
        point = str(p1_score)+'-'+str(p2_score)
    return point