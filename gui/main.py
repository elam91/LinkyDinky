import flet as ft
from flet import Colors, Icons
import json
import sys
import os

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from gui.components.config_form import create_config_form
from gui.components.tag_input import create_tag_input
from gui.components.console_view import create_console_view
from gui.components.cookie_manager import create_cookie_manager
from gui.bot_runner import BotRunner

def main(page: ft.Page):
    page.title = "LinkyDinky - LinkedIn Automation Bot"
    page.window.width = 1400
    page.window.height = 800
    page.padding = 20
    
    config_path = os.path.join(BASE_DIR, "config/config.json")
    cookies_path = os.path.join(BASE_DIR, "cookies")
    
    bot_runner = None
    status_text = ft.Text("Status: Idle", size=16, weight=ft.FontWeight.BOLD)
    start_button = None
    stop_button = None
    
    def get_path(relative_path):
        return os.path.join(BASE_DIR, relative_path)
    
    def load_json(path):
        try:
            full_path = get_path(path) if not os.path.isabs(path) else path
            with open(full_path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_json(path, data):
        full_path = get_path(path) if not os.path.isabs(path) else path
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def on_config_saved():
        console.add_log("Configuration saved successfully!")
    
    console = create_console_view()
    
    def update_status(status):
        status_map = {
            "idle": ("Idle", Colors.GREY),
            "running": ("Running", Colors.GREEN),
            "stopped": ("Stopped", Colors.RED),
        }
        text, color = status_map.get(status, ("Unknown", Colors.GREY))
        status_text.value = f"Status: {text}"
        status_text.color = color
        
        start_button.disabled = (status == "running")
        stop_button.disabled = (status != "running")
        
        page.update()
    
    def on_start_click(e):
        keyword = keyword_input.value.strip() if keyword_input.value else None
        script = script_dropdown.value
        if keyword:
            console.add_log(f"Starting {script} with keyword: {keyword}")
        else:
            console.add_log(f"Starting {script} with default keywords from config")
        bot_runner.start(script=script, keyword=keyword)
    
    def on_stop_click(e):
        console.add_log("Stop button clicked")
        bot_runner.stop()
    
    bot_runner = BotRunner(
        on_log_callback=console.add_log,
        on_status_change=update_status
    )
    
    config_form = create_config_form(config_path, page, cookies_path=cookies_path, on_save=on_config_saved)
    
    def on_cookies_changed(users):
        config_form.refresh_user_dropdown(users)
    
    cookie_manager = create_cookie_manager(cookies_path, page, on_cookies_changed=on_cookies_changed)
    
    keywords_keep = load_json("config/keywordskeep.json")
    keywords_keep_input = create_tag_input(
        "Keywords Keep",
        keywords_keep,
        on_change=lambda items: save_json("config/keywordskeep.json", items)
    )
    
    blacklist = load_json("config/blacklist.json")
    blacklist_input = create_tag_input(
        "Title Blacklist",
        blacklist,
        on_change=lambda items: save_json("config/blacklist.json", items)
    )
    
    name_blacklist = load_json("config/nameblacklist.json")
    name_blacklist_input = create_tag_input(
        "Name Blacklist",
        name_blacklist,
        on_change=lambda items: save_json("config/nameblacklist.json", items)
    )
    
    mandatory = load_json("config/mandatory.json")
    mandatory_input = create_tag_input(
        "Mandatory Keywords",
        mandatory,
        on_change=lambda items: save_json("config/mandatory.json", items)
    )
    
    currentwork = load_json("config/currentworkblacklist.json")
    position_blacklist = currentwork.get("position", [])
    employer_blacklist = currentwork.get("employer", [])
    
    def save_currentwork_position(items):
        currentwork["position"] = items
        save_json("config/currentworkblacklist.json", currentwork)
    
    def save_currentwork_employer(items):
        currentwork["employer"] = items
        save_json("config/currentworkblacklist.json", currentwork)
    
    position_blacklist_input = create_tag_input(
        "Current Position Blacklist",
        position_blacklist,
        on_change=save_currentwork_position
    )
    
    employer_blacklist_input = create_tag_input(
        "Current Employer Blacklist",
        employer_blacklist,
        on_change=save_currentwork_employer
    )
    
    script_descriptions = {
        "request_minimum": "Sends connection requests until minimum daily quota is reached",
        "request_loops": "Sends connection requests for a fixed number of loops",
        "withdraw_requests": "Withdraws pending invitations older than 1 month",
        "old_connects": "Re-engage existing connections you've messaged before",
        "unmessaged_connects": "Find connections you've never messaged and open their profiles",
        "search_first_names": "Collect first names for translation (Hebrew messages)",
        "scheduler": "Run connection requests on a daily schedule",
    }
    
    script_description_text = ft.Text(
        script_descriptions["request_minimum"],
        size=12,
        italic=True,
        color=Colors.GREY_700,
    )
    
    def on_script_change(e):
        script_description_text.value = script_descriptions.get(script_dropdown.value, "")
        script_description_text.update()
    
    script_dropdown = ft.Dropdown(
        label="Script to Run",
        value="request_minimum",
        on_change=on_script_change,
        options=[
            ft.dropdown.Option("request_minimum", "Send Requests (Until Minimum)"),
            ft.dropdown.Option("request_loops", "Send Requests (Fixed Loops)"),
            ft.dropdown.Option("withdraw_requests", "Withdraw Old Invitations"),
            ft.dropdown.Option("old_connects", "Re-engage Old Connections"),
            ft.dropdown.Option("unmessaged_connects", "Message Unmessaged Connections"),
            ft.dropdown.Option("search_first_names", "Collect Names for Translation"),
            ft.dropdown.Option("scheduler", "Scheduled Daily Run"),
        ],
        width=400,
    )
    
    keyword_input = ft.TextField(
        label="Custom Keyword (optional)",
        hint_text="Leave empty to use keywords from config",
    )
    
    start_button = ft.ElevatedButton(
        "Start Bot",
        icon=Icons.PLAY_ARROW,
        on_click=on_start_click,
        bgcolor=Colors.GREEN,
        color=Colors.WHITE,
    )
    
    stop_button = ft.ElevatedButton(
        "Stop Bot",
        icon=Icons.STOP,
        on_click=on_stop_click,
        bgcolor=Colors.RED,
        color=Colors.WHITE,
        disabled=True,
    )
    
    left_panel = ft.Container(
        content=ft.Column(
            [
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                cookie_manager,
                ft.Divider(),
                config_form,
                ft.Divider(),
                keywords_keep_input,
                ft.Container(height=10),
                blacklist_input,
                ft.Container(height=10),
                name_blacklist_input,
                ft.Container(height=10),
                mandatory_input,
                ft.Container(height=10),
                position_blacklist_input,
                ft.Container(height=10),
                employer_blacklist_input,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        ),
        expand=True,
        padding=10,
    )
    
    right_panel = ft.Container(
        content=ft.Column(
            [
                ft.Text("Bot Control", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                script_dropdown,
                script_description_text,
                ft.Container(height=10),
                keyword_input,
                ft.Container(height=10),
                ft.Row(
                    [
                        start_button,
                        stop_button,
                    ],
                    spacing=10,
                ),
                ft.Container(height=5),
                status_text,
                ft.Container(height=20),
                console,
            ],
            spacing=10,
            expand=True,
        ),
        expand=True,
        padding=10,
    )
    
    save_settings_button = ft.ElevatedButton(
        "Save All Settings",
        icon=Icons.SAVE,
        on_click=config_form.save_config,
        bgcolor=Colors.BLUE,
        color=Colors.WHITE,
    )
    
    page.add(
        ft.Row(
            [
                ft.Text("LinkyDinky Automation Bot", size=28, weight=ft.FontWeight.BOLD),
                save_settings_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        ft.Divider(),
        ft.Row(
            [
                left_panel,
                ft.VerticalDivider(),
                right_panel,
            ],
            expand=True,
            spacing=10,
        ),
    )
    
    console.add_log("LinkyDinky GUI initialized successfully!")
    console.add_log("Configure your settings on the left and click 'Save All Settings' to save")

if __name__ == "__main__":
    ft.app(target=main)
