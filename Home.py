import streamlit as st
import pandas as pd
import plotly_express as px
from dca_oop import ARPS
st.title("Decline Curve Analysis")
"""An app to make Decline curve analysis using ARP's models for conventional reservoirs.
- Upload your data 
- Specify is it field or only one well data 
- Choose the right parameters 
- The result will whow
"""
# ------------------------ side bar -------------------------
st.sidebar.markdown("## Data Input `Production data`")
file = st.sidebar.file_uploader("Upload Data file",type=["CSV"])
# check if the file is uploaded

if file:
    try:
        @st.cache
        def upload_file(file):
            df = pd.read_csv( file , parse_dates=True )
            return df
        df = upload_file(file)
        #check wheter the data if for one well or multiwell
        type = st.sidebar.selectbox("Type of data",["One_Well","Filed_Data"])
        if type == "Filed_Data":

            # if multiwells so choose the well
            col = st.sidebar.selectbox("Wells_name_column",list(df.columns),index=0)
            well = st.sidebar.selectbox("Which well?",list(df[col].unique()),index=1)
            Q_col = st.sidebar.selectbox("Production column",list(df.columns),index=2)
            date = st.sidebar.selectbox("Date column",list(df.columns))
            freq = st.sidebar.selectbox("data Frequency", ["Daily", "Monthly", "Yearly"])
            # the final df of the well
            df = df[df[col] == well]
            arps_model = ARPS(df,Q_col,date)
            # show data
            """sample of data"""
            st.write(df.head())
        # if the data was only one well
        if type == "One_Well":
            # if multiwells so choose the well
            Q_col = st.sidebar.selectbox("Production column",list(df.columns),index=0)
            date = st.sidebar.selectbox("Date column",list(df.columns),index=1)
            freq = st.sidebar.selectbox("data Frequency", ["Daily", "Monthly", "Yearly"])
            # the final df of the well
            df = df[[date,Q_col]]
            # show data
            """sample of data"""
            st.write(df.head())

        """## Smoothing the data using moving average"""
        window = st.slider("Window size",min_value=10,max_value=200,value= 100)
        std = st.slider("Removing outliers",min_value=1,max_value=10,value=3)
        df_smoothed = arps_model.smooth(window_size=window,stds=std,trim=True)
        Q_smoothed= Q_col+"_rol_Av"
        df2= df_smoothed[[date,Q_col,Q_smoothed]]
        fig = px.line(df2,x=date,y=[Q_col,Q_smoothed],width=900,height=600)
        st.plotly_chart(fig)

        # preprocess the data column
        arps_model.prepocess_date_col(frequency=freq)
        # show all line
        """## ARP's models fitted"""
        # fit all the model
        parameters , Qs = arps_model.fit_all_models()
        fig = px.line(Qs,x="Time",y=["Original_Smoothed","Exponential","Harmonic","Hyperbolic"],width=1000,height=600)
        st.plotly_chart(fig)
        """#### Models parameters"""
        st.table(parameters)
        st.success('Made with love'+'\u2764\ufe0f'+' Ahmed Elsayed')
    except:
        st.error("Make sure you choosed the right parameters")
