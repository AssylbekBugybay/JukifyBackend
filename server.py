from flask import Flask, render_template, request, jsonify
import random
import classes
import json
import sys
import spotipy
import database
from datetime import datetime

app = Flask(__name__)

parties = {}

# instance of class Database
myDb = database.Database()

@app.route('/createParty', methods =['POST'])
def createParty():
    """
    Needed Json data for this request:
    {
        "userId": "1",
        "authToken": "ASLDKfmasldkmfaskme2131re3dq3"
        "playlistId" : "37i9dQZF1DXbKGrOUA30KN",
        "partyName": "prterltmelr"
    }
    return Json data for this request:
    {
        response: "success" or "failure"
        partyId: id of the party instance newParty created
        requestId: 0(specify later why it has to be returned)
        queueList: json array produced from linked list of songs list of party master

    }
    Method is creates party instance and stores in the Databases:
    1) Receives POST request and gets json data: masterId, authKey, playlistId and partyName 
    2) Then the correctness of the token is checked, if token is not correct failure json response is returned
    3) Available online spotify devices are checked, smartphone is selected if there are multiple devices
    4) After that the 5 digit PartyID is generated, method also checks if such Party ID already exists in the databases
       while generating the Party instance newParty we also provide temporary linked list to store the music queue
    5) As the instance is generated list of Party instances is made and after that instance is saved in databases (partyId and mastedId is stored)
    6) First song from the playlist is played
    7) The list of first 100 songs from playlist of party master is fetched, to fetch the country code "DE" is used, 
       additionally "trach" and "episode" is stored
    8) From the fetched method the enumerated object is made to make it iterable
    9) While iterating the variables are stored and song class instance is made
    10) Each song is added to the newParty linked list
    """
    # get POST content
    masterId = request.get_json()['userId']
    authKey = request.get_json()['authToken']
    playlistId = request.get_json()['playlistId']
    partyName = request.get_json()['partyName']
    #will be taken from json
    deviceId=""
    
    #if token is invalid, dont create party
    try:
        spotify = spotipy.Spotify(auth=authKey)
        deviceList = spotify.devices()
    except:
        return jsonify( response = "Failure: Access token expired or there is no active device", requestId="0")

    if(len(deviceList["devices"]) > 0):
        for device in deviceList["devices"]:
            if(device["type"] == "Smartphone"):
                deviceId = device["id"]
                break
        if(deviceId == ""):
            deviceId = deviceList["devices"][0]["id"]
    else:
        return jsonify( response = "Failure: There is no active device", requestId="0")
    
    #generate party id
    partyId = random.randint(10000,99999)
    while myDb.isPartyIdExist(partyId):
        partyId = random.randint(10000,99999)      
    #we might use hash str in future
    partyId=str(partyId)  
    ## create party instance
    #temp Queue
    tempList = classes.QueueLinkedList()
    newParty = classes.Party(partyId, masterId, authKey, deviceId, tempList, partyName)
    # save party instance
    parties[newParty.id] = newParty    
    myDb.saveParty(newParty.id,masterId)

    #Play first song from playlist
    spotify.shuffle(False,device_id=deviceId)
    spotify.start_playback(context_uri='spotify:playlist:'+playlistId , device_id=deviceId)
    #add songs from playlist to linkedlist
    songsResult = spotify.playlist_items( playlistId, limit=100, market='DE', additional_types=("track", "episode"))
    for i,item in enumerate(songsResult['items']):
        track = item['track']
        imgUrl = ""
        if(track is not None):
            if( 'images' in track['album'] ):
                imgUrl =  track['album']['images'][0]['url']
            song=classes.Song(track['id'], track['name'], track['album']['name'], track['artists'][0]['name'], imgUrl)
            if(i==0):
                
                newParty.songDuration = str(track['duration_ms'])
                newParty.syncTime = datetime.now()
            myDb.saveSong(partyId, song)
            newParty.queueList.insertLast(song)         
    #Check the content of the list (for manual debug reasons)
    # node = newParty.queueList.head
    # while node:
    #     print(node.getData(), file=sys.stdout)
    #     node = node.next

    return jsonify( response="Success", partyId = newParty.id, requestId="0", queueList=newParty.queueList.toArray())




