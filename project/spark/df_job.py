import pyspark
from pyspark.sql import SparkSession,SQLContext,DataFrame
from pyspark.sql.functions import lit
import configparser
from wordcloud import WordCloud


print(pyspark.__version__)

# create the Database propertiesdb_properties={}
db_properties={}
config = configparser.ConfigParser()
config.read("./database_config.ini")
db_prop = config['mariadb']
db_url = db_prop['url']
db_properties['user']=db_prop['username']
db_properties['password']=db_prop['password']
db_properties['driver']=db_prop['driver']


def create_wc_tfidf(file_name):
    file_tifidf = spark.sql('SELECT word,tfidf FROM tfidf WHERE name = "{}"'.format(file_name)).collect()
    word_list = {x.word:x.tfidf for x in file_tifidf}
    
    wordcloud = WordCloud(width = 1000, height = 500, mode = "RGBA", background_color=None, colormap="gray")
    wordcloud.generate_from_frequencies(word_list)
    wordcloud.to_file("./wordclouds/" + file_name + ".png")

# create spark seassion with workers
spark = SparkSession.builder\
                        .master("spark://spark:7077")\
                        .appName('DF_job')\
                        .getOrCreate()

sc = spark.sparkContext
sc.setLogLevel('ERROR')

# update document frequency 
termf_df = spark.read.jdbc(url=db_url,table='tf',properties=db_properties)
termf_df.createOrReplaceTempView("tf")

# calculate document frequency over all words in the tf table
docf_df = spark.sql("select word, count(word) as df from tf group by word")
docf_df.createOrReplaceTempView("df")

# global word count
termf_global = spark.sql("select word, sum(counts) as counts from tf group by word")
termf_global = termf_global.withColumn("name",lit("global"))
termf_all = termf_global.unionByName(termf_df)
termf_all.createOrReplaceTempView("tf_all")

# calculate tfIdf for each document per word
tfidf = spark.sql("select tf_all.name,tf_all.word, tf_all.counts / df.df as tfidf from tf_all join df on df.word = tf_all.word")
tfidf.createOrReplaceTempView("tfidf")

# select all document name and generate new word-clouds
names = tfidf.select("name").distinct().collect()
for name in names:
    create_wc_tfidf(name.name)

docf_df.write.option("encoding", "UTF-8").jdbc(url=db_url,table='df',mode='overwrite',properties=db_properties)
tfidf.write.option("encoding", "UTF-8").jdbc(url=db_url,table='tfidf',mode='overwrite',properties=db_properties)

sc.stop()
spark.stop()
