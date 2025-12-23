import flet as ft
from flet import Colors, Icons
import json
import os
import re

def create_cookie_manager(cookies_path: str, page: ft.Page, on_cookies_changed=None):
    
    def get_available_users():
        users = []
        if os.path.exists(cookies_path):
            for filename in os.listdir(cookies_path):
                match = re.match(r'(.+)cookie\.json$', filename)
                if match:
                    users.append(match.group(1))
        return sorted(users)
    
    def refresh_cookie_list():
        users = get_available_users()
        cookie_chips.controls.clear()
        
        if not users:
            cookie_chips.controls.append(
                ft.Text("No cookies found. Add one to get started.", italic=True, color=Colors.GREY_500)
            )
        else:
            for user in users:
                chip = ft.Chip(
                    label=ft.Text(user),
                    on_delete=lambda e, u=user: delete_cookie(u),
                )
                cookie_chips.controls.append(chip)
        
        try:
            cookie_chips.update()
        except:
            pass
        
        if on_cookies_changed:
            on_cookies_changed(users)
    
    def delete_cookie(username):
        cookie_file = os.path.join(cookies_path, f"{username}cookie.json")
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
            refresh_cookie_list()
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Deleted cookie for {username}"), bgcolor=Colors.ORANGE)
            )
    
    def open_add_dialog(e):
        username_field = ft.TextField(
            label="Username",
            hint_text="e.g., johndoe",
            autofocus=True,
        )
        
        cookie_field = ft.TextField(
            label="Cookie JSON",
            hint_text="Paste your cookie JSON here (from EditThisCookie export)",
            multiline=True,
            min_lines=10,
            max_lines=15,
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_cookie(e):
            username = username_field.value.strip().lower()
            cookie_text = cookie_field.value.strip()
            
            if not username:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Please enter a username"), bgcolor=Colors.RED)
                )
                return
            
            if not cookie_text:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Please paste your cookie JSON"), bgcolor=Colors.RED)
                )
                return
            
            try:
                cookie_data = json.loads(cookie_text)
            except json.JSONDecodeError:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Invalid JSON format"), bgcolor=Colors.RED)
                )
                return
            
            os.makedirs(cookies_path, exist_ok=True)
            cookie_file = os.path.join(cookies_path, f"{username}cookie.json")
            
            with open(cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            dialog.open = False
            page.update()
            refresh_cookie_list()
            
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Cookie saved for {username}!"), bgcolor=Colors.GREEN)
            )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Cookie"),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Use EditThisCookie browser extension to export your LinkedIn cookie.",
                            size=12,
                            color=Colors.GREY_600,
                        ),
                        ft.Container(height=10),
                        username_field,
                        ft.Container(height=10),
                        cookie_field,
                    ],
                    tight=True,
                ),
                width=500,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Save Cookie", on_click=save_cookie, bgcolor=Colors.GREEN, color=Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    cookie_chips = ft.Row(
        wrap=True,
        spacing=10,
    )
    
    add_button = ft.ElevatedButton(
        "Add Cookie",
        icon=Icons.ADD,
        on_click=open_add_dialog,
    )
    
    container = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("LinkedIn Cookies", size=16, weight=ft.FontWeight.BOLD),
                    add_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            cookie_chips,
        ],
        spacing=10,
    )
    
    container.refresh = refresh_cookie_list
    container.get_users = get_available_users
    
    refresh_cookie_list()
    
    return container