@app.route('/closeParty', methods = ['POST'])
def closeParty():
    '''
    Required body in JSON
    {
        "userId": "12e11",
        "partyId": "3781"
    }
    Method deletes the party:
    1) Receives POST request and gets json data: partyId and masterId
    2) Server has to make sure if such a Party exists. Also server makes sure that the request is coming from right Party Master
    3) Both checks are done via comparing the ids inside the existing array of Party instances
    4) If both checks are done succussfully then corresponding responce is generated and Closing Date in Party table in databases is updated
    5) If checks are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    masterId = postData['userId']
    partyId = postData['partyId']

    #check if thats master who wants to close party
    if(partyId in parties):            
        if parties[partyId].masterId == masterId:
            try:
                spotify = spotipy.Spotify(auth=parties[partyId].authKey)
                spotify.pause_playback(device_id=parties[partyId].deviceId)
            except:
                pass
            myDb.setClosingDate(partyId)
            del parties[partyId]            
            return jsonify( response = "Success: PARTY IS DELETED" , requestId="1")
        else:
            return jsonify ( response = "Failure: PARTY ID MATCHED, BUT MASTER ID DOES NOT MATCH ", requestId="1")
    #return jsonify( masterId = masterId, partyId = str(newParty.getId()))
    else:
        return jsonify( response = "Failure: PARTY ID DOES NOT MATCH" , requestId="1")
    





@app.route('/join', methods = ['POST'])
def join():
    '''
    Required body in JSON
    {
        "userId": "1",
        "partyId": "3781"
    }
    Method joins the party:
    1) Receives POST request and gets json data: userId and partyId
    2) Check if party exists
    3) Get users currently playing song, song should be of "DE" country code. Songs id, name, album and artist, and if image url is available is also sent
    5) If checks are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    userId = postData['userId']
    partyId = postData['partyId']
    # check if party exists
    if partyId not in parties:
        return jsonify( response = "Failure: BAD PARTY ID" , requestId="2")

    if parties[partyId].join(userId):
        #maybe return current song
        spotify = spotipy.Spotify(auth=parties[partyId].authKey)
        results = spotify.currently_playing(market='DE')   
        if(results is None):
            return jsonify( response = "Success: JOINED", partyId = partyId, userId = userId, currentMs = "0", 
            song="No Playback", requestId="2") 
        item = results['item']
        currentMs = str(results['progress_ms'])
        durationMs = str(item['duration_ms'])
        imgUrl = ""
        if( 'images' in item['album'] ):
            imgUrl =  item['album']['images'][0]['url']
        song=classes.Song(item['id'], item['name'], item['album']['name'], item['artists'][0]['name'], imgUrl)
        
        return jsonify( response = "Success: JOINED", partyId = partyId, partyName=parties[partyId].partyName, 
        userId = userId, currentMs = currentMs, durationMs=durationMs, 
        song=json.dumps(song.__dict__), queueList=parties[partyId].queueList.toArray(), requestId="2") 
    else:
        return jsonify( response = "Failure: COULD NOT JOIN THE PARTY", requestId="2")


@app.route('/leave', methods = ['POST'])
def leave():
    '''
    Required body in JSON
    {
        "userId": "1",
        "partyId": "3781"
    }
    Method allows for attendants to leave the party:
    1) Receives POST request and gets json data: userId and partyId
    2) Check if party exists
    3) Check if requesting partyId is party master. It returns false if it is Party Master. Because party master cant leave, he can only close the party.
    5) If checks are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    userId = postData['userId']
    partyId = postData['partyId']
    # check if party exists
    if partyId not in parties:
        return jsonify( response = "Failure: BAD PARTY ID" , requestId="3")

    if parties[partyId].leave(userId):
        #print(parties[partyId].member, file=sys.stdout) 
        return jsonify( response = "Success: LEFT", partyId = partyId, userId = userId, requestId="3")
    else:
        return jsonify( response = "Failure: COULD NOT LEAVE THE PARTY", requestId="3")




@app.route('/playSong', methods = ['POST'])
def playSong():
    '''
    Required body in JSON
    {    
        "partyId": "3781"
        "songId" : "232mk3v32K2r3R"
    }
    Method allows to play the song:
    1) Receives POST request and gets json data: songId and partyId
    2) Check if party exists
    3) Use start_playback() method if SongId is right
    4) Song id, name, album and artist, and if image url is available is also saved in the databases
    5) If checks are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    
    songId = postData['songId']
    partyId = postData['partyId']
    
    # check if party exists
    if(partyId in parties):
        spotify = spotipy.Spotify(auth=parties[partyId].authKey) 
        try:
            spotify.start_playback(uris=['spotify:track:'+songId], device_id=parties[partyId].deviceId)            
            #(uris=['spotify:track:'+songId])  
        except:
            return jsonify(response = "Failure: Song could not be played.", requestId="4")
        
        item = spotify.track(songId, market='DE')        
        imgUrl = ""
        if('images' in item):
            imgUrl = item['images'][0]['url']
        song = classes.Song(item['id'], item['name'], item['album']['name'], item['artists'][0]['name'], imgUrl)      
        myDb.saveSong(partyId, song)
        return jsonify(response = "Success: Song is being played", requestId="4")
    else:     
        return jsonify( response = "Failure: BAD PARTY ID" , requestId="4")
        
    
