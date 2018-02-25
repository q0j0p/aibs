import pandas as pd
import neurom as nm
import os, sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pymongo
# from query import *
import swc

from allensdk.core.cell_types_cache import CellTypesCache, ReporterStatus as RS
from allensdk.api.queries.cell_types_api import CellTypesApi

DBNAME = "neuron_data"
USER = None
HOST = 'localhost'
MONGODB_NAME = "neurons"
MONGODB_URI = 'mongodb://localhost:27017/'

sql_create = """
CREATE DATABASE {}
""".format(DBNAME) # not liable to sql injection
def create_database():
    try:
        #print "start"
        connection = psycopg2.connect(
        dbname = 'postgres',
        host = HOST
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql_create)

        print "database {} created".format(DBNAME)

    except:
        print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]



def create_table():
    pass

class Neuron(object):
    def __init__(self, dbname=DBNAME, host='localhost'):
        """Connects to posgresql database using psycpog2"""
        try:
            self.connection = psycopg2.connect(
            dbname = dbname,
            host = host
            )
            self.cursor = self.connection.cursor()
        except:
            pprint("Cannot connect to database {}".format(dbname))
            print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
        else:
            self.connection.autocommit = True

    def _query_sql(self, query):
        self.cursor.execute(query)

    def create_neuron_table(self):
        """Creates sql table for neuron data"""
        create_table_command = """
            CREATE TABLE IF NOT EXISTS neuron (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                origin VARCHAR(100),
                experiment_id INT references experiment(ID)
                );"""
        self.cursor.execute(create_table_command)

    def get_db_status(self):
        self._query_sql("""SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'""")
        for table in self.cursor.fetchall():
            print(table)

    def close_db(self):
        self.connection.close()

    def load_swcfile(self, swcfile, name=None):
        """Loads swc file, verifying validity of data.  Ensure:
            # index is complete and serial,
            # soma exists,
            # single tree,
            # has soma, dendrites, axons?
            # nonzero radii?
        """
        # Designate name
        filename = swcfile.split('.')
        if filename[1] == "swc":
            if name:
                self.name = name
            else:
                self.name = filename[0]

        swc.preview_file(swcfile)




    def create_morphology_table(self):

        create_table_command = """
            CREATE TABLE neuron (
                id SERIAL PRIMARY KEY,
                x FLOAT,
                y FLOAT,
                z FLOAT,
                r FLOAT,
                p INTEGER);"""

        self.cursor.execute(create_table_command)

    def find_path(self, neuron):
        pass


class aibs(object):
    def __init__(self, dbname=MONGODB_NAME):
        self.dbname = MONGODB_NAME

    def create_mongodb(self):
        pass

    def db_connect(self):
        try:
            self.mongoclient = pymongo.MongoClient(MONGODB_URI)
            print "Connected to {}".format(MONGODB_URI)
        except pymongo.errors.ConnectionFailure as e:
            print "Could not connect to MongoDB: %s".format(e)
        self.mongodbase = self.mongoclient[self.dbname]
        self.coll = self.mongodbase['']
