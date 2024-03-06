import requests, time
from pypresence import Presence
from datetime import datetime

CLOCKIFY_API_KEY = ""
WORKSPACE_ID = ""
USER_ID = ""
DISCORD_APPLICATION_ID = ""

RPC = Presence(DISCORD_APPLICATION_ID)
RPC.connect()

def getAllActivities():
    url = f'https://api.clockify.me/api/v1/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries'
    headers = {
        "ContentType": "application/json",
        "X-Api-Key": CLOCKIFY_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
            
        else:
            print(f"Error fetching time activities. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def getSubjectName(PROJECT_ID):
    url = f'https://api.clockify.me/api/v1/workspaces/{WORKSPACE_ID}/projects/{PROJECT_ID}'
    headers = {
        "ContentType": "application/json",
        "X-Api-Key": CLOCKIFY_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None # no subject provided
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def getTaskName(PROJECT_ID, TASK_ID):
    url = f'https://api.clockify.me/api/v1/workspaces/{WORKSPACE_ID}/projects/{PROJECT_ID}/tasks/{TASK_ID}'
    headers = {
        "ContentType": "application/json",
        "X-Api-Key": CLOCKIFY_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None # no task provided
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def formatUtc(UTC):
    duration_str = UTC
    duration_str = duration_str[2:]
    print(duration_str)

    if duration_str == "0S":
        return "0h, 0m"
    
    hours, minutes, seconds = 0, 0, 0
    if 'H' in duration_str:
        hours = duration_str.split("H")[0]
    if 'M' in duration_str:
        minutes = duration_str.split("M")[1].split("S")[0]
    if 'S' in duration_str:
        seconds = duration_str.split("M")[1].split("S")[0]
    return f"{hours}h, {minutes}m, {seconds}s"

while True:
    activities = getAllActivities()
    if activities:
        found = False
        for entry in activities:
            if not entry['timeInterval']['end']:
              
                utc = entry['timeInterval']['start']
                utc_timestamp = datetime.strptime(utc, "%Y-%m-%dT%H:%M:%SZ")
                epoch = int((utc_timestamp - datetime(1970, 1, 1)).total_seconds())                
                
                project = getSubjectName(entry['projectId'])
                task = getTaskName(entry['projectId'], entry['taskId'])

                state = "No Subject Provided" # placeholder
                description = "No Description Provided" # placeholder

                if entry['description']:
                    description = entry['description']
                

                if project:
                    project_duration = formatUtc(project['duration'])

                    task_text = ''
                    if task:
                        task_duration = formatUtc(task['duration'])

                        task_text = f"- {task['name']} ({task_duration})"

                    state = f"{project['name']} ({project_duration}) {task_text}"

                RPC.update(details=description, state=state, large_image="clockify", start=epoch, instance=True, large_text='Powered by Clockify')
                found = True
                
        if not found:
            RPC.clear()
                       
    else:
        print("Unable to fetch time activities.")

    time.sleep(15) # can only update rich presence every 15sec