# Use postman to send request to http://127.0.0.1:5000/searchSong with body in JSON:
#{    
#    "partyId": 3781
#    "searchWord" : "Never gonna let you down"
#}
#returns jsonArray

@app.route('/searchSong', methods = ['POST'])
def searchSong():
    '''
    Required body in JSON
    {
        "partyId": "1234"
        "searchWord":"Never gonna let you down"
    }
    Method allows to search song:
    1) Receives POST request and gets json data: searchWord and partyId
    2) Check if party exists
    3) Using search() method we get 5 songs with "DE" country code
    4) Song id, name, album and artist, and if image url is available is returned
    5) If checks are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    
    searchWord = postData['searchWord']
    partyId = postData['partyId']
    
    # check if party exists
    if(partyId in parties):       
        spotify = spotipy.Spotify(auth=parties[partyId].authKey) 
        results=spotify.search(q=searchWord, limit=5, market='DE')        
        items = results['tracks']['items']
        songs=[]
        if len(items) > 0:
            for i,item in enumerate(items):
                imgUrl = ""
                if( 'images' in item['album'] ):
                    imgUrl =  item['album']['images'][0]['url']
                song = classes.Song(item['id'], item['name'], item['album']['name'], item['artists'][0]['name'], imgUrl)
                #songs[i]=json.dumps(song.__dict__)
                songs.append(json.dumps(song.__dict__))       
            return jsonify( response= "Success: Lists of songs returned", songs=songs, requestId="5")
        else:
            return jsonify(response = "Failure: No songs found", requestId="5")
    else:        
        return jsonify( response = "Failure: BAD PARTY ID" , requestId="5")        


# 
#returns jsonArray

@app.route('/getPartyHistory', methods = ['POST'])
def getPartyHistory():
    '''
    Required body in JSON
    {    
        "partyId": 3781
    }
    Method allows to fetch the party history:
    1) Receives POST request and gets json data: partyId
    2) isPartyClosed() method is to see if it is over, we check if there is an existing "closing date entry" in the database
    4) Array of Json strings of Songs is returned
    5) If checks are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    partyId = postData['partyId']
    
    # LIMITATION to use this functionality !
    # we can only view the party history if a party already took place and finished.
    # we cannot see any party history detail if party is not over yet.
    # To see if it is over, we check if there is an existing "closing date entry" in the database
    # If closing date entry is not Null ( this is doublechecked by isPartyClosed function in database.py), then we proceed.

    #for now we dont care if party is closed
    if(myDb.isPartyClosed(partyId) or True):     # if party is closed, only then we can see results  
        results = myDb.getSongs(partyId)
        songs=[]  
        if len(results) > 0:
            for i,item in enumerate(results):
                song=classes.Song(item[0], item[1], item[2], item[3], item[4])
                songs.append(json.dumps(song.__dict__))
            return jsonify(response = "Success: Songs that are played during the party (ID) " + partyId, songs=songs, requestId="6") 
        else:
            return jsonify(response = "Failure: No songs were played during this party ", requestId="6")        
    else:     
        return jsonify(response = "Failure: Party History cannot be viewed ( party does not exist or bad ID)", requestId="6")    

# Use postman to send request to http://127.0.0.1:5000/getPlaylists with body in JSON:
#{    
#    "authToken": "3781kjnfelkrjnflk34jnj3"
# }

