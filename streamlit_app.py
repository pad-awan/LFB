# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 14:09:01 2021

@author: arnau


Nom du projet : LFB streamlit

Date de la dernière révision :

Auteur(s) : arnaud HUBERT

Révision N° : Version 1

Client : Streamlit

Fichiers du projet :
					-	streamlit_app.py



"""


################################################
#				Programme principal
################################################

# -----------------------------------------------
#		    Zone des 'imports' de modules
# -----------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
# from math import cos, sin, acos, pi
from sklearn.linear_model import LinearRegression,SGDRegressor

from sklearn.ensemble import GradientBoostingRegressor,RandomForestRegressor
import base64
# import time



#----------------------------------------------------
#		Zone de déclaration des variables globales
#----------------------------------------------------

LOGO_IMAGE = "fire.png"
st.set_page_config(page_title='London Fire Brigade - Rescue Times', 
                   page_icon=LOGO_IMAGE, 
                   layout='wide', 
                   initial_sidebar_state='auto')
pic = st.markdown(
    """
    <style>
    .container {
        display: flex;
    }
    .logo-text {

        font-size:25px !important;
        padding-top: 40px !important;
        padding-left: 30px !important;

    }
    .logo-img {
        float:right;
    }
    </style>
    """,
    unsafe_allow_html=True
)


welc =st.markdown(
    f"""
    <div class="container">
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
        <p class="logo-text"><font color=#6e6e6e><b>Welcome</b></font> to the Arrival Time Estimator<br>dedicated to the London Fire Brigade.
        <br>
        <br>
            This tool will help you to predict<br>the estimated time of arrival of the LFB,
        <br>
            based on the factors chosen.
        <br>
        <br>
            <b>Please select your settings</b>
        <br><br><br><br>
            <a href="https://smallpdf.com/shared#st=97bb4f3d-f30a-4c2f-9aaf-037ecc233065&fn=README.pdf&ct=1617856336952&tl=share-document&rf=link/" target="_blank">
                <font size=2.9>
                    <i>
                        <b>For more details about this project, check our analysis report here</b>
                    </i>
                </font>
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


classifier_name = st.sidebar.selectbox("Select model :", 
                                       ("LinearRegression","GradientBoostingRegressor","SGDRegressor","RandomForestRegressor"))

#####data cleaning

# Borough Firehouses load
df_cas_quart = pd.read_csv('df_cas_quart_2019.csv', index_col=0)
# BoroughName sort
df_cas_quart = df_cas_quart.sort_values('ProperCase', ascending = True)



# Ward + incident group + weekday - load
df_sqigwd = pd.read_csv('df_sqigwd_2019.csv', index_col=0)

# Borough + SpecialServiceType + hourofcall - load
df_quart = pd.read_csv('df_quartiers_2019.csv', index_col=0)

# Ward + DelayCodeId  - load
df_sqid = pd.read_csv('df_sqid_2019.csv', index_col=0)


# Borouh names and Ward names load
df_qsq = pd.read_csv('df_qsq_2019.csv', index_col=0)
# Borough Names and Ward names sort
df_qsq = df_qsq.sort_values(['ProperCase','IncGeo_WardName'], ascending = True)

# Incident group load
df_ig = pd.read_csv('df_ig_2019.csv', index_col=0)


# DelayCodeId and description - load
df_codeid = pd.read_csv('df_codeid_2019.csv', index_col=0)



# SpecialServiceType and description - load
df_sst = pd.read_csv('df_sst_2019.csv', index_col=0)
# Sidebar SpecialServiceType description list -  load
liste_sst = []
for sst in df_sst.SpecialServiceType.unique():
    liste_sst.append(sst)



# Sidebar DelayCodeId description list -  load
liste_delaycodeid = []
for description in df_codeid.DelayCode_Description.unique():
    liste_delaycodeid.append(description)


# Sidebar Borough name list -  load
liste_qu = []
for quartier in df_cas_quart.ProperCase.unique():
    liste_qu.append(quartier)


#-------------------------------------------------------
#		Zone de déclaration des modules ou des fonctions
#-------------------------------------------------------





# num_data_2020 preprocessed load

def upload_data2020():
    num_data = pd.read_csv('num_data_2020.csv', index_col=0)
    # num_data2 = num_data.copy()
    return num_data
num_data = upload_data2020()


