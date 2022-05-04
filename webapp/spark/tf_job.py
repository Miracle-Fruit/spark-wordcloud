from dataclasses import dataclass
import pyspark
from pyspark.sql import SparkSession,SQLContext,DataFrame
from pyspark.sql.functions import lit
import configparser
import sys,os
import re

from wordcloud import WordCloud

print(pyspark.__version__)

#Create the Database propertiesdb_properties={}
db_properties={}
config = configparser.ConfigParser()
config.read("database_config.ini")
db_prop = config['mariadb']
db_url = db_prop['url']
db_properties['user']=db_prop['username']
db_properties['password']=db_prop['password']
db_properties['driver']=db_prop['driver']

txt_file = str(sys.argv[1])
table_name = os.path.basename(txt_file).split('.')[0] # create table name here

# add specific configs here wit conf.set('key','value)
conf = pyspark.SparkConf()
# conf.set('spark.jars', '/opt/bitnami/spark/jars/')
conf.set('spark.driver.extraClassPath','/opt/bitnami/spark/jars/mysql-connector-java-8.0.29.jar')
# conf.set('spark.executor.memory','2g')
# conf.set('spark.executor.cores', '2')
# create spark sessaion with workers
spark = SparkSession.builder\
                        .master("spark://spark:7077")\
                        .appName('TF_job_'+table_name)\
                        .config(conf=conf)\
                        .getOrCreate()
sc = spark.sparkContext
sc.setLogLevel('ERROR')

# calculate tfIdf for upload
txt = sc.textFile(txt_file)
# calculate term_frequency
counts = txt.flatMap(lambda line: re.split("\W+", line.lower())) \
            .filter(lambda word: len(word)>3)\
            .map(lambda word: (word, 1)) \
            .reduceByKey(lambda a, b: a + b)

# create data_frame with cols: file_name, word, counts
tf_data = spark.createDataFrame(counts,["word","counts"])
tf_data = tf_data.withColumn("name",lit(str(table_name))).repartition("word").sortWithinPartitions("word")
tf_data.createOrReplaceTempView("tf_local")
tf_data.write.option("encoding", "UTF-8").jdbc(url=db_url,table='tf',mode='append',properties=db_properties)

# count current df for this document (distinct word = count 1)
word_df = spark.sql("SELECT word FROM tf_local").withColumn("df",lit(1)).repartition("word").sortWithinPartitions("word")

# update data_frequency table 
df = spark.read.jdbc(url=db_url,table='df',properties=db_properties).cache()
df_data = df.unionByName(word_df)
df_data.createOrReplaceTempView("df")
df_data = spark.sql("SELECT word, SUM(df) as df FROM df GROUP BY word")
df_data.write.option("truncate", "true").option("encoding", "UTF-8").jdbc(url=db_url,table='df',mode='overwrite',properties=db_properties)
spark.catalog.dropTempView("df") # have to drop else the replace doesn't work

# calculate tfIdf for the current document
df_data.createOrReplaceTempView("df")
tfidf = spark.sql("SELECT tf_local.name,tf_local.word, tf_local.counts / df.df as tfidf FROM tf_local JOIN df ON df.word = tf_local.word")
tfidf.createOrReplaceTempView("tfidf")

# genarate word_cloud
file_tifidf = spark.sql('SELECT word,tfidf FROM tfidf WHERE name = "{}"'.format(table_name)).collect()
word_list = {x.word:x.tfidf for x in file_tifidf}
wordcloud = WordCloud(width = 1000, height = 500, mode = "RGBA", background_color=None, colormap="gray")
wordcloud.generate_from_frequencies(word_list)
wordcloud.to_file("./wordclouds/" + table_name + ".png")

sc.stop()
spark.stop()
