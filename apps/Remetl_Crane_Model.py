
import pandas as pd
import numpy as np
import pyodbc
# import os
import time
from datetime import datetime
from misc import parameters as p
import logging
import schedule
from sqlalchemy import create_engine
import subprocess
import warnings
warnings.filterwarnings('ignore')

driver = 'ODBC+DRIVER+13+for+SQL+Server'
engine_stmt = ("mssql+pyodbc://%s:%s@%s/%s?driver=%s" % (p.Azure_username, p.Azure_password, p.Azure_server, p.Azure_database, driver))
engine = create_engine(engine_stmt)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

def get_df_mes(sql):
    try:
        conn = pyodbc.connect(p.conn_string)
        df_input = pd.read_sql(sql, conn)
        conn.close()
    except Exception as err:
        logging.info({"Error": str(err)})
    return df_input

def get_CAST_SPEED():
    df = pd.read_csv('./Data/SPEED.csv')
    return df
def get_CONFIG_TIME():
    data = {
        'EQUIP': ['DC1', 'DC2'],
        'COOLING_TIME': [6, 5],
        'INGOT_REMOVAL_TIME': [25, 15],
        'CASTING_PREPARATION_TIME': [55, 55],
        'HCR': [6, 6]
    }

    df = pd.DataFrame(data)
    return df

def INS_yej_REMELT_CAST_CRANE(data_df):
    logging.info('START_yej_REMELT_CAST_CRANE')
    try:
        conn = pyodbc.connect(p.Azure_conn_string)
        cursor = conn.cursor()

        sql = """
                IF EXISTS (SELECT * FROM [dbo].[yej_REMELT_CAST_CRANE] WHERE [PLANDTTM] = ? AND [CASTEQPTNM] = ? AND [BATCHNO] = ?)
                    DELETE FROM [dbo].[yej_REMELT_CAST_CRANE] WHERE [PLANDTTM] = ? AND [CASTEQPTNM] = ? AND [BATCHNO] = ?;
                INSERT INTO [dbo].[yej_REMELT_CAST_CRANE]([PLANDTTM],[CASTEQPTNM],[BATCHNO],[ALLOY],[GAUGE],[WIDTH],[LENGTH],[SPEED]
                ,[CASTING_START_TIME],[CASTING_END_TIME],[COOLING_TIME],[INGOT_REMOVAL_TIME],[CASTING_PREPARATION_TIME],[OVERLAP],[VIRTUAL],[OVERLAP_TIME]) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """
        for index, row in data_df.iterrows():
            cursor.execute(sql,row['PLANDTTM'],row['CASTEQPTNM'], row['BATCHNO'],row['PLANDTTM'],row['CASTEQPTNM'], row['BATCHNO'],row['PLANDTTM'], row['CASTEQPTNM'],row['BATCHNO']
                           ,row['ALLOY'],row['GAUGE'],row['WIDTH'],row['LENGTH'],row['SPEED']
                           ,row['CASTING_START_TIME'],row['CASTING_END_TIME'],row['COOLING_TIME'],row['INGOT_REMOVAL_TIME'],row['CASTING_PREPARATION_TIME'],row['OVERLAP'],row['VIRTUAL'],row['OVERLAP_TIME'])
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as err:
        logging.info({"Error": str(err)})
    logging.info('END_yej_REMELT_CAST_CRANE')

def QRY_yej_REMELT_CAST_SPEED():
    logging.info('START_QRY_yej_REMELT_CAST_SPEED')
    try:
        conn = pyodbc.connect(p.Azure_conn_string)
        cursor = conn.cursor()

        query = """
                SELECT * FROM [dbo].[yej_REMELT_CAST_SPEED] 
            """
        cursor.execute(query)
        df = pd.DataFrame(c.fetchall(), columns=["EQUIP","ALLOY","GAUGE","WIDTH","SPEED"])
    
        cursor.close()
        conn.close()
        return df
    except Exception as err:
        logging.info({"Error": str(err)})
        return None
    logging.info('END_QRY_yej_REMELT_CAST_SPEED')
def make_table(df):
    data = {
        'PLANDTTM': [],
        'CASTEQPTNM': [],
        'BATCHNO': [],
        'ALLOY': [],
        'GAUGE': [],
        'WIDTH': [],
        'LENGTH': [],
        'SPEED': [],
        'CASTING_START_TIME': [],
        'CASTING_END_TIME': [],
        'COOLING_TIME': [],
        'INGOT_REMOVAL_TIME': [],
        'CASTING_PREPARATION_TIME': [],
        'VIRTUAL': []
    }
    df2 = pd.DataFrame(data)
    num_rows_df1 = len(df)
    df2 = df2.iloc[:num_rows_df1]
    return df2


