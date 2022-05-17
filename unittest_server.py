import unittest
from server import app
import json
import requests

class TestServer(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):        
        self.authToken = "BQB41Ne7o42v3_9D0fo67t-RVVHkIKFaN_xDRoSBHOX5gCLdROHpbWvO8xz1CFAwNjGSUCWv2I7WOCe4nmpz9kUVQ8oe1BTI2OVFEyp-ci734eWMOIxqKbYBLUsEzUP9nWORhLCSMMv6DvoBSZRJRLw7Y-lFw-0iMoXsT4tgsBWY5RoVrsLY_eACJdEYfsYkvrB1kjJbRuN5tMXUdfIpF3ta1PV7zu2JQfc-Sqrb1cIG-8c8ACsN67Q"
        self.partyId=""
        self.headers={"Content-Type": "application/json"}
        self.tester = app.test_client()

    #Success case of party creation
    def test01CreatePartySuccess(self):
        payload = json.dumps({
            "userId": "test",
            "authToken": self.authToken,
            "playlistId": "0fZm7ygIaFLpTX7AEd38WT",
            "partyName" : "TestParty"
        })

        result = self.tester.post('/createParty',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])
        type(self).partyId=result.json['partyId']        
    
    #Fail case of party creation
    def test02CreatePartyFail(self):        
        payload = json.dumps({
            "userId": "test",
            "authToken": "invalid",
            "playlistId":"invalid",
            "partyName":"invalid"
        })

        result = self.tester.post('/createParty',headers=self.headers, data=payload)
        self.assertRaises(requests.exceptions.HTTPError)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])    
   
    #Success case of closing is at the end
    #Fail case of party closing
    def test03ClosePartyFail(self):
        payload = json.dumps({
            "userId": "test",
            "partyId": "invalid"
        })

        result = self.tester.post('/closeParty',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])  

    #Success case of join party
    def test04JoinPartySuccess(self):
        payload = json.dumps({
            "userId": "test2",
            "partyId": self.partyId
        })

        result = self.tester.post('/join',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])

    #Fail case of join party
    def test05JoinPartyFail(self):
        payload = json.dumps({
            "userId": "test2",
            "partyId": "invalid"
        })

        result = self.tester.post('/join',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])  

    #Success case of leave party
    def test06LeavePartySuccess(self):
        payload = json.dumps({
            "userId": "test2",
            "partyId": self.partyId
        })

        result = self.tester.post('/leave',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])

    #Fail case of leave party
    def test07LeavePartyFail(self):
        payload = json.dumps({
            "userId": "invalid",
            "partyId": "invalid"
        })

        result = self.tester.post('/leave',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of Play Song
    def test08PlaySongSuccess(self):
        payload = json.dumps({
            "partyId": self.partyId,
            "songId": "6U3lYxb88LzzRIEjHEVUnr"
        })

        result = self.tester.post('/playSong',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])

    #Fail case of leave party
    def test09PlaySongFail(self):
        payload = json.dumps({
            "songId": "invalid",
            "partyId": "invalid"
        })

        result = self.tester.post('/playSong',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of Search Song
    def test10SearchSongSuccess(self):
        payload = json.dumps({
            "partyId": self.partyId,
            "searchWord": "Love"
        })

        result = self.tester.post('/searchSong',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])
        self.assertEqual(type([]), type(result.json['songs']))

    #Fail case of Search Song
    def test11SearchSongFail(self):
        payload = json.dumps({
            "partyId": "invalid",
            "searchWord": "invalid"
        })

        result = self.tester.post('/searchSong',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of Get Party History  ### 55338 is sample party which has history
    def test12GetPartyHistorySuccess(self):
        payload = json.dumps({
            "partyId": "36972"           
        })

        result = self.tester.post('/getPartyHistory',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])
        self.assertEqual(type([]), type(result.json['songs']))
    
    #Fail case of Get Party History
    def test13GetPartyHistoryFail(self):
        payload = json.dumps({
            "partyId": "invalid"         
        })

        result = self.tester.post('/getPartyHistory',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of Get Playlist
    def test14GetPlaylistsSuccess(self):
        payload = json.dumps({
            "authToken": self.authToken           
        })

        result = self.tester.post('/getPlaylists',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])
        self.assertEqual(type([]), type(result.json['playlists']))

    #Fail case of Get Playlist
    def test15GetPlaylistsFail(self):
        payload = json.dumps({
            "authToken": "invalid"           
        })

        result = self.tester.post('/getPlaylists',headers=self.headers, data=payload)
        self.assertRaises(requests.exceptions.HTTPError)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of Update Token
    def test16UpdateTokenSuccess(self):
        payload = json.dumps({
            "partyId": self.partyId,
            "authToken": self.authToken           
        })

        result = self.tester.post('/updateToken',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])

    #Fail case of Update Token
    def test17UpdateTokenFail(self):
        payload = json.dumps({
            "partyId": "invalid",
            "authToken": "invalid"           
        })

        result = self.tester.post('/updateToken',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of Add Song to Party
    def test18AddSongSuccess(self):
        payload = json.dumps({
            "partyId": self.partyId,            
            'spotifyId': "5UJmwdqGP7RONuVzYnHjUp",
            'name': "Hey You",
            'album' : 'The Wall',
            'artist' : 'Pink Floyd',
            'imgUrl' : 'https://i.scdn.co/image/ab67616d0000b2733e6b6b961dbe279540b72cb5'
            })

        result = self.tester.post('/addSong', headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])

    #Fail case of Add song
    def test19AddSongFail(self):
        payload = json.dumps({
            "partyId": "invalid",            
            'spotifyId': "invalid",
            'name': "invalid",
            'album' : 'invalid',
            'artist' : 'invalid',
            'imgUrl' : 'invalid'
            })

        result = self.tester.post('/addSong',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of Skip Song
    def test20SkipSongSuccess(self):
        payload = json.dumps({
            "partyId": self.partyId,            
            'userId': "test"
            })

        result = self.tester.post('/skipSong', headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])

    #Fail case of Skip Song
    def test21SkipSongFail(self):
        payload = json.dumps({
            "partyId": self.partyId,            
            'userId': "invalid"
            })

        result = self.tester.post('/skipSong',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of Skip Song
    def test22SetNextSongSuccess(self):
        payload = json.dumps({
            "partyId": self.partyId,            
            'songId': "73SpzrcaHk0RQPFP73vqVR"
            })

        result = self.tester.post('/setNextSong', headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])
        self.assertEqual(type([]), type(result.json['queueList']))
        

    #Fail case of Set next Song
    def test23SetNextSongFail(self):
        payload = json.dumps({
            "partyId": "invalid",            
            'songId': "invalid"
            })

        result = self.tester.post('/setNextSong',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of getQueueList
    def test24GetQueueListSuccess(self):
        payload = json.dumps({
            "partyId": self.partyId  
            })

        result = self.tester.post('/getQueueList', headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])
        self.assertEqual(type([]), type(result.json['queueList']))

    #Fail case of Skip Song
    def test25GetQueueListFail(self):
        payload = json.dumps({
            "partyId": "invalid"           
            })

        result = self.tester.post('/getQueueList',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Failure", result.json['response'])

    #Success case of party closing
    def test99ClosePartySuccess(self):
        payload = json.dumps({
            "userId": "test",
            "partyId": self.partyId
        })

        result = self.tester.post('/closeParty',headers=self.headers, data=payload)
        self.assertEqual(200, result.status_code)
        self.assertIn("Success", result.json['response'])     


if __name__ == "__main__":           
    unittest.main()