import streamlit as st
import pandas as pd
import numpy as np
import os
import warnings
import pandas.io.sql as psql
import psycopg2
import pathlib
warnings.filterwarnings('ignore')

#Page construction
def page_construct():
    st.set_page_config(page_title="IRRI GSL", layout='wide')
    valid = False
    if 'initializer' not in st.session_state:
        st.session_state.initializer = False #only for initialization


#For running DB querries
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


#Page View
def dataview_r(conn, filters):
    try:
    #Display code for Service Requests
        service = pd.read_sql_query("SELECT * FROM public.gsl_service_requests", conn)
        r_cont = st.container()
        r_cont.header('Service Requests')
        r_cont.write('Live table of GSL service requests from 2019 onward')
        df = pd.DataFrame(service)
        filter = np.full(len(df), True)
        for feature_name, val in filters.items():
            if feature_name in ['status','requestor_program','genotyping_platform']:
                if val not in ["", 0.0]:
                    filter = (
                        filter
                        & (df[feature_name] == val))
        r_cont.dataframe(df[filter])
        rcsv = df.to_csv().encode('utf-8')
        rcsv_head = df[filter].to_csv().encode('utf-8')
        r1,r2,r3,r4 = r_cont.columns(4)
        r1.download_button(label='Download ALL service requests', data=rcsv, file_name='GSL Service Requests.csv',mime='text/csv')
        r2.download_button(label='Download FILTERED service requests', data=rcsv_head, file_name='GSL Service Requests.csv',mime='text/csv')
        conn.close()
    except:
        st.write()

        
def dataview_s(conn,filters):
    try:
    #Display code for Samples
        query = "SELECT * FROM public.gsl_samples"
        samples = pd.read_sql_query(query, conn)
        s_cont = st.container()
        s_cont.header('Samples and Products')
        s_cont.write('Live table of GSL samples and product info used in service requests from 2019 onward.')
        s_cont.write('NOTE: The table only shows the first 1,000 rows. To view all, use the download buttons below.')
        df = pd.DataFrame(samples)
        filter = np.full(len(df), True)
        for feature_name, val in filters.items():
            if feature_name in ['designation','gid','source_study_name']:
                if val not in ["", 0.0]:
                    filter = (
                        filter
                        & (df[feature_name] == val))
        s_cont.dataframe(df[filter].head(1000))
        scsv = df.to_csv().encode('utf-8')
        scsv_head = df[filter].to_csv().encode('utf-8')
        s1,s2,s3,s4 = s_cont.columns(4)
        s1.download_button(label='Download ALL samples', data=scsv, file_name='GSL Samples/Product.csv',mime='text/csv')
        s2.download_button(label='Download FILTERED samples', data=scsv_head, file_name='GSL Samples/Product.csv',mime='text/csv')
        conn.close()
    except psycopg2.Error as e:
        st.write(e)



#Validation of credentials
def validate():
    try:
        conn = init_connection()
        return True
    except:
        return False


    
#Log in page
page_construct()
st.title('IRRI GSL - Custom B4R Database View');
with st.expander('Please Login Here', expanded= not st.session_state.initializer):
    with st.form('Login', True):
        username = st.text_input('Username')
        password = st.text_input('Password',type='password')
        submitted = st.form_submit_button(label='Login')
        if submitted:
            st.secrets['postgres']['user'] = username
            st.secrets['postgres']['password'] = password
            if validate():
                st.session_state.initializer = True
            else:
                st.session_state.initializer = 'Blank'
            
#Data page
if st.session_state.initializer == False:
    st.write()
elif st.session_state.initializer == 'Blank':
    st.header('Login credentials incorrect. You are not permitted to access this page.') 
elif st.session_state.initializer == True:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    filters = {
        'status': col1.text_input('Status',""),
        'requestor_program': col2.text_input('Program',""),
        'genotyping_platform': col3.text_input('Platform',""),
        'designation': col4.text_input('Designation',""),
        'gid': col5.number_input('GID',0),
        'source_study_name': col6.text_input('Study Name', "")
    } 
    conn = init_connection()
    dataview_r(conn, filters)
    conn = init_connection()
    dataview_s(conn,filters)