def extract_alloy_code(alloy):
    if len(alloy) < 5:
        return np.nan

    second_four_chars = alloy[1:5]
    second_char = alloy[1]

    if second_four_chars == '3104':
        return '3104'
    elif second_char == '6':
        return '6xxx'
    elif second_four_chars == '5182':
        return '5182'
    elif second_char == '5':
        return '5xxx'
    else:
        return np.nan


def Add_config(df,CASTEQPTID):
    df_speed = get_CAST_SPEED()
    # df_speed = QRY_yej_REMELT_CAST_SPEED()
    df_config_time = get_CONFIG_TIME()

    if CASTEQPTID == 'YJ1RTCS1':
        EQUIP = 'DC1'
    else:
        EQUIP = 'DC2'
    df_speed = df_speed.loc[df_speed.EQUIP==EQUIP]
    df_config_time = df_config_time.loc[df_config_time.EQUIP == EQUIP]
    df['ALLOY_R'] = df['ALLOY'].apply(extract_alloy_code)

    for index, row in df_speed.iterrows():
        matching_row = df[(df['WIDTH'] == row['WIDTH']) & (df['ALLOY_R'] == row['ALLOY']) & (df['GAUGE'] == row['GAUGE'])]
        if not matching_row.empty:
            df.loc[matching_row.index, 'SPEED'] = row['SPEED']
    df['exp_CASTING_TIME'] = (df['LENGTH'] / df['SPEED'])

    df['HCR'] = df_config_time['HCR'].values[0]
    df['CONFIG_COOLING_TIME'] = df_config_time['COOLING_TIME'].values[0]
    df['CONFIG_INGOT_REMOVAL_TIME'] = df_config_time['INGOT_REMOVAL_TIME'].values[0]
    df['CONFIG_CASTING_PREPARATION_TIME'] = df_config_time['CASTING_PREPARATION_TIME'].values[0]

    df['COOLING_TIME'] = df['CASTING_END_TIME'] + pd.to_timedelta(df['CONFIG_COOLING_TIME'],unit='m')
    df['INGOT_REMOVAL_TIME'] = df['CASTING_END_TIME'] + pd.to_timedelta(df['CONFIG_INGOT_REMOVAL_TIME'],unit='m')
    df['CASTING_PREPARATION_TIME'] = df['CASTING_END_TIME']+ pd.to_timedelta(df['CONFIG_CASTING_PREPARATION_TIME'], unit='m')

    return df
