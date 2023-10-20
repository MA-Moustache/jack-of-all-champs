import psutil
import requests
import base64
import json
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk

__author__ = "@MA-M0ustache"

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class ClientData:
    def __init__(self):
        self.isRunning = False
        self.ProcessId = 0
        self.cmdline = ""
        self.RiotPort = 0
        self.RiotToken = ""
        self.ClientPort = 0
        self.ClientToken = ""
        self.Region = ""
        self.GameState = ""
        
def extract_content(str_source, str_start, str_end):
    if str_start in str_source and str_end in str_source:
        start = str_source.index(str_start) + len(str_start)
        end = str_source.index(str_end, start)
        return str_source[start:end]

    return ""


def make_request(info, method, url, client):
    port = info.ClientPort if client else info.RiotPort
    auth_token = info.ClientToken if client else info.RiotToken

    try:
        headers = {'Authorization': f'Basic {auth_token}', 'Content-Type': 'application/json'}
        response = requests.request(method, f'https://127.0.0.1:{port}{url}', headers=headers, verify=False)
        return response.text
    except:
        return ''
        
    
ClientInfo = ClientData()

processes = [process for process in psutil.process_iter() if process.name() == "LeagueClientUx.exe"]
champion_ids_all = [1, 10, 101, 102, 103, 104, 105, 106, 107, 11, 110, 111, 112, 113, 114, 115, 117, 119, 12, 120, 121, 122, 126, 127, 13, 131, 133, 134, 136, 14, 141, 142, 143, 145, 147, 15, 150, 154, 157, 16, 161, 163, 164, 166, 17, 18, 19, 2, 20, 200, 201, 202, 203, 21, 22, 221, 222, 223, 23, 233, 234, 235, 236, 238, 24, 240, 245, 246, 25, 254, 26, 266, 267, 268, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 350, 36, 360, 37, 38, 39, 4, 40, 41, 412, 42, 420, 421, 427, 429, 43, 432, 44, 45, 48, 497, 498, 5, 50, 51, 516, 517, 518, 523, 526, 53, 54, 55, 555, 56, 57, 58, 59, 6, 60, 61, 62, 63, 64, 67, 68, 69, 7, 711, 72, 74, 75, 76, 77, 777, 78, 79, 8, 80, 81, 82, 83, 84, 85, 86, 875, 876, 887, 888, 89, 895, 897, 9, 90, 902, 91, 92, 950, 96, 98, 99]


if len(processes) > 0:
    ClientInfo.isRunning = True
    ClientInfo.ProcessId = processes[0].pid
    if ClientInfo.cmdline == "":
        for process in processes:
            if process.name() == "LeagueClientUx.exe":
            
                ClientInfo.cmdline = process.name() + " [" + ','.join(process.cmdline()) + "]"
                ClientInfo.RiotPort = int(extract_content(ClientInfo.cmdline, "--riotclient-app-port=", "," "--no-rads"))
                ClientInfo.RiotToken = str(base64.b64encode((b"riot:" + extract_content(ClientInfo.cmdline, "--riotclient-auth-token=", "," "--riotclient").encode("ISO-8859-1"))), "utf-8")
                ClientInfo.ClientPort = int(extract_content(ClientInfo.cmdline, "--app-port=", "," "--install"))
                ClientInfo.ClientToken = str(base64.b64encode((b"riot:" + extract_content(ClientInfo.cmdline, "--remoting-auth-token=", "," "--respawn-command=LeagueClient.exe").encode("ISO-8859-1"))), "utf-8")
                ClientInfo.Region = extract_content(make_request(ClientInfo, "GET", "/lol-rso-auth/v1/authorization", True), "currentPlatformId\":\"", "\",\"subject")
                ClientInfo.GameState = make_request(ClientInfo, "GET", "/lol-gameflow/v1/gameflow-phase", True).strip('"')
                
                data_set = json.loads(make_request(ClientInfo, "GET", "/lol-challenges/v1/challenges/local-player", True))
                
                if "401106" in data_set:
                    obj_401106 = data_set["401106"]
                    if "completedIds" in obj_401106:
                        completed_ids_data = obj_401106["completedIds"]
                        champion_ids_filtered = [completed_id for completed_id in champion_ids_all if completed_id not in completed_ids_data]

                base_url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/"

                root = tk.Tk()
                root.title("Icônes des champions")

                frame = tk.Frame(root)
                frame.pack()

                icons_per_row = 10

                row = 0
                col = 0
                
                print("Fetching data...")
                for champion_id in champion_ids_filtered:
                    
                    icon_url = base_url + str(champion_id) + ".png"
                    response = requests.get(icon_url)

                    if response.status_code == 200:
                        img_data = Image.open(BytesIO(response.content))
                        img_data = img_data.resize((img_data.width // 2, img_data.height // 2))

                        img = ImageTk.PhotoImage(img_data)
                        label = tk.Label(frame, image=img)
                        label.photo = img
                        label.grid(row=row, column=col, padx=5, pady=5)

                        col += 1
                        if col >= icons_per_row:
                            col = 0
                            row += 1

                root.mainloop()