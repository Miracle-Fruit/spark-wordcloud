# Spark Wordcloud

Generate word clouds from large text files and determine term and document frequency across several documents.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Miracle-Fruit/spark-wordcloud)

![Webapp Preview](preview.png)

## Demo Video

--insert video--

## Documentation

Our infrastructure is based on Docker Containers, we placed each service on a singel container (refer to diagram below):

* Flask (Webapp and file system)
* Apache Spark (Spark Setup and Master)
* Worker Nodes 1..n (Apache Spark Worker Nodes)
* MariaDB (Database)

All of those system use the docker bridge network *bdea_network* to communicate between each other. A HTML with Bootstrap forms the Webapp for our Flask Frontend and allows the user to upload text files. The Webapp offers to execute two Spark Jobs:

1. `tf_job` which is executes everytime a new text file is uploaded on the website
2. `df_job` which is the batch job that can be manually executed to generate the global term frequency word cloud based on the document frequency

The data generated from the Spark Jobs is saved in MariaDB. MariaDB has three tables that are initialized on startup:

- tf (stores the term frequency for all documents)
- df (stores the document frequency for all words)
- tfidf (stores the TFIDF value for each document)

Due to its setup Spark distrubuted the workload between the avavilable worker nodes (please read below on how to scale them).

### Architecture

The following vector image is a visualization of the above description:

![Webapp Architecture](webapp-architecture.svg)

### Challenges & Problems

* Read and write in the same sparkjob -> can cache the table 
* special character are not correcly saved in database -> change char_set and collate to utf-8
* queries in sql are sometimes not so easy 
* bootstrap elemente center -> frontend sucked
* setup with database and JDBC-driver -> link driver by spark-submit and in docker-image
* docker setup with all componands -> try and error until its works
* spark-jobs depands strongly on systems hardware  e.g. 4MB .txt-file  PC ->  11-20sec, laptop -> 2-3min

You can also view or download the documentation as a [PDF Document](documentation.pdf).

## Development

You can easily develope this application by opening up GitPod (see above) and have the whole environemt up and running. Alternatively you can clone the repo and develope locally - simply run the following commands from the roor of the repository:

```bash
docker-compose -f webapp/docker-compose.yml up
```

Worker can be scaled with `--scale spark-worker`:

```bash
docker-compose -f webapp/docker-compose.yml up --scale spark-worker=2
```

## Sources

### Text File Sources

* [The Grand Inquisitor by Fyodor Dostoyevsky](https://www.gutenberg.org/ebooks/8578)
* [The Brothers Karamazov by Fyodor Dostoyevsky](https://www.gutenberg.org/ebooks/28054)
* [The Gambler by Fyodor Dostoyevsky](https://www.gutenberg.org/ebooks/2197)
* [The Idiot by Fyodor Dostoyevsky](https://www.gutenberg.org/ebooks/2638)