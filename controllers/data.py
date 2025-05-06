import requests
import os
import pprint
from models.endpoints import Endpoints

API_TOKEN = os.getenv("ROBOT_API_KEY")

class RobotEvents:
    BASE_URL = "https://www.robotevents.com/api/v2"

    def __init__(self, api_token=None):
        self.headers = {
            "Authorization": f"Bearer {api_token or API_TOKEN}",
            "Content-Type": "application/json",
        }

    def fetch(self, endpoint: Endpoints, **kwargs):
        """
        Generic fetch function that handles all API requests
        
        Args:
            endpoint: Endpoint object from Endpoints enum
            **kwargs: Additional parameters including:
                - params: Dictionary of query parameters
                - path_params: Dictionary of path parameters (e.g., {id: 123, div: "blue"})
        """
        # Get the endpoint path pattern
        url_pattern = f"{self.BASE_URL}{endpoint.value}"
        
        # Replace any path parameters in the URL
        path_params = kwargs.get('path_params', {})
        try:
            url = url_pattern.format(**path_params) if path_params else url_pattern
        except KeyError as e:
            # Map specific keys based on endpoint 
            if 'team_id' in path_params and str(e) == "'id'":
                # If team_id is provided but the URL expects 'id'
                path_params['id'] = path_params['team_id']
                url = url_pattern.format(**path_params)
            else:
                raise KeyError(f"Missing required path parameter: {e}")
        
        # Extract query params if present
        params = kwargs.get('params', None)
        
        # Make the GET request
        try: 
            response = requests.get(url, headers=self.headers, params=params)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            print(f"ERROR querying {url}:\n{e}")
        except requests.exceptions.HTTPError as e:
            pass
        return 

    def _handle_response(self, response):
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


if __name__ == "__main__":
    controller = RobotEvents()
    
    # Example of getting data for a single team
    # Using a specific team ID (e.g. 1234)
    team_id = 171256
    per_page = 50
    team_data = controller.fetch(
        Endpoints.TEAM_DETAIL, 
        path_params={"team_id": team_id}
    )
    print(f"Team {team_id} details:")
    pprint.pprint(team_data)
    
    # You can also fetch team's events
    team_events = controller.fetch(
        Endpoints.TEAM_EVENTS, 
        path_params={"team_id": team_id},
        params={"per_page": per_page}
    )
    print(f"\nEvents for team {team_id}:")
    pprint.pprint(team_events)