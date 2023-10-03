# import necessary libraries
import requests

# create an object to call the API
class PostcodeApi:

    # create initialiser
    def __init__(self):
        self.api = 'https://api.postcodes.io'

    # create a function to check the validity of the input postcode
    def check_validity(self, p):
        
        val = self.api + '/postcodes/' + p + '/validate' # formulate validity endpoint
        result = requests.get(val).json()['result'] # get the request result

        if result == False: # check if the entered postcode is valid
            print(f'Non-valid post code: {p}')
            return None
        
        else:
            return True

    # create a function to check if the postcode is terminated
    def check_termination(self, p):
        
        ter = self.api + '/terminated_postcodes/' + p # formulate termination endpoint
        if requests.get(ter).status_code == 200: # check if the entered postcode is terminated
            print(f'The postcode {p} is terminated.')
            return None
        
        else:
            return True
    
    # create a function to request the postcode info
    def get_pos_info(self, pos):
        
        if self.check_termination(pos): # apply validity check
            if self.check_validity(pos): # apply termination check
            
                q = self.api + '/postcodes/' + pos # formulate the postcode query endpoint

                result = requests.get(q).json()['result'] # collect the result in a JSOnN format

                lat = result['latitude'] # latitude
                lon = result['longitude'] # longtitude
                city = result['admin_district'] # city
                zone = result['parliamentary_constituency'] # zone

                return {'loc' : [lat,lon],  'city' : city, 'zone' : zone} # return the findings
            
    # create a function to request the bulk postcodes info
    def get_bulk_pos_info(self, pos_bulk):
        # Define the URL
        url = self.api + '/postcodes/'

        # Define the JSON payload
        data = {
            "postcodes": pos_bulk
        }

        # Set the headers
        headers = {
            "Content-Type": "application/json"
        }

        # Send the POST request
        response = requests.post(url, json=data, headers=headers)

        # Check the response
        if response.status_code == 200:
            # The request was successful, and you can parse the response JSON
            result = response.json()
            print(result)
        else:
            # Handle the error
            print(f"Error: {response.status_code} - {response.text}")