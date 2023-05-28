import sqlite3
import datetime

DATABASE_FILENAME = 'consultancy.db'

class ConsultancyDatabase():

    def __init__(self, filename, temporary_run=False):
        self.filename = filename
        self.schemas = ['CREATE TABLE IF NOT EXISTS business(bid INTEGER PRIMARY KEY, name TEXT, desc TEXT, proj INT)',
                        'CREATE TABLE IF NOT EXISTS consultant(cid INTEGER PRIMARY KEY, image BLOB, name TEXT, tech TEXT, about TEXT)',
                        'CREATE TABLE IF NOT EXISTS project(pid INTEGER PRIMARY KEY AUTOINCREMENT, bid INTEGER, name TEXT, tagline TEXT, stipend INTEGER, desc TEXT, tech TEXT)',
                        'CREATE TABLE IF NOT EXISTS application(cid INTEGER, pid INTEGER, created TEXT, status INTEGER, PRIMARY KEY(cid, pid))']
        self.login_schemas = ['CREATE TABLE IF NOT EXISTS login(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT, category INTEGER)']
        # category 1 represents consultant, 2 represents business
        self.create_database()
        self.create_tables()
        self.create_login_tables()
        if temporary_run:
            self.create_fake_users()
    
    def create_fake_users(self):
    #     self.add_business("BUSY", "busi@ness", "busy")
    #     self.add_consultant("CONSUL", "consult@ant", "consul")
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        # curr.execute('DELETE FROM application')
        # curr.execute(f"INSERT OR IGNORE INTO project (bid, name, tagline, tech) VALUES(1, 'project hai bhai', 'bas project', 'mongo db, bola na', 'Kal subah')")
        # curr.execute(f"INSERT OR IGNORE INTO project (bid, name, tagline, tech) VALUES(1, 'bas project', 'project hai bhai', 'php, bola na', 'Kal raat')")
    #     curr.execute(f"INSERT OR IGNORE INTO application VALUES(2, 3, 'now', 'wow')")
    #     curr.execute(f"INSERT OR IGNORE INTO application VALUES(2, 1, 'now', 'wow')")
        conn.commit()
        conn.close()
    
    def create_database(self):
        conn = sqlite3.connect(self.filename)
        conn.close()
    
    def create_tables(self):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        for schema in self.schemas:
            curr.execute(schema)
        conn.commit()
        conn.close()
    
    def create_login_tables(self):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        for schema in self.login_schemas:
            curr.execute(schema)
        conn.commit()
        conn.close()
    
    def search_login_using_id(self, id):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f'SELECT * FROM login WHERE id = {id}')
        user = curr.fetchone()
        conn.commit()
        conn.close()
        return user
    
    def search_login_using_email(self, email):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"SELECT * FROM login WHERE email = '{email}'")
        user = curr.fetchone()
        conn.commit()
        conn.close()
        return user
    
    # add lines to add consultants and businesses to their specific tables in the db
    
    def add_consultant(self, name, email, password):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"INSERT INTO login (email, password, category) VALUES ('{email}', '{password}', 1)")
        conn.commit()
        curr.execute(f"SELECT id FROM login WHERE email = '{email}' AND category = 1")
        cid = curr.fetchone()[0]
        curr.execute(f"INSERT INTO consultant (cid, name) VALUES ({cid}, '{name}')")
        conn.commit()
        conn.close()
    
    def add_business(self, name, email, password):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"INSERT INTO login (email, password, category) VALUES ('{email}', '{password}', 2)")
        conn.commit()
        curr.execute(f"SELECT id FROM login WHERE email = '{email}' AND category = 2")
        bid = curr.fetchone()[0]
        curr.execute(f"INSERT INTO business (bid, name) VALUES ({bid}, '{name}')")
        conn.commit()
        conn.close()

    def add_project(self, name, tagline, desc, stipend, tech, bid):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"INSERT INTO project (bid, name, tagline, desc, stipend, tech) VALUES ({bid}, '{name}', '{tagline}', '{desc}', {stipend}, '{tech}')")
        conn.commit()
        conn.close()
    
    def get_projects_for_business(self, id):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"SELECT name, tagline, tech FROM project WHERE bid = {id}")
        projects = curr.fetchall()
        conn.commit()
        conn.close()
        return projects

    def get_applications_using_cid(self, id):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"SELECT name, created, status FROM application a, project p WHERE cid = {id} AND a.pid = p.pid")
        applications = curr.fetchall()
        conn.commit()
        conn.close()
        return applications
    
    def get_consultant_from_login_id(self, id):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"SELECT name FROM consultant WHERE cid = '{id}'")
        user = curr.fetchone()[0]
        conn.commit()
        conn.close()
        return user
    
    def get_business_from_login_id(self, id):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"SELECT name FROM business WHERE bid = '{id}'")
        user = curr.fetchone()[0]
        conn.commit()
        conn.close()
        return user
    
    def get_projects_by_cid(self, cid):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"SELECT pid, p.name, p.tagline, p.stipend, b.name FROM project p, business b WHERE b.bid = p.bid AND p.pid NOT IN (SELECT a.pid FROM application a WHERE a.cid = {cid})")
        projects = curr.fetchall()
        conn.commit()
        conn.close()
        return projects
    
    def get_project_by_pid(self, pid):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"SELECT p.*, b.name FROM project p, business b WHERE p.pid = {pid} AND p.bid = b.bid")
        details = curr.fetchone()
        conn.commit()
        conn.close()
        return details
    
    def get_projects_count_by_bid(self, bid):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"SELECT COUNT(*) FROM project WHERE bid = {bid}")
        posted_count = curr.fetchone()[0]
        conn.commit()
        conn.close()
        return posted_count
    
    def get_applications_count_by_bid(self, bid):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        curr.execute(f"SELECT COUNT(*) FROM application WHERE pid IN (SELECT pid from project WHERE bid = {bid})")
        application_count = curr.fetchone()[0]
        conn.commit()
        conn.close()
        return application_count
    
    def add_application(self, cid, suggestions, pid):
        conn = sqlite3.connect(self.filename)
        curr = conn.cursor()
        # 0 is unreviewed, -1 is rejected, 1 is approved
        curr.execute(f"INSERT INTO application (cid, pid, created, status) VALUES ({cid}, {pid}, '{datetime.datetime.now()}', 0)")
        conn.commit()
        conn.close()
    



# db = ConsultancyDatabase('db.db')
