## Setup

Install docker-compose in ubuntu
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

```
sudo chmod +x /usr/local/bin/docker-compose
```

start container
```
docker-compose up --scale spark-worker=2
```

--> http://localhost:5000/

.txt-file examples can be dowloaded [here](https://corpus.canterbury.ac.nz/descriptions/#large) or [.txt-books](https://www.gutenberg.org/) 


### ToDo's
* PDF/Architekturplan (draw.io) überarbeiten
* run df_job von flask (button im frontend)
* Präsentations Video


### Problems
* Read and write in the same sparkjob -> can cache the table 
* special character are not correcly saved in database -> change char_set and collate to utf-8
* queries in sql are sometimes not so easy 
* bootstrap elemente center -> frontend sucked
* setup with database and JDBC-driver -> link driver by spark-submit and in docker-image
* docker setup with all componands -> try and error until its works
* spark-jobs depands strongly on systems hardware  e.g. 4MB .txt-file  PC ->  11-20sec, laptop -> 2-3min
