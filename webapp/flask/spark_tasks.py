import sys 
import subprocess

# run job in spark container -> note working directory is the in ./flask (where the spark-submit is called)
def upload(file_path):
    base_path = "/opt/application/spark/"
    spark_submit_str = "spark-submit --packages mysql:mysql-connector-java:8.0.29 --master spark://spark:7077 {}tf_job.py {}".format(base_path,file_path)
    process=subprocess.Popen(spark_submit_str,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    stdout,stderr = process.communicate()
    if process.returncode !=0:
        print(stderr,file=sys.stderr)
    print(stdout,file=sys.stdout)


def batch():
    base_path = "/opt/application/spark/"
    spark_submit_str = "spark-submit --packages mysql:mysql-connector-java:8.0.29 --master spark://spark:7077 {}df_job.py".format(base_path)
    process=subprocess.Popen(spark_submit_str,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    stdout,stderr = process.communicate()
    if process.returncode !=0:
        print(stderr,file=sys.stderr)
    print(stdout,file=sys.stdout)