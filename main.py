from controllers.data import RobotEvents
from models.endpoints import Endpoints
from models.teams import Teams
from models.seasons import Seasons
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
  
def main():
    controller = RobotEvents()
        
    # Define available endpoints for the user to select
    available_endpoints = {
        "team": Endpoints.TEAM,
        "team_events": Endpoints.TEAM_EVENTS,
        "team_matches": Endpoints.TEAM_MATCHES,
        "team_rankings": Endpoints.TEAM_RANKINGS,
        "team_skills": Endpoints.TEAM_SKILLS,
        "team_awards": Endpoints.TEAM_AWARDS,
        "events": Endpoints.EVENTS,
        "event": Endpoints.EVENT,
        "event_teams": Endpoints.EVENT_TEAMS,
        "event_skills": Endpoints.EVENT_SKILLS,
        "event_awards": Endpoints.EVENT_AWARDS,
        "event_division_matches": Endpoints.EVENT_DIVISION_MATCHES,
        "event_division_finalist_rankings": Endpoints.EVENT_DIVISION_FINALIST_RANKINGS,
        "event_division_rankings": Endpoints.EVENT_DIVISION_RANKINGS,
        "teams": Endpoints.TEAMS,
        "programs": Endpoints.PROGRAMS,
        "program": Endpoints.PROGRAM,
        "seasons": Endpoints.SEASONS,
        "season": Endpoints.SEASON,
        "season_events": Endpoints.SEASON_EVENTS,
    }
        
    # Create completers for the prompt
    endpoint_completer = WordCompleter(list(available_endpoints.keys()))
    team_completer = WordCompleter([t.name for t in Teams])
    season_completer = WordCompleter([s.name for s in Seasons])
        
    # Ask user what to query
    endpoint_choice = prompt("What would you like to query?: ", 
                            completer=endpoint_completer)
        
    if endpoint_choice not in available_endpoints:
        print(f"Invalid endpoint: {endpoint_choice}")
        return
        
    # Get team ID if needed
    team_id = None
    if any(word in endpoint_choice for word in ['team', 'team_events', 'team_matches', 'team_rankings', 'team_skills', 'team_awards']):
        team_name = prompt("Enter team (use tab for suggestions, or leave empty for none): ", 
                          completer=team_completer)
        if team_name:
            try:
                team_id = Teams[team_name].value
            except KeyError:
                print(f"Invalid team: {team_name}")
                return
    
    # Get season ID if needed
    season_id = None
    if any(word in endpoint_choice for word in ['season', 'season_events']):
        season_name = prompt("Enter season (use tab for suggestions, or leave empty for none): ", 
                           completer=season_completer)
        if season_name:
            try:
                season_id = Seasons[season_name].value
            except KeyError:
                print(f"Invalid season: {season_name}")
                return
    
    # Get event ID if needed
    event_id = None
    if any(word in endpoint_choice for word in ['event', 'event_teams', 'event_skills', 'event_awards', 
                                               'event_division_matches', 'event_division_finalist_rankings', 
                                               'event_division_rankings']):
        event_id = prompt("Enter event ID (or leave empty for none): ")
                
    # Initialize path_params conditionally
    path_params = {}
    if team_id is not None and 'team' in endpoint_choice:
        path_params["id"] = team_id
    if season_id is not None and 'season' in endpoint_choice:
        path_params["id"] = season_id
    if event_id is not None and 'event' in endpoint_choice:
        path_params["id"] = event_id
        
    # Additional parameters based on endpoint
    params = {}
        
    if endpoint_choice == "team_events" and season_id is not None:
        per_page = int(prompt("Results per page: ", default="10"))
        params["per_page"] = per_page
        params["season"] = [season_id]
        
    # Fetch and display the data
    result = controller.fetch(
        available_endpoints[endpoint_choice],
        path_params=path_params,
        params=params if params else None
    )
        
    # Display results in a formatted panel
    
    console = Console()
    
    print(f"\nResults for {endpoint_choice}:")
    
    # Check if result has a data field (common API response format)
    if isinstance(result, dict) and 'data' in result:
        data = result['data']
        
        if isinstance(data, dict):
            # For single object responses within data field
            panel_content = ""
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    panel_content += f"[bold]{key}[/bold]: {len(value)} items\n"
                else:
                    panel_content += f"[bold]{key}[/bold]: {value}\n"
            console.print(Panel(panel_content, title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()}[/bold blue]"))
        
        elif isinstance(data, list):
            # For list responses within data field
            if data and isinstance(data[0], dict):
                # Create a table with columns based on the first item's keys
                table = Table(title=f"{endpoint_choice.replace('_', ' ').title()}")
                
                # Use all available keys
                all_keys = list(data[0].keys())
                
                for key in all_keys:
                    table.add_column(str(key).replace('_', ' ').title(), overflow="fold")
                
                # Add rows
                for item in data[:20]:  # Limit rows for display
                    table.add_row(*[str(item.get(key, "")) for key in all_keys])
                
                console.print(table)
                if len(data) > 20:
                    console.print(f"[italic](Showing 20 of {len(data)} results)[/italic]")
            else:
                # Simple list display if not dict items
                console.print(Panel(str(data), title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()}[/bold blue]"))
    elif isinstance(result, dict):
        # For single object responses (without data field)
        panel_content = ""
        for key, value in result.items():
            if isinstance(value, (dict, list)):
                panel_content += f"[bold]{key}[/bold]: {len(value)} items\n"
            else:
                panel_content += f"[bold]{key}[/bold]: {value}\n"
        console.print(Panel(panel_content, title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()}[/bold blue]"))
    
    elif isinstance(result, list):
        # For list responses
        if result and isinstance(result[0], dict):
            # Create a table with columns based on the first item's keys
            table = Table(title=f"{endpoint_choice.replace('_', ' ').title()}")
            
            # Use all available keys
            all_keys = list(result[0].keys())
            
            for key in all_keys:
                table.add_column(str(key).replace('_', ' ').title(), overflow="fold")
            
            # Add rows
            for item in result[:20]:  # Limit rows for display
                table.add_row(*[str(item.get(key, "")) for key in all_keys])
            
            console.print(table)
            if len(result) > 20:
                console.print(f"[italic](Showing 20 of {len(result)} results)[/italic]")
        else:
            # Simple list display if not dict items
            console.print(Panel(str(result), title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()}[/bold blue]"))
    else:
        # Fallback for other types
        console.print(Panel(str(result), title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()}[/bold blue]"))
  
if __name__ == "__main__":
    main()