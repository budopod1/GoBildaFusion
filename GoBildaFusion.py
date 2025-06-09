import os
import json
import traceback
import subprocess
import adsk.core
import adsk.fusion
# import adsk.cam

app = adsk.core.Application.get()
ui = app.userInterface

btn_id = "InsertGoBildaPart"

handlers = []

def print(*msg, sep=" "):
    ui.messageBox(sep.join(map(str, msg)))

def main():
    insert_panel = ui.activeWorkspace.toolbarPanels.itemById("InsertPanel")

    btn_cmd = ui.commandDefinitions.addButtonDefinition(
        btn_id, "Insert GoBilda Part", 
        "Insert GoBilda parts", ".")
    
    on_created = InsertStartHandler()
    btn_cmd.commandCreated.add(on_created)
    handlers.append(on_created)

    btn_ctrl = insert_panel.controls.addCommand(btn_cmd)

    btn_ctrl.isPromotedByDefault = True
    btn_ctrl.isPromoted = True

class InsertStartHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            event_args = adsk.core.CommandCreatedEventArgs.cast(args)
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
            print(f'Failed:\n{traceback.format_exc()}')


class InsertFinishedHandler(adsk.core.CommandEventHandler):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
    
    def notify(self, args):
        try:
            if self.browser.sendInfoToHTML("a", "a"):
                print("Inserting parts...")

        except Exception:
            print(f'Failed:\n{traceback.format_exc()}')

class DataFromPageHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            event_args = adsk.core.HTMLEventArgs.cast(args)
            data = json.loads(json.loads(event_args.data)["data"])

            for _ in range(data["count"]):
                add_part_by_name(data["sku"])
        except Exception:
            print(f'Failed:\n{traceback.format_exc()}')

def add_part_by_name(name):
    print("ADD THE PART BY THE NAME", name)

def run(_context: str):
    try:
        os.chdir(os.path.dirname(__file__))
        subprocess.run("env -i HOME=\"$HOME\" bash -l -c 'python3 server.py' &", shell=True)
        main()
        adsk.autoTerminate(False)
    except Exception:
        print(f'Failed:\n{traceback.format_exc()}')

def stop(_context: str):
    try:
        btn_cmd = ui.commandDefinitions.itemById(btn_id)
        if btn_cmd:
            btn_cmd.deleteMe()
    except Exception:
        print(f'Failed:\n{traceback.format_exc()}')
