import flet as ft
from flet import Colors, Icons
import json

def create_config_form(config_path: str, page: ft.Page, on_save=None):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    fields = {}
    
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
    
    basic_fields = ['user', 'location', 'chromedriver_path', 'webhook_url']
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
    
    return form_column
