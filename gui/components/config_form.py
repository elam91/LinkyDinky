import flet as ft
from flet import Colors, Icons
import json
import os
import re

def create_config_form(config_path: str, page: ft.Page, cookies_path: str = None, on_save=None):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    fields = {}
    user_dropdown = None
    
    def get_available_users():
        users = []
        if cookies_path and os.path.exists(cookies_path):
            for filename in os.listdir(cookies_path):
                match = re.match(r'(.+)cookie\.json$', filename)
                if match:
                    users.append(match.group(1))
        return sorted(users)
    
    def refresh_user_dropdown(users=None):
        if user_dropdown is None:
            return
        if users is None:
            users = get_available_users()
        
        user_dropdown.options = [ft.dropdown.Option(u) for u in users]
        
        if config.get('user') in users:
            user_dropdown.value = config.get('user')
        elif users:
            user_dropdown.value = users[0]
        else:
            user_dropdown.value = None
        
        try:
            user_dropdown.update()
        except:
            pass
    
    def save_config(e=None):
        print(f"Save button clicked! Saving to {config_path}")
        print(f"Fields to save: {list(fields.keys())}")
        
        for key, control in fields.items():
            if isinstance(control, ft.TextField):
                try:
                    config[key] = int(control.value)
                except ValueError:
                    config[key] = control.value
                print(f"  {key} = {config[key]}")
            elif isinstance(control, ft.Switch):
                config[key] = control.value
                print(f"  {key} = {config[key]}")
            elif isinstance(control, ft.Dropdown):
                config[key] = control.value
                print(f"  {key} = {config[key]}")
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Successfully saved to {config_path}")
        except Exception as ex:
            print(f"ERROR saving config: {ex}")
        
        if on_save:
            on_save()
        
        if page:
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Configuration saved!"), bgcolor=Colors.GREEN)
            )
    
    def create_field(key, value):
        if isinstance(value, bool):
            control = ft.Switch(
                label=key.replace('_', ' ').title(),
                value=value,
            )
        elif isinstance(value, int):
            control = ft.TextField(
                label=key.replace('_', ' ').title(),
                value=str(value),
                keyboard_type=ft.KeyboardType.NUMBER,
            )
        elif isinstance(value, list):
            return None
        else:
            control = ft.TextField(
                label=key.replace('_', ' ').title(),
                value=str(value),
            )
        
        fields[key] = control
        return control
    
    form_fields = []
    
    form_fields.append(ft.Text("Basic Settings", size=20, weight=ft.FontWeight.BOLD))
    
    users = get_available_users()
    current_user = config.get('user', '')
    
    user_dropdown = ft.Dropdown(
        label="User",
        options=[ft.dropdown.Option(u) for u in users],
        value=current_user if current_user in users else (users[0] if users else None),
        hint_text="Select a user (add a cookie first)" if not users else None,
    )
    fields['user'] = user_dropdown
    form_fields.append(user_dropdown)
    
    basic_fields = ['location', 'chromedriver_path', 'webhook_url']
    for key in basic_fields:
        if key in config:
            field = create_field(key, config[key])
            if field:
                form_fields.append(field)
    
    form_fields.append(ft.Divider())
    form_fields.append(ft.Text("Connection Settings", size=20, weight=ft.FontWeight.BOLD))
    
    connection_fields = ['connect_amount', 'minimum_daily_connects', 'maximum_daily_connects', 
                        'send_connect_message', 'exact_match']
    for key in connection_fields:
        if key in config:
            field = create_field(key, config[key])
            if field:
                form_fields.append(field)
    
    form_fields.append(ft.Divider())
    form_fields.append(ft.Text("Experience & Loop Settings", size=20, weight=ft.FontWeight.BOLD))
    
    exp_fields = ['minimum_experience', 'maximum_experience', 'loops', 'sleep_between_loops', 
                 'resend_amount', 'withdraw_amount', 'old_connects_loops',
                 'name_collect_amount']
    for key in exp_fields:
        if key in config:
            field = create_field(key, config[key])
            if field:
                form_fields.append(field)
    
    form_fields.append(ft.Divider())
    form_fields.append(ft.Text("Advanced Settings", size=20, weight=ft.FontWeight.BOLD))
    
    advanced_fields = ['delayed_start', 'mandatory_first_word', 
                      'old_connect_month_delta_answered', 'old_connect_month_delta_unanswered']
    for key in advanced_fields:
        if key in config:
            field = create_field(key, config[key])
            if field:
                form_fields.append(field)
    
    form_column = ft.Column(
        form_fields,
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
    )
    
    form_column.save_config = save_config
    form_column.refresh_user_dropdown = refresh_user_dropdown
    
    return form_column
