import os
import sys
from pathlib import Path
import json
import traceback
import subprocess
import adsk.core
import adsk.fusion
# import adsk.cam

handlers = []

to_delete = []

def print(*msg, sep=" "):
    ui.messageBox(sep.join(map(str, msg)))

def report_error():
    print(f'Failed:\n{traceback.format_exc()}')

def queue_setup():
    try:
        ui.activeWorkspace
    except Exception:
        on_activated = WorkspaceActivatedHandler()
        ui.workspaceActivated.add(on_activated)
        handlers.append(on_activated)
    else:
        ui_setup()

class WorkspaceActivatedHandler(adsk.core.WorkspaceEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, event_args):
        ui.workspaceActivated.remove(self)
        try:
            ui_setup()
        except Exception:
            report_error()

def ui_setup():
    insert_panel = ui.activeWorkspace.toolbarPanels.itemById("InsertPanel")

    btn_cmd = ui.commandDefinitions.addButtonDefinition(
        "InsertGoBildaPart", "Insert GoBilda Part", 
        "Insert GoBilda parts", ".")
    to_delete.append(btn_cmd)
    
    on_created = InsertStartHandler()
    btn_cmd.commandCreated.add(on_created)
    handlers.append(on_created)

    btn_ctrl = insert_panel.controls.addCommand(btn_cmd)
    to_delete.append(btn_ctrl)

    btn_ctrl.isPromotedByDefault = True
    btn_ctrl.isPromoted = True

class InsertStartHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, event_args):
        try:
            cmd = event_args.command
            inputs = cmd.commandInputs

            browser = inputs.addBrowserCommandInput(
                "browser", "", "http://localhost:7776", 200, 400)

            on_data = DataFromPageHandler()
            cmd.incomingFromHTML.add(on_data)
            handlers.append(on_data)
            
            on_execute = InsertFinishedHandler(browser)
            cmd.execute.add(on_execute)
            handlers.append(on_execute)
        except Exception:
            report_error()

class InsertFinishedHandler(adsk.core.CommandEventHandler):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
    
    def notify(self, event_args):
        try:
            if self.browser.sendInfoToHTML("a", "a"):
                print("Working...")

        except Exception:
            report_error()

class DataFromPageHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, event_args):
        try:
            data = json.loads(json.loads(event_args.data)["data"])

            if not data["sku"]:
                print("No part selected")
                return

            add_part_by_name(data["sku"], data["count"])
        except json.JSONDecodeError:
            pass
        except Exception:
            report_error()

def walk_directory(dir):
    for sub in dir.dataFolders:
        yield from walk_directory(sub)
    for file in dir.dataFiles:
        yield file

def get_gobilda_dir():
    for dir in folder.dataFolders:
        if dir.name == "GoBilda":
            return dir
    return None

def add_part_by_name(name, times):
    target_file = None
    for data_file in walk_directory(get_gobilda_dir() or folder):
        if name not in data_file.name:
            continue
        if target_file is None or len(data_file.name) < len(target_file.name):
            target_file = data_file
    
    if target_file is None:
        print(f"{name} has not been downloaded into this project")
        return

    root = app.activeProduct.rootComponent
    transform = adsk.core.Matrix3D.create()
    for _ in range(times):
        adsk.doEvents()
        root.occurrences.addByInsert(target_file, transform, True)

def start_server():
    os.chdir(os.path.dirname(__file__))
    with open("file.txt", "w") as file:
        file.write("HI!")

def get_python_cmd():
    fusion_dir = Path(sys.executable).parent
    fusion_py = fusion_dir / "Python" / "python.exe"
    if fusion_py.exists():
        return fusion_py
    else:
        return "python3"

def run(_context: str):
    global app, ui, project, folder
    try:
        os.chdir(os.path.dirname(__file__))

        python = get_python_cmd()
        try:
            import flask
            import requests
        except ImportError:
            subprocess.check_call([python, "-m", "pip", "install", "flask", "requests"])
        subprocess.Popen([python, "server.py"], creationflags=subprocess.CREATE_NO_WINDOW)

        app = adsk.core.Application.get()
        ui = app.userInterface
        project = app.data.activeProject
        folder = project.rootFolder

        queue_setup()
        adsk.autoTerminate(False)
    except Exception:
        report_error()

def stop(_context: str):
    try:
        for thing in to_delete:
            thing.deleteMe()
    except Exception:
        report_error()
