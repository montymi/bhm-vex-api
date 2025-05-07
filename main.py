from controllers.data import RobotEvents
from models.endpoints import Endpoints
from models.teams import Teams
from models.seasons import Seasons
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
import csv
import io


def main():
    controller = RobotEvents()
    console = Console()

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

    # Find the 2025 season ID
    current_season_id = None
    console.print("[bold]Filtering for 2025 season data only[/bold]")
    
    # Try to find the 2025 season in the Seasons enum
    try:
        # First look for a season specifically named "2025"
        current_season_id = Seasons["2025"].value
        console.print(f"Using 2025 season (ID: {current_season_id})")
    except KeyError:
        # Try to find a season that contains "2025" in its name
        for season in Seasons:
            if "2025" in season.name:
                current_season_id = season.value
                console.print(f"Using {season.name} season (ID: {current_season_id})")
                break
        
        if current_season_id is None:
            # If we still don't have a 2025 season, prompt the user
            console.print("[yellow]Could not automatically identify the 2025 season. Please select it manually.[/yellow]")
            season_name = prompt(
                "Enter the 2025 season name (use tab for suggestions): ",
                completer=season_completer,
            )
            try:
                current_season_id = Seasons[season_name].value
            except KeyError:
                console.print(f"[red]Invalid season: {season_name}[/red]")
                return

    # Ask user what to query
    endpoint_choice = prompt(
        "What would you like to query?: ", completer=endpoint_completer
    )

    if endpoint_choice not in available_endpoints:
        console.print(f"[red]Invalid endpoint: {endpoint_choice}[/red]")
        return

    # Get team ID if needed
    team_ids = []
    if any(
        word in endpoint_choice
        for word in [
            "team",
            "team_events",
            "team_matches",
            "team_rankings",
            "team_skills",
            "team_awards",
        ]
    ):
        team_input_method = prompt(
            "Enter 'names' for team names or 'ids' for direct IDs: "
        )
        
        if team_input_method.lower() == 'names':
            team_names_input = prompt(
                "Enter team(s) (comma-separated, use tab for suggestions, or leave empty for none): ",
                completer=team_completer,
            )
            
            if team_names_input:
                team_names = [name.strip() for name in team_names_input.split(',')]
                
                for team_name in team_names:
                    try:
                        team_ids.append(Teams[team_name].value)
                    except KeyError:
                        console.print(f"[red]Invalid team: {team_name}[/red]")
                        return
        
        elif team_input_method.lower() == 'ids':
            team_ids_input = prompt(
                "Enter team ID(s) (comma-separated, or leave empty for none): "
            )
            
            if team_ids_input:
                # Parse the comma-separated list of IDs
                try:
                    team_ids = [int(id.strip()) for id in team_ids_input.split(',')]
                except ValueError:
                    console.print("[red]Invalid team ID format. Please enter numeric IDs separated by commas.[/red]")
                    return
        
        else:
            console.print("[red]Invalid input method. Please enter 'names' or 'ids'.[/red]")
            return

    # Get event ID if needed
    event_id = None
    if any(
        word in endpoint_choice
        for word in [
            "event",
            "event_teams",
            "event_skills",
            "event_awards",
            "event_division_matches",
            "event_division_finalist_rankings",
            "event_division_rankings",
        ]
    ):
        # For event-related endpoints, offer to list 2025 events first
        show_events = prompt("Would you like to see a list of 2025 events first? (y/n): ")
        
        if show_events.lower() == 'y':
            events_result = controller.fetch(
                Endpoints.EVENTS,
                params={"season": [current_season_id], "per_page": 50}
            )
            
            if isinstance(events_result, dict) and "data" in events_result:
                event_data = events_result["data"]
                if event_data:
                    events_table = Table(title="2025 Events")
                    events_table.add_column("ID")
                    events_table.add_column("Name")
                    events_table.add_column("Location")
                    events_table.add_column("Start")
                    
                    for event in event_data:
                        events_table.add_row(
                            str(event.get("id", "")),
                            str(event.get("name", "")),
                            f"{event.get('location', {}).get('city', '')}, {event.get('location', {}).get('region', '')}",
                            str(event.get("start", ""))
                        )
                    
                    console.print(events_table)
        
        event_id = prompt("Enter event ID (or leave empty for none): ")
        if event_id:
            try:
                event_id = int(event_id)
            except ValueError:
                console.print("[red]Invalid event ID. Please enter a numeric ID.[/red]")
                return

    # Additional parameters based on endpoint
    params = {"season": [current_season_id]}  # Always include the 2025 season filter

    per_page = int(prompt("Results per page: ", default="50"))
    params["per_page"] = per_page
    
    # Function to fetch data for a single team
    def fetch_team_data(team_id):
        # Initialize path_params for this team
        team_path_params = {}
        if team_id is not None and "team" in endpoint_choice:
            team_path_params["id"] = team_id
        if current_season_id is not None and "season" in endpoint_choice:
            team_path_params["id"] = current_season_id
        if event_id is not None and "event" in endpoint_choice:
            team_path_params["id"] = event_id
            
        # Special handling for different endpoints to ensure season filtering
        endpoint_params = params.copy()
        
        # Make sure season filter is applied correctly based on endpoint
        if endpoint_choice == "team_events":
            # For team_events, we can directly filter by season
            endpoint_params["season"] = [current_season_id]
        elif endpoint_choice == "team_matches":
            # For team_matches, we need to get events from the 2025 season first
            # and then filter the matches based on those events
            if "season_events" not in endpoint_params:
                # First get all 2025 events for this team
                events_result = controller.fetch(
                    Endpoints.TEAM_EVENTS,
                    path_params={"id": team_id},
                    params={"season": [current_season_id], "per_page": 100}
                )
                
                if isinstance(events_result, dict) and "data" in events_result:
                    event_data = events_result["data"]
                    if event_data:
                        # Get event IDs
                        event_ids = [event["id"] for event in event_data]
                        endpoint_params["event"] = event_ids
        
        # Fetch the data for this team with appropriate filtering
        return controller.fetch(
            available_endpoints[endpoint_choice],
            path_params=team_path_params,
            params=endpoint_params,
        )
    
    # If we have team IDs, fetch data for each team and concatenate the results
    if team_ids and "team" in endpoint_choice:
        console.print(f"\n[bold]Fetching 2025 season data for {len(team_ids)} teams...[/bold]")
        
        # Initialize the combined result
        combined_result = None
        
        # Process each team ID
        for i, team_id in enumerate(team_ids):
            console.print(f"Processing team ID {team_id} ({i+1}/{len(team_ids)})...")
            
            # Fetch data for this team
            result = fetch_team_data(team_id)
            
            # Initialize combined_result with the structure of the first result
            if combined_result is None:
                if isinstance(result, dict) and "data" in result:
                    combined_result = {"data": [], "meta": result.get("meta", {})}
                else:
                    combined_result = []
            
            # Add this team's data to the combined result
            if isinstance(result, dict) and "data" in result:
                if isinstance(result["data"], list):
                    # For list data, merge all items together
                    for item in result["data"]:
                        # Ensure each item has a team_id field if not already present
                        if "team_id" not in item and endpoint_choice != "team":
                            item["team_id"] = team_id
                        combined_result["data"].append(item)
                else:
                    # For non-list data, add as a single item with team_id
                    item = result["data"]
                    if "team_id" not in item:
                        item["team_id"] = team_id
                    combined_result["data"].append(item)
            elif isinstance(result, list):
                # For list results, merge all items
                for item in result:
                    if isinstance(item, dict) and "team_id" not in item:
                        item["team_id"] = team_id
                    combined_result.append(item)
            else:
                # If it's neither a dict with data nor a list, print a warning
                console.print(f"[yellow]Warning: Unexpected result format for team {team_id}[/yellow]")
        
        # Use the combined result for display
        result = combined_result
    else:
        # For non-team queries or single teams, fetch data normally
        console.print("\n[bold]Fetching 2025 season data...[/bold]")
        
        if team_ids:
            result = fetch_team_data(team_ids[0])
        else:
            # For non-team endpoints
            path_params = {}
            if current_season_id is not None and "season" in endpoint_choice:
                path_params["id"] = current_season_id
            if event_id is not None and "event" in endpoint_choice:
                path_params["id"] = event_id
                
            result = controller.fetch(
                available_endpoints[endpoint_choice],
                path_params=path_params,
                params=params,
            )

    # Display results in a formatted panel
    console.print(f"\n[bold green]Results for {endpoint_choice} (2025 season only):[/bold green]")

    # Check if result has a data field (common API response format)
    if isinstance(result, dict) and "data" in result:
        data = result["data"]

        if isinstance(data, dict):
            # For single object responses within data field
            panel_content = ""
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    panel_content += f"[bold]{key}[/bold]: {len(value)} items\n"
                else:
                    panel_content += f"[bold]{key}[/bold]: {value}\n"
            console.print(
                Panel(
                    panel_content,
                    title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()} (2025 Season)[/bold blue]",
                )
            )

        elif isinstance(data, list):
            # For list responses within data field
            if data:
                console.print(f"[green]Found {len(data)} results for 2025 season[/green]")
                
                if isinstance(data[0], dict):
                    # Create a table with columns based on the first item's keys
                    table = Table(title=f"{endpoint_choice.replace('_', ' ').title()} (2025 Season)")

                    # Use all available keys
                    all_keys = list(data[0].keys())

                    for key in all_keys:
                        table.add_column(
                            str(key).replace("_", " ").title(), overflow="fold"
                        )

                    # Add rows (limit to 20 for display)
                    display_count = min(20, len(data))
                    for item in data[:display_count]:
                        table.add_row(*[str(item.get(key, "")) for key in all_keys])

                    console.print(table)
                    if len(data) > 20:
                        console.print(f"[italic](Showing 20 of {len(data)} results)[/italic]")

                    # Convert data to CSV format
                    output = io.StringIO()
                    csv_writer = csv.writer(output)
                    if data:
                        # Write header
                        csv_writer.writerow(data[0].keys())
                        # Write rows
                        for row in data:
                            csv_writer.writerow(row.values())

                    console.print("\n[bold]CSV Output (2025 Season):[/bold]")
                    console.print(output.getvalue())
                    output.close()
                else:
                    # Simple list display if not dict items
                    console.print(
                        Panel(
                            str(data),
                            title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()} (2025 Season)[/bold blue]",
                        )
                    )
            else:
                console.print("[yellow]No data found for the 2025 season with these parameters.[/yellow]")
    elif isinstance(result, dict):
        # For single object responses (without data field)
        panel_content = ""
        for key, value in result.items():
            if key != "meta":  # Skip meta information in the panel
                if isinstance(value, (dict, list)):
                    panel_content += f"[bold]{key}[/bold]: {len(value)} items\n"
                else:
                    panel_content += f"[bold]{key}[/bold]: {value}\n"
        console.print(
            Panel(
                panel_content,
                title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()} (2025 Season)[/bold blue]",
            )
        )

    elif isinstance(result, list):
        # For list responses
        if result:
            console.print(f"[green]Found {len(result)} results for 2025 season[/green]")
            
            if isinstance(result[0], dict):
                # Create a table with columns based on the first item's keys
                table = Table(title=f"{endpoint_choice.replace('_', ' ').title()} (2025 Season)")

                # Use all available keys
                all_keys = list(result[0].keys())

                for key in all_keys:
                    table.add_column(str(key).replace("_", " ").title(), overflow="fold")

                # Add rows (limit to 20 for display)
                display_count = min(20, len(result))
                for item in result[:display_count]:
                    table.add_row(*[str(item.get(key, "")) for key in all_keys])

                console.print(table)
                if len(result) > 20:
                    console.print(f"[italic](Showing 20 of {len(result)} results)[/italic]")
                
                # Convert data to CSV format
                output = io.StringIO()
                csv_writer = csv.writer(output)
                if result:
                    # Write header
                    csv_writer.writerow(result[0].keys())
                    # Write rows
                    for row in result:
                        csv_writer.writerow(row.values())

                console.print("\n[bold]CSV Output (2025 Season):[/bold]")
                console.print(output.getvalue())
            else:
                # Simple list display if not dict items
                console.print(
                    Panel(
                        str(result),
                        title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()} (2025 Season)[/bold blue]",
                    )
                )
        else:
            console.print("[yellow]No data found for the 2025 season with these parameters.[/yellow]")
    else:
        # Fallback for other types
        console.print(
            Panel(
                str(result),
                title=f"[bold blue]{endpoint_choice.replace('_', ' ').title()} (2025 Season)[/bold blue]",
            )
        )


if __name__ == "__main__":
    main()