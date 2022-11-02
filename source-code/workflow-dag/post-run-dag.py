# Copyright 2019 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Data processing test workflow definition.
"""
from asyncio import Task
import datetime
from airflow import models
from airflow.contrib.operators.dataflow_operator import DataFlowJavaOperator
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator
from airflow.providers.google.cloud.operators.pubsub import PubSubPublishMessageOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator



dataflow_jar_file_test = models.Variable.get('dataflow_jar_file_test')

dataflow_staging_bucket = 'gs://%s/staging' % (
    models.Variable.get('dataflow_staging_bucket_test'))

dataflow_jar_location = 'gs://%s/%s' % (
    models.Variable.get('dataflow_jar_location_test'),
    dataflow_jar_file_test)

project = models.Variable.get('gcp_project')
region = models.Variable.get('gcp_region')
zone = models.Variable.get('gcp_zone')
input_bucket = 'gs://' + models.Variable.get('gcs_input_bucket_test')
output_bucket_name = models.Variable.get('gcs_output_bucket_test')

yesterday = datetime.datetime.combine(
    datetime.datetime.today() - datetime.timedelta(1),
    datetime.datetime.min.time())

default_args = {
    'dataflow_default_options': {
        'project': project,
        'zone': zone,
        'region': region,
        'stagingLocation': dataflow_staging_bucket
    }
}

with models.DAG(
    'test_word_count',
    schedule_interval=None,
    default_args=default_args) as dag:
  run_this_first = EmptyOperator(
    task_id='run_this_first',
)
  

check_enviroment = BranchPythonOperator(
    task_id='check_enviroment',
    python_callable=lambda: publish_task,
)

publish_task = PubSubPublishMessageOperator(
    task_id='publish_test_complete',
    project=project,
    topic= {{ dag_run.conf['pubsub_topic'] }},
    messages=[{'data': dataflow_jar_file_test.encode('utf-8')}],
    start_date=yesterday
)

#CP gs://{{Composer_Bucket}}/logs/{{Dag_Name}}/echo/{{Run-ID}} gs://{{NonLive Destination Bucket}}

copy_logs_to_nonlive = GCSToGCSOperator(
    task_id="copy_logs_to_nonlive",
    source_bucket={{Composer_Bucket}},
    source_object="/logs/{{Dag_Name}}/echo/{{Run-ID}}",
    destination_bucket={{NonLive Destination Bucket}},
    destination_object="livelogs/",
)






run_this_first >> check_enviroment >> [publish_task, copy_logs_to_nonlive]




### Output Validation 