@app.route('/getPlaylists', methods = ['POST'])
def playlists():
    '''
    Required body in JSON:
    {    
        "authToken": "3781kjnfelkrjnflk34jnj3"
    }
    Method allows to get Spotify playlist:
    1) Receives POST request and gets json data: authKey
    2) Connect to spotify using authKey
    3) Method current_user_playlists() gets current users playlist
    4) If the users playlist has less than 5 or just 5 songs, then featured_playlists() method gets 30 songs from Spotify featured playlist. playlistItems list is created for that.
    5) If checks are failed or passed corresponding messages are sent
    '''
    # get POST content
    postData = request.get_json()
    authKey = request.get_json()['authToken']
    #connect to spotify
    spotify = spotipy.Spotify(auth=authKey) 

    #get user spotify playlists
    try:
        userPlaylists = spotify.current_user_playlists(limit=30, offset=0)
    except:
        #in case authtoken is invalid
        return jsonify(response="Failure", requestId="7")

    playlistCount = userPlaylists['total']
    returnList=[]
    if playlistCount <= 5:
        featuredPlaylists = spotify.featured_playlists(locale=None, country=None, timestamp=None, limit=30-playlistCount, offset=0)
        ### Adding user playlist if exists
        playlistItems = userPlaylists['items']
        for i,item in enumerate(playlistItems):  
            playlist={}
            if(item['tracks']['total'] != 0):
                playlist['imageUrl'] = item['images'][0]['url']
                playlist['playlistName'] = item['name']
                playlist['playlistId'] = item['id']
                playlist['numberOfSongs'] = item['tracks']['total']
                returnList.append(playlist)

        ### Parsing featured playlists
        playlistItems = featuredPlaylists['playlists']['items']
        for i,item in enumerate(playlistItems):  
            playlist={}
            if(item['tracks']['total'] != 0):
                playlist['imageUrl'] = item['images'][0]['url']
                playlist['playlistName'] = item['name']
                playlist['playlistId'] = item['id']
                playlist['numberOfSongs'] = item['tracks']['total']
                returnList.append(playlist)
        return jsonify(response="Success: Playlists returned", playlists=returnList, requestId="7")

    else:
        playlistItems = userPlaylists['items']
        for i,item in enumerate(playlistItems):  
            playlist={}
            if(item['tracks']['total'] != 0):
                playlist['imageUrl'] = item['images'][0]['url']
                playlist['playlistName'] = item['name']
                playlist['playlistId'] = item['id']
                playlist['numberOfSongs'] = item['tracks']['total']
                returnList.append(playlist)
        return jsonify(response="Success: Playlists returned", playlists=returnList, requestId="7")
    




@app.route('/updateToken', methods = ['POST'])
def updateToken():
    '''
    Required body in JSON
    {
       "partyId": "21324",
       "authToken": "3781"
    }
    Method updateToken() allows to update authKey:
    1) Receives POST request and gets json data: authToken and partyId
    2) Check if party exists
    3) If checks are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    newToken = postData['authToken']
    partyId = postData['partyId']
    # check if party exists
    if partyId not in parties:
        return jsonify( response = "Failure: BAD PARTY ID", requestId="8" )
    else:
        parties[partyId].authKey = newToken
        return jsonify( response = "Success: Spotify token is updated.", requestId="8")

@app.route('/addSong', methods = ['POST'])
def addSong():
    '''
    Required body in JSON
    {
    "partyId": "21324",
    'spotifyId': "3781",
    'name': "hey you",
    'album' : 'albumname',    
    'artist' : 'pink floyd',
    'imgUrl' :'www.imgur.com'          
    }
    Method addSong() allows to add Song into the queue:
    1) Receives POST request and gets json data: songJson and partyId
    2) Check if party exists
    3) Add the song to the queue list and to users queue
    3) If checks are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    partyId = postData['partyId']
    spotifyId = postData['spotifyId']
    name = postData['name']
    album = postData['album']
    artist = postData['artist']
    url = postData['imgUrl']
    # check if party exists
    if partyId not in parties:
        return jsonify( response = "Failure: BAD PARTY ID", requestId="9" )   
    else:
        song = classes.Song(spotifyId, name, album, artist, url)
        try:
            spotify = spotipy.Spotify(auth=parties[partyId].authKey)  
            spotify.add_to_queue(song.spotifyId, device_id = parties[partyId].deviceId)
            parties[partyId].queueList.insertNext(song)
            myDb.saveSong(partyId, song)
            return jsonify( response = "Success: Song is added to queue.", requestId="9")
        except:
            return jsonify( response = "Failure: Access token expired or there is no active device", requestId="9")
        

