#!/usr/bin/python3.7

import datetime as dt
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import psycopg2 as db
from elasticsearch import Elasticsearch

default_args={
        'owner':'eun',
        'start_date':dt.datetime(2024,3,11),
        'retries':1,
        'retry_delay':dt.timedelta(minutes=5),
}

def queryPostgresql():
    conn_string="dbname='dataengineering' host='localhost' user='postgres' password='0000'"
    conn=db.connect(conn_string)
    df=pd.read_sql("select name,city from users",conn)
    df.to_csv('postgresqldata.csv')
    print("---------Data Saved---------")

def insertElasticsearch():
    es=Elasticsearch()
    df=pd.read_csv('postgresqldata.csv')
    for i,r in df.iterrows():
        doc=r.to_json()
        res=es.index(index="frompostgresql", doc_type="doc",body=doc)
        print(res)

with DAG('MyDBdag',
        default_args=default_args,
        schedule_interval=timedelta(minutes=5),
        )as dag:
    getData=PythonOperator(task_id='QueryPostgreSQL',
            python_callable=queryPostgresql)

    insertData=PythonOperator(task_id='InsertDataElasticsearch',
            python_callable=insertElasticsearch)

getData >> insertData


