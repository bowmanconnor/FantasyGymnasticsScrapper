from pymongo import MongoClient
from pprint import pprint

class Connector:
    def __init__(self):
        self.__client = None    # private 
        self.__db = None        # private
        self.__collection = None     # private

    def connectDB(self):
        self.__client = MongoClient('mongodb+srv://jkula:M0nk3y25!@rtncluster-tfnqg.gcp.mongodb.net/test?retryWrites=true&w=majority')
        self.__db = self.__client['rtn_db']
        self.__collection = self.__db['college_gymnastics']
        return

    def create_directory(self, dir, path):
        # prevent duplicate directories
        if (self.__collection.find_one( {'dir': dir}, {'path', path} )):
            print("Sorry, that directory has already been created.")
            return
        doc = { 'dir': dir,
                'path': path,
                }
        doc_id = self.__collection.insert_one(doc).inserted_id
        return doc

    def get_doc_id(self, dir, path):
        return self.__collection.find_one( {'dir': dir}, {'path': path} )['_id']

    def print_doc(self, doc_id):
        pprint(self.__collection.find_one( {'_id': doc_id} ))
        return

    def get_collection(self):
        return self.__collection

    def delete_doc(self, dir, path):
        return self.__collection.find_one_and_delete( {'dir': dir}, {'path': path} )
    
    def list_docs(self, path):
        # for doc in self.__collection.find( {'path': path} ):
        #     pprint(doc)
        for doc in self.__collection.find( {'path': path} ):
            pprint(doc)
        return

if __name__ == "__main__":
    # connect to MongoDB
    mongoDB = Connector()
    mongoDB.connectDB()
    print("----------------------------------------------------------------------------------------------------")
    # create and store a new user
    # print("ADDING NEW DOCUMENT...")
    # print(mongoDB.create_directory("2019", "Men/"))
    # print("----------------------------------------------------------------------------------------------------")
    # pprint(mongoDB.list_users())
    # print("----------------------------------------------------------------------------------------------------")
    # print("DELETING DOCUMENT...")
    # pprint(mongoDB.delete_doc("2019", "Men/"))
    # print("----------------------------------------------------------------------------------------------------")
    # print docs in database
    print("LIST DOCUMENTS:")
    pprint(mongoDB.list_docs(""))
    print("----------------------------------------------------------------------------------------------------")

