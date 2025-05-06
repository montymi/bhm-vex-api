from enum import Enum, auto

class Endpoints(str, Enum):
    """Enum representing the various endpoints for the events API."""
    
    # Events endpoints
    EVENTS = "/events"
    EVENT = "/events/{id}"
    EVENT_TEAMS = "/events/{id}/teams"
    EVENT_SKILLS = "/events/{id}/skills"
    EVENT_AWARDS = "/events/{id}/awards"
    EVENT_DIVISION_MATCHES = "/events/{id}/divisions/{div}/matches"
    EVENT_DIVISION_FINALIST_RANKINGS = "/events/{id}/divisions/{div}/finalistRankings"
    EVENT_DIVISION_RANKINGS = "/events/{id}/divisions/{div}/rankings"
    
    # Teams endpoints
    TEAMS = "/teams"
    TEAM = "/teams/{id}"
    TEAM_EVENTS = "/teams/{id}/events"
    TEAM_MATCHES = "/teams/{id}/matches"
    TEAM_RANKINGS = "/teams/{id}/rankings"
    TEAM_SKILLS = "/teams/{id}/skills"
    TEAM_AWARDS = "/teams/{id}/awards"
    
    # Programs endpoints
    PROGRAMS = "/programs"
    PROGRAM = "/programs/{id}"
    
    # Seasons endpoints
    SEASONS = "/seasons"
    SEASON = "/seasons/{id}"
    SEASON_EVENTS = "/seasons/{id}/events"
    
    @classmethod
    def get_all_endpoints(cls):
        """Return a list of all endpoint values."""
        return [endpoint.value for endpoint in cls]