def get_crane_tbl(CASTEQPTID):

    df = get_df_mes(p.sql_REMELT_CRANE.format(CASTEQPTID))
    df = Add_config(df, CASTEQPTID)

    df_tbl = make_table(df)
    df_tbl['PLANDTTM'] = df['PLANDTTM']
    df_tbl['CASTEQPTNM'] = df['CASTEQPTNM']
    df_tbl['BATCHNO']=df['BATCHNO']
    df_tbl['ALLOY'] = df['ALLOY']
    df_tbl['GAUGE'] = df['GAUGE']
    df_tbl['WIDTH'] = df['WIDTH']
    df_tbl['LENGTH'] = df['LENGTH']
    df_tbl['SPEED'] = df['SPEED']

    for index, row in df.iterrows():
        if pd.isnull(row['CASTING_START_TIME']) or pd.isna(row['CASTING_START_TIME']):
            if index > 0:
                df_tbl.at[index, 'CASTING_START_TIME'] = df_tbl.at[index - 1, 'CASTING_PREPARATION_TIME']
            else:
                df_tbl.at[index, 'CASTING_START_TIME'] = datetime.now().replace(hour=6, minute=30, second=0, microsecond=0)
            df_tbl.at[index, 'CASTING_END_TIME'] = (df_tbl.at[index, 'CASTING_START_TIME']
                                                    + pd.to_timedelta(df.at[index, 'exp_CASTING_TIME'], unit='m')
                                                    + pd.to_timedelta(df.at[index, 'HCR'], unit='m'))
            df_tbl.at[index, 'COOLING_TIME'] = (df_tbl.at[index, 'CASTING_END_TIME']
                                                + pd.to_timedelta(df.at[index, 'CONFIG_COOLING_TIME'], unit='m'))
            df_tbl.at[index, 'INGOT_REMOVAL_TIME'] = (df_tbl.at[index, 'CASTING_END_TIME']
                                                      + pd.to_timedelta(df.at[index, 'CONFIG_INGOT_REMOVAL_TIME'],unit='m'))
            df_tbl.at[index, 'CASTING_PREPARATION_TIME'] = (df_tbl.at[index, 'CASTING_END_TIME']
                                                            + pd.to_timedelta(
                        df.at[index, 'CONFIG_CASTING_PREPARATION_TIME'], unit='m'))
            df_tbl.at[index, 'VIRTUAL'] = 1
        else:
            df_tbl.at[index, 'CASTING_START_TIME'] = row['CASTING_START_TIME']
            df_tbl.at[index, 'CASTING_END_TIME'] = row['CASTING_END_TIME']
            df_tbl.at[index, 'COOLING_TIME'] = row['COOLING_TIME']
            df_tbl.at[index, 'INGOT_REMOVAL_TIME'] = row['INGOT_REMOVAL_TIME']
            df_tbl.at[index, 'CASTING_PREPARATION_TIME'] = row['CASTING_PREPARATION_TIME']
            df_tbl.at[index, 'VIRTUAL'] = 0
    df_tbl['CASTING_START_TIME'] = pd.to_datetime(df_tbl['CASTING_START_TIME']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_tbl['CASTING_END_TIME'] = pd.to_datetime(df_tbl['CASTING_END_TIME']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_tbl['COOLING_TIME'] = pd.to_datetime(df_tbl['COOLING_TIME']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_tbl['INGOT_REMOVAL_TIME'] = pd.to_datetime(df_tbl['INGOT_REMOVAL_TIME']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_tbl['CASTING_PREPARATION_TIME'] = pd.to_datetime(df_tbl['CASTING_PREPARATION_TIME']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_tbl['COOLING_TIME'] = pd.to_datetime(df_tbl['COOLING_TIME'])
    df_tbl['INGOT_REMOVAL_TIME'] = pd.to_datetime(df_tbl['INGOT_REMOVAL_TIME'])

    return df_tbl

def check_overlap(df1, df2):
    import datetime
    # Function to check if two intervals overlap
    def check_overlap(start1, end1, start2, end2):
        return start1 <= end2 and start2 <= end1

    # Create an empty list to store the overlap time results
    overlap_time = []
    overlap_results = []

    # Iterate over each row in df1
    for index, row1 in df1.iterrows():
        start1 = row1['COOLING_TIME']
        end1 = row1['INGOT_REMOVAL_TIME']
        overlap_found = False
        overlap_duration = 0

        # Iterate over each row in df2
        for index, row2 in df2.iterrows():
            start2 = row2['COOLING_TIME']
            end2 = row2['INGOT_REMOVAL_TIME']

            # Check if the intervals overlap
            if check_overlap(start1, end1, start2, end2):
                overlap_found = True
                overlap_duration = min(end1, end2) - max(start1, start2)
                # %M:%S 형식으로 포맷팅
                overlap_duration = str(overlap_duration.seconds // 60) + ":" + str(overlap_duration.seconds % 60).zfill(2)

                break

        # Append the overlap duration to the list
        overlap_time.append(overlap_duration)
        overlap_results.append(1 if overlap_found else 0)

    # Add the overlap duration results to df1 as a new column
    df1['OVERLAP_TIME'] = overlap_time
    df1['OVERLAP'] = overlap_results
    return df1

def main():
    logging.info('###################### Start !! ################')
    try:
        df1 = get_crane_tbl('YJ1RTCS1')
        df2 = get_crane_tbl('YJ1RTCS2')
        #DC1 와 DC2에서 COOLING_TIME ~ INGOT_REMOVAL_TIME 구간이 겹치는 지 여부 확인
        df_dc1 = check_overlap(df1, df2)
        INS_yej_REMELT_CAST_CRANE(df_dc1)
        df_dc2 = check_overlap(df2,df1)
        INS_yej_REMELT_CAST_CRANE(df_dc2)

    finally:
        pass

if __name__ == '__main__':
    main()

    # logging.info('Scheduling..')
    # schedule.every(1).hours.do(main)
    # while True:        
    #     schedule.run_pending()
    #     time.sleep(1)