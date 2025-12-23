import flet as ft
from flet import Colors, Icons

def create_tag_input(label: str, items: list, on_change=None):
    items_list = items.copy()
    input_field = ft.TextField(
        hint_text=f"Add {label.lower()}...",
        expand=True,
    )
    chips_row = ft.Row(wrap=True, spacing=5, run_spacing=5)
    
    def update_chips():
        chips_row.controls.clear()
        for item in items_list:
            chip = ft.Chip(
                label=ft.Text(item),
                on_delete=lambda e, i=item: remove_item(i),
                delete_icon=ft.Icon(Icons.CLOSE),
            )
            chips_row.controls.append(chip)
        
        if not items_list:
            chips_row.controls.append(
                ft.Text("No items added yet", italic=True, color=Colors.GREY_500)
            )
    
    def add_item(e):
        value = input_field.value.strip()
        if value and value not in items_list:
            items_list.append(value)
            input_field.value = ""
            if on_change:
                on_change(items_list)
            update_chips()
            chips_row.update()
    
    def remove_item(item):
        if item in items_list:
            items_list.remove(item)
            if on_change:
                on_change(items_list)
            update_chips()
            chips_row.update()
    
    input_field.on_submit = add_item
    
    update_chips()
    
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(label, size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        input_field,
                        ft.IconButton(
                            icon=Icons.ADD,
                            tooltip="Add item",
                            on_click=add_item
                        )
                    ]
                ),
                chips_row,
            ],
            spacing=10,
        ),
        padding=10,
        border=ft.border.all(1, Colors.OUTLINE),
        border_radius=5,
    )
