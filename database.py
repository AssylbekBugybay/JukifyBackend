import mysql.connector
from datetime import datetime


class Database:
    '''
    Class performs the operations on the Databases
    '''
    def __init__(self):
        '''
        Constructor opens connection to DB
        '''
        self.config = {
            'host' : "87.106.171.240",
            'user' : "jukify",
            'password' : "SWProject2021",
            'database' : "jukifydb"
        }
    def saveParty(self, partyId, masterId):
        '''
        Stores party in the DB
        @param partyId - Party ID to be stored
        @param masterId - Party Master to be stored
        '''
        now = datetime.now()
        creationDate = now.strftime('%Y-%m-%d %H:%M:%S')
        cnx=mysql.connector.connect(**self.config)
        myCursor = cnx.cursor()
        cmd="INSERT INTO Party values(%s,%s,%s,null);"
        values=(partyId, creationDate, masterId)        
        myCursor.execute(cmd,values)
        cnx.commit()
        myCursor.close()        
        cnx.close()

    def getParties(self):
        '''
        Returns parties from DB
        @return results
        '''
        cnx=mysql.connector.connect(**self.config)
        myCursor = cnx.cursor()
        cmd="SELECT * FROM Party;"
        myCursor.execute(cmd)
        results=myCursor.fetchall()
        myCursor.close()
        cnx.close()
        return results

    def saveSong(self, partyId, song):
        '''
        Saves song in DB
        @param partyId - Party where the song was played
        @param song - Song data
        '''
        cnx=mysql.connector.connect(**self.config)
        myCursor = cnx.cursor()
        cmd="INSERT INTO Songs values(%s,%s,%s,%s,%s,%s);"
        values=(song.spotifyId, song.name, song.album, song.artist, song.imgUrl, partyId)        
        myCursor.execute(cmd,values)
        myCursor.close()
        cnx.commit()
        cnx.close()
    
    def getSongs(self, partyId):
        '''
        Returns song for a specific party from DB
        @param partyId - ID of the party
        @return results
        '''
        cnx=mysql.connector.connect(**self.config)
        myCursor = cnx.cursor()
        cmd="SELECT * FROM Songs WHERE Party_idParty="+partyId+";"        
        myCursor.execute(cmd)
        results=myCursor.fetchall()
        myCursor.close()
        cnx.close()
        return results

    def isPartyIdExist(self, newPartyId):
        '''
        Checks if party exists in DB
        @return Boolean
        '''
        cnx=mysql.connector.connect(**self.config)
        myCursor = cnx.cursor()                             #++ check what this method does
        cmd="SELECT * FROM Party WHERE idParty="+str(newPartyId)+";"
        myCursor.execute(cmd)
        results=myCursor.fetchall()
        myCursor.close()
        cnx.close()
        if(len(results)>0):
            return True
        else:
            return False

    def setClosingDate(self, partyId):
        '''
        Sets closing date of a party
        @param partyId - Party ID 
        '''
        now = datetime.now()
        closingDate = now.strftime('%Y-%m-%d %H:%M:%S')
        cnx=mysql.connector.connect(**self.config)
        myCursor = cnx.cursor()
        query="UPDATE Party SET closingDate=%s WHERE idParty = %s"
        values=(closingDate, partyId)        
        myCursor.execute(query, values)
        cnx.commit()
        myCursor.close()        
        cnx.close()

    def isPartyClosed(self, partyId):
        '''
        Checks if party is closed
        @param partyId - ID of the party
        @return Boolean
        '''
        cnx=mysql.connector.connect(**self.config)
        myCursor = cnx.cursor()
        cmd="SELECT * FROM Party WHERE idParty='"+partyId+ "' AND closingDate IS NOT NULL;"
        # then there is a closing date for a party ( then one can view history)
        myCursor.execute(cmd)
        results=myCursor.fetchall()
        myCursor.close()
        cnx.close()
        if(len(results)>0):
            return True
        else:
            return False


#db = Database()
#if (db.isPartyClosed(str(30891))):
#    print ("party closed")
#else:
#    print ("NULL -- party is not closed ")