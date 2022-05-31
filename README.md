1. pip install requirements.txt
2. If file with DB (data/db/nba.db) not exist, run command:<br />python modules/db_worker/init_sqlite_db.py
3. If you work with new DB, run script to save franchises to DB: </br> python modules/scrapper/franchises_scrapper.py
4. If you work with new DB, to open file modules/scrapper/main.py and set self.get_status(is_start=True); is_start=True;
5. run command: docker-compose up --build
6. It's all