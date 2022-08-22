import streamlit as st
import pandas as pd
import plotly_express as px
from dca import remove_outlier ,hyperbolic_fit,exponential_fit,harmonic_fit,hyperbolic,exposential,harmonic,PREPROCESS_DATA
st.title("Decline Curve Analysis")
"""An app to make Decline curve analysis using ARP's models for conventional reservoirs.
- Upload your data 
- Specify is it field or only one well data 
- Choose the right parameters 
- The result will whow
"""
# ------------------------ side bar -------------------------
st.sidebar.markdown("## Data Input")
file = st.sidebar.file_uploader("Upload Data file",type=["CSV"])
# check if the file is uploaded
if file:
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
        df = df[df[col] == well][[date,Q_col]]
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
    std = st.slider("Removing outliers",min_value=1,max_value=100,value=50)
    df2= remove_outlier(df,Q_col,window,std,trim=True)
    Q_smoothed= Q_col+"_rol_Av"
    df2= df2[[date,Q_col,Q_smoothed]]
    fig = px.line(df,x=date,y=[Q_col,Q_smoothed],width=900,height=600)
    st.plotly_chart(fig)
    # preprocess the data for the curve fitting
    T,Q = PREPROCESS_DATA(df2,date,Q_col,freq)
    # fit the model
    hyberbolic_parameters = hyperbolic_fit(T, Q)
    # fit the harmonic model
    harmonic_parameters = harmonic_fit(T, Q)
    # fit the exponential moel
    exp_parameters = exponential_fit(T, Q)
    all_params = [hyberbolic_parameters, harmonic_parameters, exp_parameters]
    data_info = {
        "Model": [i[-1] for i in all_params],
        "Qi": [i[0] for i in all_params],
        "Di": [i[1] for i in all_params],
        "b": [i[2] for i in all_params],
        "Normalized RMSE": [i[3] for i in all_params],
    }
    df_info = pd.DataFrame(data_info, columns=list(data_info.keys()))
    # show all line
    """## ARP's models fitted"""
    # tfit = np.linspace(min(T), m  ax(T), 100)
    Q_hyberbolic = hyperbolic(T, *hyberbolic_parameters[0:3])
    Q_harmonic = harmonic( T, *harmonic_parameters[0:2])
    Q_exponential = harmonic(T, *exp_parameters[0:2])
    fitted = pd.DataFrame({
        "Time":T,
        "OriginalSmoothed":Q,
        "Hyberpolic":Q_hyberbolic,
        "Harmonic": Q_harmonic,
        "Exponential": Q_exponential
                           })
    fig = px.line(fitted,x="Time",y=["OriginalSmoothed","Hyberpolic","Harmonic","Exponential"],width=1000,height=600)
    st.plotly_chart(fig)
    """#### Models parameters"""
    st.table(df_info)

    st.success('Made with love'+'\u2764\ufe0f'+' Ahmed Elsayed')
