from flask import jsonify
import json


class Party:
    '''
    Class Party is used in order to create Party objects 

    Attributes:
        1) id - Party ID
        2) masterId - Party Master ID
        3) authKey - Spotify Authorization Token
        4) member - Current members
        5) requests - Current requests
        6) deviceId - Spotify playback device
        7) queueList - Linked list with current playing queue
        8) partyName - Party name
        9) syncTime - Time since last sync
        10) songDuration - Current song duration
        11) currentMs - Current song time
    '''
    def __init__(self, id, masterId, authKey, deviceId, tempQueue, partyName):
        '''
        Constructor
        @param id - party id
        @param masterId - id of the party master
        @param authKey Spotify Authorization Token
        @param deviceId Spotify playback device
        @param tempQueue Linked list with current playing queue
        @param partyName Party name
        '''
        # constructor
        self.id = id
        self.masterId = masterId
        self.authKey= authKey
        self.member = []
        self.requests = []
        self.deviceId = deviceId
        self.queueList = tempQueue
        self.partyName = partyName
        self.syncTime = "0"
        self.songDuration = "0"
        self.currentMs = "0"
    def __del__(self):
        return
    def addMember(self, member):
        '''
        Adds a member to a party
        @param member - Member to be added
        '''
        self.member.append(member)
    def deleteMember(self, member):
        '''
        Deletes member from a party
        @param member - Member to be removed
        '''
        i = 0
        while (self.member[i].id != member.id and i < len(self.member)):
            i = i+1
        self.member.pop(i)
    def getMember(self):
        '''
        Returns member
        @return member
        '''
        return self.member
    def getRequests(self):
        '''
        Returns requests
        @return requests
        '''
        return self.requests
    def getRequest(self):
        '''
        Returns request
        @return request
        '''
        if len(self.requests) != 0:
            response = jsonify( 
                spotifyid = self.requests[len(self.requests)-1].getSpotifyId(), 
                name = self.requests[len(self.requests)-1].getName(),
                album = self.requests[len(self.requests)-1].getAlbum(),
                artist = self.requests[len(self.requests)-1].getArtist(),
                amount = len(self.requests)-1
                )
            self.requests.pop(len(self.requests)-1)
            return response
        else:
            return None
    def toString(self):
        '''
        toString
        @return String
        '''
        return "ID: " + str(self.id) + " |  masterId: " + str(self.masterId)
    def join(self, memberId):
        '''
        Joins party 
        @param memberId - Member to join
        @return Boolean
        '''
        if memberId not in self.member:
            self.member.append(memberId)
            return True
        else:
            return False
    def leave(self, memberId):
        '''
        Leaves party
        @param memberId - Member to leave
        @return Boolean
        '''
        if memberId == self.masterId:
            return False
        if memberId not in self.member:
            return False
        else:
            self.member.remove(memberId)
            return True
    def addRequest(self, song):
        '''
        Adds song to request
        @param song - Song to be added
        '''
        self.requests.append(song)
    def clearRequests(self):
        '''
        Clears requests
        '''
        self.requests.clear()

        

class Master:
    '''
    Class Master is used in order to create instance of Party Master
    
    Attributes:
        1) Id - ID of the partymaster
    '''
    def __init__(self, id):
        '''
        Constructor
        @param id - Id of the partymaster
        '''
        self.id = id
    def getId(self):
        '''
        Returns id of the party master
        @return id
        '''
        return self.id


class Song:
    '''
    Class Song- to create instances of Song

    Attributes:
        1) spotifyId - Spotify ID of the song
        2) name - Song name
        3) album - Song album
        4) artist - Song artist
        5) imgUrl - Link to image
    '''
    def __init__(self, spotifyId=None, name=None, album=None, artist=None, url="", jsonObj=None):
        '''
        Constructor
        @param spotifyId - Spotify ID of the song
        @param name - Song name
        @param album - Song album
        @param artist - Song artist
        @param url - Link to image
        @param jsonObj - If json object is provided instead
        '''
        if(jsonObj is None):
            self.spotifyId = spotifyId
            self.name = name
            self.album = album
            self.artist = artist
            self.imgUrl = url
        else:
            imgUrl = ""
            if('images' in jsonObj['album']):
                imgUrl = jsonObj['album']['images'][0]['url']
            self.spotifyId = jsonObj['id']
            self.name = jsonObj['name']
            self.album = jsonObj['album']['name']
            self.artist = jsonObj['artists'][0]['name']
            self.imgUrl = imgUrl

    def toJSON(self):
        '''
        Returns song data in JSON format
        @return JSON String
        '''
        return jsonify(spotifyId = self.spotifyId, name = self.name, album = self.album, artist = self.artist)
    def __str__(self):
        '''
        toString song data
        @return String
        '''
        return "ID: " + self.spotifyId + " Name: " + self.name + " Album: " + self.album + " Artist: " + self.artist
        