# Sidebar Settings retrieving function
def user_input():
    hourofcall = st.sidebar.slider('Hour of Call', 0, 23, 12)
    weekday = st.sidebar.select_slider('Weekday', 
                                       options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    incidentgroup = st.sidebar.radio('Incident Group', ('Fire', 'False Alarm', 'Special Service'))
    sst_sel= st.sidebar.selectbox('Special Service Type', liste_sst)
    codeid_description= st.sidebar.selectbox('DelayCode Description', liste_delaycodeid)
    quartier= st.sidebar.selectbox('Borough Name', liste_qu)
    if incidentgroup == 'Fire' or incidentgroup == 'False Alarm':
        sst_sel = 'None'   # When Fire or False Alarm then SpecialServiceType value is None
    # User choices dictionnary definition
    data = {'hourofcall': hourofcall,
    'weekday': weekday,
    'incidentgroup': incidentgroup,
    'specialservicetype': sst_sel,
    'codeid_description': codeid_description,
    'quartier': quartier
    }
    # User choices in a DataFrame
    parametres = pd.DataFrame(data, index=[0])
    # User choices DataFrame return
    return parametres

# user_input call to retrieve User choices DataFrame
df = user_input()










# GPS borough points load

def upload_gps():
    gps = pd.read_csv('gpsfinal.csv', index_col=0, sep=";")
    return gps
gps = upload_gps()












# Sidebar WardName list -  load
liste_sq = []
for sousquartier in df_qsq[df_qsq.ProperCase == df.quartier[0]].IncGeo_WardName.unique():
    liste_sq.append(sousquartier)
# Sidebar WardName list initialization
sous_quartier= st.sidebar.selectbox('Ward Name', liste_sq)

#st.write(liste_sq)
num_quartier = df_cas_quart[df_cas_quart.ProperCase == df.quartier[0]].ProperCase_num
for nq in num_quartier:
    val_quartier = nq

num_sst = df_sst[df_sst.SpecialServiceType == df.specialservicetype[0]].SpecialServiceType_num
for sst in num_sst:
    val_sst = sst

num_ig = df_ig[df_ig.IncidentGroup == df.incidentgroup[0]].IncidentGroup_num
for ig in num_ig:
    val_ig = ig

num_codeid = df_codeid[df_codeid.DelayCode_Description == df.codeid_description[0]].DelayCodeId
for cid in num_codeid:
    val_codeid = cid


num_sous_quartier = df_qsq[(df_qsq.ProperCase == df.quartier[0])&(df_qsq.IncGeo_WardName == sous_quartier)].IncGeo_WardName_num
for nsq in num_sous_quartier:
    val_sous_quartier = nsq




# parameters by user
# def add_parameter_ui(clf_name):
#     params =dict()
#     if clf_name =="LinearRegression":
#         n_jobs = st.sidebar.slider("n_jobs",10,500)
#         params["n_jobs"] = n_jobs
#     elif clf_name == "RandomForestRegressor":
#         n_estimators = st.sidebar.slider("n_estimators",10,5000)
#         # criterion = st.sidebar.slider("criterion:",["mse", "mae"])
#         params["n_estimators"] = n_estimators
#         # params["criterion"] = criterion
#     else:
#         loss = st.sidebar.selectbox('loss:',["lad", "huber", "quantile"])
#         n_estimators = st.sidebar.slider("n_estimators",100,1000)
#         # alpha=st.sidebar.slider("alpha",1,10)
#         max_depth = st.sidebar.slider("max_depth",1,5)
#         # params["alpha"] = alpha
#         params["loss"] = loss
#         params["n_estimators"] = n_estimators
#         params["max_depth"] = max_depth
#         # params["learning_rate"] = learning_rate
#     return params

# params = add_parameter_ui(classifier_name)


def get_classifier(clf_name):
    if clf_name=="LinearRegression":
        clf = LinearRegression(n_jobs=15,normalize=True)
    elif clf_name =="GradientBoostingRegressor":
        clf = SGDRegressor()
    elif clf_name =="SGDRegressor":
        clf = GradientBoostingRegressor(n_estimators=15)
    elif clf_name =="RandomForestRegressor":
        clf = RandomForestRegressor(n_estimators=15,criterion="mse")
    return clf







# On peut déclarer et écrire les fonctions (ou modules) avant, pendant ou après le programme principal.

#-------------------------------------------------------
#						PROGRAMME
#-------------------------------------------------------





# st.title('London Fire Brigade - Rescue Times')
st.text("")
st.text("")


st.sidebar.image("LFBlogo.png")
st.sidebar.header('Settings')


clf = get_classifier(classifier_name)

num_heure = df.hourofcall[0]

# replace weekday numbers by weekday
num_wd = df.weekday[0]
num_wd = num_wd.replace('Monday','0')
num_wd = num_wd.replace('Tuesday','1')
num_wd = num_wd.replace('Wednesday','2')
num_wd = num_wd.replace('Thursday','3')
num_wd = num_wd.replace('Friday','4')
num_wd = num_wd.replace('Saturday','5')
num_wd = num_wd.replace('Sunday','6')

num_wd = int(num_wd)

# Arrival time prediction Button
submit = st.sidebar.button('>>Arrival time prediction<<')
if submit:
    data_pred = {'HourOfCall': num_heure,
        'DelayCodeId': val_codeid,
        'ProperCase_num': val_quartier,
        'casernes_quartier': 0,
        'tmoyq': 0.0,
        'tmedq': 0.0,
        'CalWeekDay': num_wd,
        'IncGeo_WardName_num': val_sous_quartier,
        'casernes_sous_quartier': 0,
        'tmoysqigwd': 0.0,
        'tmedsqigwd': 0.0,
        'tstdsqigwd': 0.0,
        'tminsqigwd': 0.0,
        'tmaxsqigwd': 0.0,
        'tmoyqussho': 0.0,
        'tmedqussho': 0.0,
        'tstdqussho': 0.0,
        'tminqussho': 0.0,
        'tmaxqussho': 0.0,
        'IncidentGroup_num': val_ig,
        'SpecialServiceType_num': val_sst,
        'tmoyCodeId': 0.0,
        'tmedCodeId': 0.0,
        'tstdCodeId': 0.0,
        'tminCodeId': 0.0,
        'tmaxCodeId': 0.0,
        'FirstPumpArriving_AttendanceTime' : 302
        }
    # into DataFrame
    num_data_pred = pd.DataFrame(data_pred, index=[0])
    # Statistics retrieval
    num_data_pred['casernes_quartier'] = df_cas_quart[df_cas_quart.ProperCase_num == val_quartier][['casernes_quartier']].values
    num_data_pred['tmoyq'] = df_cas_quart[df_cas_quart.ProperCase_num == val_quartier][['tmoyq']].values
    num_data_pred['tmedq'] = df_cas_quart[df_cas_quart.ProperCase_num == val_quartier][['tmedq']].values
    #  2019 Statistics retrieval when exists for this Wardname / incidentgroup / weekday
    if df_sqigwd[(df_sqigwd.IncGeo_WardName_num == val_sous_quartier)&(df_sqigwd.IncidentGroup == df.incidentgroup[0])&(df_sqigwd.CalWeekDay == num_wd)].shape[0] == 1:
        num_data_pred['casernes_sous_quartier'] = df_sqigwd[(df_sqigwd.IncGeo_WardName_num == val_sous_quartier)
                                                            &(df_sqigwd.IncidentGroup == df.incidentgroup[0])
                                                            &(df_sqigwd.CalWeekDay == num_wd)][['casernes_sous_quartier']].values
        num_data_pred['tmoysqigwd'] = df_sqigwd[(df_sqigwd.IncGeo_WardName_num == val_sous_quartier)
                                                &(df_sqigwd.IncidentGroup == df.incidentgroup[0])
                                                &(df_sqigwd.CalWeekDay == num_wd)][['tmoysqigwd']].values
        num_data_pred['tmedsqigwd'] = df_sqigwd[(df_sqigwd.IncGeo_WardName_num == val_sous_quartier)
                                                &(df_sqigwd.IncidentGroup == df.incidentgroup[0])
                                                &(df_sqigwd.CalWeekDay == num_wd)][['tmedsqigwd']].values
        num_data_pred['tstdsqigwd'] = df_sqigwd[(df_sqigwd.IncGeo_WardName_num == val_sous_quartier)
                                                &(df_sqigwd.IncidentGroup == df.incidentgroup[0])
                                                &(df_sqigwd.CalWeekDay == num_wd)][['tstdsqigwd']].values
        num_data_pred['tminsqigwd'] = df_sqigwd[(df_sqigwd.IncGeo_WardName_num == val_sous_quartier)
                                                &(df_sqigwd.IncidentGroup == df.incidentgroup[0])
                                                &(df_sqigwd.CalWeekDay == num_wd)][['tminsqigwd']].values
        num_data_pred['tmaxsqigwd'] = df_sqigwd[(df_sqigwd.IncGeo_WardName_num == val_sous_quartier)
                                                &(df_sqigwd.IncidentGroup == df.incidentgroup[0])
                                                &(df_sqigwd.CalWeekDay == num_wd)][['tmaxsqigwd']].values
    # 2019 Statistics retrieval when exists for this  Boroughname / SpecialServiceType / HourOfCall
    if df_quart[(df_quart.ProperCase == df.quartier[0])&(df_quart.SpecialServiceType == df.specialservicetype[0])&(df_quart.HourOfCall == num_heure)].shape[0] == 1:
        num_data_pred['tmoyqussho'] = df_quart[(df_quart.ProperCase == df.quartier[0])
                                            &(df_quart.SpecialServiceType == df.specialservicetype[0])
                                            &(df_quart.HourOfCall == num_heure)][['tmoyqussho']].values
        num_data_pred['tmedqussho'] = df_quart[(df_quart.ProperCase == df.quartier[0])
                                            &(df_quart.SpecialServiceType == df.specialservicetype[0])
                                            &(df_quart.HourOfCall == num_heure)][['tmedqussho']].values
        num_data_pred['tstdqussho'] = df_quart[(df_quart.ProperCase == df.quartier[0])
                                            &(df_quart.SpecialServiceType == df.specialservicetype[0])
                                            &(df_quart.HourOfCall == num_heure)][['tstdqussho']].values
        num_data_pred['tminqussho'] = df_quart[(df_quart.ProperCase == df.quartier[0])
                                            &(df_quart.SpecialServiceType == df.specialservicetype[0])
                                            &(df_quart.HourOfCall == num_heure)][['tminqussho']].values
        num_data_pred['tmaxqussho'] = df_quart[(df_quart.ProperCase == df.quartier[0])
                                            &(df_quart.SpecialServiceType == df.specialservicetype[0])
                                            &(df_quart.HourOfCall == num_heure)][['tmaxqussho']].values
    # 2019 Statistics retrieval when exists for this Wardname / DelayCodeId
    if df_sqid[(df_sqid.IncGeo_WardName == sous_quartier)
            &(df_sqid.DelayCodeId == val_codeid)].shape[0] == 1:
        num_data_pred['tmoyCodeId'] = df_sqid[(df_sqid.IncGeo_WardName == sous_quartier)
                                            &(df_sqid.DelayCodeId == val_codeid)][['tmoyCodeId']].values
        num_data_pred['tmedCodeId'] = df_sqid[(df_sqid.IncGeo_WardName == sous_quartier)
                                            &(df_sqid.DelayCodeId == val_codeid)][['tmedCodeId']].values
        num_data_pred['tstdCodeId'] = df_sqid[(df_sqid.IncGeo_WardName == sous_quartier)
                                            &(df_sqid.DelayCodeId == val_codeid)][['tstdCodeId']].values
        num_data_pred['tminCodeId'] = df_sqid[(df_sqid.IncGeo_WardName == sous_quartier)
                                            &(df_sqid.DelayCodeId == val_codeid)][['tminCodeId']].values
        num_data_pred['tmaxCodeId'] = df_sqid[(df_sqid.IncGeo_WardName == sous_quartier)
                                            &(df_sqid.DelayCodeId == val_codeid)][['tmaxCodeId']].values
    # features line display
    #st.write(num_data_pred)
    # num_data 2020 and features dataframe Normalization
    # from sklearn import preprocessing
    # from sklearn.model_selection import train_test_split
    # from sklearn.model_selection import cross_val_score
    # from sklearn.metrics import mean_squared_error
    
    scaler = preprocessing.StandardScaler().fit(num_data)
    num_data[num_data.columns] = pd.DataFrame(scaler.transform(num_data), 
                                            columns=num_data.columns, 
                                            index= num_data.index)
    num_data_pred[num_data_pred.columns] = pd.DataFrame(scaler.transform(num_data_pred),
                                                        columns=num_data_pred.columns, 
                                                        index= num_data_pred.index)
        
    ###Classification
    dfw = num_data
    target = dfw.FirstPumpArriving_AttendanceTime
    feats = dfw.drop(['FirstPumpArriving_AttendanceTime'], axis=1)
    # 2020 samples
    
    # split datas
    X_train, X_test, y_train, y_test = train_test_split(feats, target, test_size=0.2,random_state=1234)
    clf.fit(X_train, y_train)
    
    y_pred = clf.score(X_test,y_test)
    
    # display the classifier
    st.write(f"regressor ={classifier_name}")
    
    # display score of the regression model
    st.write(f"score = {y_pred}")
    
    # delete target column from num_data_pred into feats_demo
    feats_demo = num_data_pred.drop(['FirstPumpArriving_AttendanceTime'], axis=1)
    # prediction with trained model
    pred_test = clf.predict(feats_demo)
    
    
    # def results():
    # feats_demo,gps
    # reconstruction of the results 
    num_X1 = feats_demo[['HourOfCall']]
    num_X2 = feats_demo[['DelayCodeId', 'ProperCase_num',
        'casernes_quartier', 'tmoyq', 'tmedq', 'CalWeekDay',
        'IncGeo_WardName_num', 'casernes_sous_quartier', 'tmoysqigwd',
        'tmedsqigwd', 'tstdsqigwd', 'tminsqigwd', 'tmaxsqigwd', 'tmoyqussho',
        'tmedqussho', 'tstdqussho', 'tminqussho', 'tmaxqussho',
        'IncidentGroup_num', 'SpecialServiceType_num', 'tmoyCodeId',
        'tmedCodeId', 'tstdCodeId', 'tminCodeId', 'tmaxCodeId']]
    num_X1 = num_X1.join(num_X2)
    # predict target column addition
    num_X_pred = num_X1.assign(FirstPumpArriving_AttendTime_pred=pd.DataFrame(pred_test, columns=['FirstPumpArriving_AttendTime_pred']).values)
    # Denormalization to get the arrival estimated time in seconds
    num_X_pred_inverse = pd.DataFrame(scaler.inverse_transform(num_X_pred), columns=num_X_pred.columns, index= num_X_pred.index)
    # display denormalized DataFrame
    #st.write(num_X_pred_inverse)
    
    # estimated time rounded in integer
    tps_estimated = int(np.round(num_X_pred_inverse.FirstPumpArriving_AttendTime_pred[0], 0))
    # Minutes seconds transformation
    tps_minutes = tps_estimated // 60
    tps_seconds = tps_estimated % 60
    # preparing result message
    #success_message = 'Estimated LFB arrival time : ' + str(tps_estimated) + ' seconds.'
    success_message = 'Estimated LFB arrival time : ' + str(tps_minutes) + ' minutes ' + str(tps_seconds) + ' seconds.'
    
    
    # Estimated LFB arrival time display
    st.success(success_message)
        
    #Loading of the data to create the map
    datagps=(df.quartier)
    mapgps=gps.merge(right=datagps, on = "quartier", how = "right")
    mapgps['temps']=tps_estimated
    mapgps['min']=tps_minutes
    mapgps['sec']=tps_seconds
    
    
    # results()
    
    def display_map():
        global min,sec,quartier,mapgps
        
        #Display of the map
        tooltip = {
            "html": "The estimated arrival time is <b>{min}</b> min <b>{sec}</b> sec<br> for <b>{quartier}</b> area,<br> depending the information entered.",
            "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
        }
        
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/cedric60128/ckn0g3q6u13pz17pbnp9vmn6n',
            tooltip = tooltip,
            initial_view_state=pdk.ViewState(
            latitude=51.450,
            longitude=-0.070,
            zoom=8.80,
            pitch=50,
            bearing=-10
        ),
            layers=[
                pdk.Layer(
                    'ColumnLayer',
                    data=mapgps,
                    get_position='[lon, lat]',
                    get_elevation='[temps]',
                    radius=500,
                    auto_highlight=True,
                    elevation_scale=50,
                    elevation_range=[0, 100],
                    get_fill_color=["temps * -100", "temps", "temps * 10", 300],
                    pickable=True,
                    extruded=True
                )
            ]
        ))
    #map_active = st.button("Afficher la carte")
    # if map_active :
    display_map()
