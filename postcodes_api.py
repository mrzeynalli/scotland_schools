# import necessary libraries
import requests, json

# create an object to call the API
class PosscodeApi:

    # create initialiser
    def __init__(self):
        self.api = 'https://api.postcodes.io'

    # create a function to check the validity of the input postcode
    def check_validity(self, p):
        
        val = self.api + '/postcodes/' + p + '/validate' # formulate validity endpoint
        result = json.loads(requests.get(val).text)['result'] # get the request result

        if result == False: # check if the entered postcode is valid
            print(f'Non-valid post code: {p}')
            return None
        
        else:
            return True

    # create a function to check if the postcode is terminated
    def check_termination(self, p):
        
        ter = self.api + '/terminated_postcodes/' + p # formulate termination endpoint
        ter_json = json.loads(requests.get(ter).text)
        status = ter_json['status'] # get request status

        if status == 200: # check if the entered postcode is terminated
            print(f'The postcode {p} is terminated.')
            return None
        
        else:
            return True
    
    # create a function to request the postcode info
    def get_pos_info(self, pos):
        
        if self.check_termination(pos): # apply validity check
            if self.check_validity(pos): # apply termination check
            
                q = self.api + '/postcodes/' + pos # formulate the postcode query endpoint

                result = json.loads(requests.get(q).text)['result'] # collect the result in a JSOnN format

                lat = result['latitude'] # latitude
                lon = result['longitude'] # longtitude
                city = result['admin_district'] # city
                zone = result['parliamentary_constituency'] # zone

                return {'loc' : [lat,lon],  'city' : city, 'zone' : zone} # return the findings