class Node(object):
    '''
    Class Node to create instances of node in the linked list
    
    Attributes:
        1) data - data of the node
        2) next - reference to next node
    '''
    def __init__(self, data=None, nextNode=None):
        '''
        Constructor
        @param data - Data of the node
        @param nextNode - Reference to next node
        '''
        self.data = data
        self.next = nextNode
    def getData(self):
        '''
        Gets data from node
        @return data
        '''
        return self.data
    def getNext(self):
        '''
        Gets reference to next from node
        @return next
        '''
        return self.next
    def setNext(self, newNext):
        '''
        Sets reference to next node
        @param newNext - Reference to next node
        '''
        self.next = newNext


class QueueLinkedList(object):
    '''
    Class QueueLinkedList implements linked list for song queue

    Attributes:
        1) head - Front of the list
        2) lastInsertedOutOfOrder - Last node inserted dynamically 
    '''
    def __init__(self, head=None):
        '''
        Constructor
        @param head - Beginning node of the list
        '''
        self.head = head
        self.lastInsertedOutOfOrder = None
    def insertHead(self, data):
        '''
        Inserts node at front
        @param data - Data for new node
        '''
        newNode = Node(data)
        newNode.setNext(self.head)
        self.head = newNode    
    def insertNext(self, data):
        '''
        Inserts node after last dynamically inserted node
        @param data - Data for new node
        '''
        newNode = Node(data)
        if self.lastInsertedOutOfOrder is None:
            newNode.setNext(self.head.next)
            self.head.setNext(newNode)
            self.lastInsertedOutOfOrder = self.head.next
        else:
            newNode.setNext(self.lastInsertedOutOfOrder.next)
            self.lastInsertedOutOfOrder.setNext(newNode)
            self.lastInsertedOutOfOrder = self.lastInsertedOutOfOrder.next
        
    def insertLast(self, data):
        '''
        Inserts node at the end
        @param data - Data for new node
        '''
        newNode = Node(data)
        if(self.head == None):
            self.head = newNode
            return
        else:
            temp = self.head
            while(temp.next != None):
                temp = temp.next
            temp.next = newNode    
    def size(self):
        '''
        Returns size of the list
        @return count
        '''
        current = self.head
        count = 0
        while current:
            count += 1
            current = current.getNext()
        return count
    def search(self, id):
        '''
        Searches for node with specific data
        @param id - Data of a node to be found
        @return Node
        '''
        current = self.head
        found = False
        while current and found is False:
            if current.getData().spotifyId == id:
                found = True
            else:
                current = current.getNext()
        if current is None:
            raise ValueError("Data not in list")
        return current
    def delete(self, id):
        '''
        Deletes node with specific data
        @param id - Data of a Node to be deleted
        '''
        current = self.head
        previous = None
        found = False
        while current and found is False:
            if current.getData().spotifyId == id:
                found = True
            else:
                previous = current
                current = current.getNext()
        if current is None:
            raise ValueError("Data not in list")
        if previous is None:
            self.head = current.getNext()
        else:
            previous.setNext(current.getNext())
    def deleteHead(self):
        '''
        Delets head
        '''
        self.head = self.head.getNext()
    def skipUntilMatch(self, id):
        '''
        Cuts the beginning of the list until specific Node has been found
        @param id - Data of a node to be skipped until
        @return Boolean
        '''
        frog = self.head
        while (frog.getData().spotifyId != id):
            frog = frog.next
        if frog is None:
            return False
        self.head = frog
        return True
    def toArray(self):
        '''
        Returns list as an array
        @return NodeArray
        '''
        songsArray = []
        current = self.head
        while current:
            songsArray.append(json.dumps(current.getData().__dict__))
            current = current.next
        return songsArray
    def printList(self):
        '''
        Prints the list in console output
        '''
        print("---------------")
        arr = self.toArray()
        for val in arr:
            print(val)
        print("---------------")
    #General knowledge of how linked list works
    
    #llist.head = Node(1)
    #second = Node(2)
    #third = Node(3)

    '''
    Three nodes have been created.
    We have references to these three blocks as head,
    second and third
 
    llist.head        second              third
         |                |                  |
         |                |                  |
    +----+------+     +----+------+     +----+------+
    | 1  | None |     | 2  | None |     |  3 | None |
    +----+------+     +----+------+     +----+------+
    '''
 
    #llist.head.next = second; # Link first node with second
 
    '''
    Now next of first Node refers to second.  So they
    both are linked.
 
    llist.head        second              third
         |                |                  |
         |                |                  |
    +----+------+     +----+------+     +----+------+
    | 1  |  o-------->| 2  | null |     |  3 | null |
    +----+------+     +----+------+     +----+------+
    '''
 
    #second.next = third; # Link second node with the third node
 
    '''
    Now next of second Node refers to third.  So all three
    nodes are linked.
 
    llist.head        second              third
         |                |                  |
         |                |                  |
    +----+------+     +----+------+     +----+------+
    | 1  |  o-------->| 2  |  o-------->|  3 | null |
    +----+------+     +----+------+     +----+------+
    '''