@app.route('/skipSong', methods = ['POST'])
def skipSong():
    '''
    Required body in JSON
    {
        "partyId": "21324",
        "userId": "3781"
    }
    Method skipSong() allows to skip the Song:
    1) Receives POST request and gets json data: userId and partyId
    2) Check if party exists
    3) Use method next_track() to set next track
    4) If checks and operations are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    userId = postData['userId']
    partyId = postData['partyId']
    #check party exists
    if((partyId in parties) and (parties[partyId].masterId == userId)):
        try:
            spotify = spotipy.Spotify(auth = parties[partyId].authKey)  
            spotify.next_track(device_id = parties[partyId].deviceId)
            return jsonify( response = "Success: Song is skipped." , requestId="10")
        except:
            return jsonify( response = "Failure: Access token expired or there is no active device", requestId="10")
    else:
        return jsonify( response = "Failure: partyId doesnt exist or user has no right to skip song." , requestId="10")
    
@app.route('/setNextSong', methods = ['POST'])
def setNextSong():
    '''
    Required body in JSON
    {
        "partyId": "21324",
        "songId": "3781"
    }
    Method setNextSong() allows to Party Master to  set the next Song into the queue:
    1) Receives POST request and gets json data: songId and partyId
    2) Check if party exists
    3) Delete the song from the queue and using insertNext() set next track
    4) If checks and operations are failed or passed corresponding messages are sent
    '''
    # get POST data
    postData = request.get_json()
    songId = postData['songId']
    partyId = postData['partyId']
    #check party exists
    if(partyId in parties):
        try:
            spotify = spotipy.Spotify(auth = parties[partyId].authKey)  
            spotify.add_to_queue(songId, device_id = parties[partyId].deviceId)
            #we need to remove it from queque and add as next song
            song=parties[partyId].queueList.search(songId)
            parties[partyId].queueList.insertNext(song.getData())
            return jsonify( response = "Success: Song is moved up as next song", queueList=parties[partyId].queueList.toArray(), requestId="11")
        except:
            return jsonify( response = "Failure: Access token expired or there is no active device", requestId="11")
    else:
        return jsonify( response = "Failure: partyId doesnt exist or user has no right to skip song." , requestId="11")
    

@app.route('/getQueueList', methods = ['POST'])
def getQueueList():
    '''
    Required body in JSON
    {
        "partyId" :"1234"
    }
    Method getQueueList() allows to Party Member to get current playing queue
    1) Receives POST request and gets json data: partyId
    2) Check if party exists
    3) Check if recently checked
    4) If yes, return recent check with sync
    4) If not, get current player status and return
    '''
    postData = request.get_json()
    partyId = postData['partyId']

    if(partyId in parties):
        newTime = datetime.now()
        #check if the status asked already by another user in 5 seconds
        if(( newTime - parties[partyId].syncTime ).seconds > 5):            
            parties[partyId].syncTime = newTime
            spotify = spotipy.Spotify(auth=parties[partyId].authKey)
            try:
                results = spotify.currently_playing(market='DE')   
            except:
                return jsonify(response ="Failure: Access token expired.", requestId="12")
            if(results != None):
                #item = results['item']
                currentSpotifyId = results['item']['id']
                currentSpotifyDuration = results['item']['duration_ms']
                if( currentSpotifyId != parties[partyId].queueList.head.getData().spotifyId):
                    parties[partyId].queueList.skipUntilMatch(currentSpotifyId)
                #else:
                    #if this song is moved up before and spotify tries to play again, skip it
                #    spotify.next_track(device_id = parties[partyId].deviceId)
                parties[partyId].currentMs = str(results['progress_ms'])
                parties[partyId].songDuration = currentSpotifyDuration
        return jsonify(response = "Success: Queuelist returned.", currentMS=parties[partyId].currentMs, songDuration=parties[partyId].songDuration,  queueList = parties[partyId].queueList.toArray(), requestId="12")
    else:
        return jsonify(response ="Failure: NO SUCH PARTY", requestId="12")

@app.route('/frontendTest', methods = ['POST'])
def frontendTest():
    '''
    Required body in JSON
    {
        "payload" :"payload"
    }
    Method frontendTest() allows to Frontend team to perform Unit Test for HTTP Client
    1) Receives POST request and gets json data: testPayload
    2) Return testPayload if not empty
    3) If empty, return NOK
    '''
    # get POST data
    postData = request.get_json()
    try:
        testString = postData['testPayload']
    except:
        return jsonify( testResult = "NOK", testPayload = "Payload empty", requestId="13")
    #check party exists
    return jsonify( testResult = "OK", testPayload = testString, requestId="13")
    
    
if __name__ == '__main__':
    app.run(debug=True)
