# koban_xie_twitter_v2_api
Python wrappers for the new Twitter API, ETL scripts for translation to an SQL database, Jupyter notebooks to interact with the SQL database.

1. `DataCollection.ipynb`: Jupyter notebook to collect data via the Twitter API
2. `docker-compose.yml`: Docker yml file to create a locally hosted MySQL container
3. `DataETL_ToMySQL.ipynb`: Jupyter notebook to create MySQL table structure and translate Twitter data to MySQL
4. `DataAnalysisVisualization.ipynb`: Jupyter notebook to create mention, hashtag, and url networks.

![pyvis network](pyvis_network.png)