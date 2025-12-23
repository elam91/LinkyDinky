import flet as ft
from flet import Colors, Icons
from datetime import datetime

def create_console_view():
    log_text = ft.TextField(
        value="",
        multiline=True,
        read_only=True,
        min_lines=10,
        max_lines=15,
        expand=True,
        border_color=Colors.OUTLINE,
    )
    
    def add_log(message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        log_text.value += log_line
        log_text.update()
    
    def clear_logs(e=None):
        log_text.value = ""
        log_text.update()
    
    container = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Console Output", size=18, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=Icons.CLEAR_ALL,
                            tooltip="Clear console",
                            on_click=clear_logs,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                log_text,
            ],
            spacing=10,
        ),
        padding=10,
        border=ft.border.all(1, Colors.OUTLINE),
        border_radius=5,
    )
    
    container.add_log = add_log
    container.clear_logs = clear_logs
    
    return container
