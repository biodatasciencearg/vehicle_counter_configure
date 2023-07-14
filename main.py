# ----------------------------------------------------------------------------------------------------------------------
# - Explanation -
# ----------------------------------------------------------------------------------------------------------------------
# This is a "simple" example of how to make a polygon editor in DPG
#   Implemented examples:
#       - Ability to recolor a shape on the fly
#       - By selecting the shape in the table, drag points appear on the plot
#       - Shapes can be editing by dragging drag points
#       - custom painter to have an "unlimited" amount of shapes,
#           instead of an overload of custom series
#
#   Some things that aren't implemented, but that could be useful ideas for people who want to iterate on the idea:
#   (as they are harder to implement, and require more complex math)
#       - Rounded shapes (no clue how to do this, except for making a polygon that has a lot of points)
#       - Central point of the shape (to be dragged around, so the entire shape changes location
#
# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import dearpygui.dearpygui as dpg
from dataclasses import dataclass, field

# Custom Library

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
# globally accessed vars
stored_shapes:dict[str:Shape] = {}
active_drag_points:list[str | int] = []

@dataclass()
class Shape:
    # A simple data class to hold all information about a shape
    #   Note: Could have been done with properties, I know

    name:str
    color:list[float] = field(default_factory=lambda:[0.,0.,0.,1.])
    points:list[tuple] = field(default_factory=lambda:[[0.,0.],[0.,1.],[1.,1.],[1.,0.]])

    def update_color(self, _, app_data):
        #   Colors are notated in a float RGB format,
        #       multiplying the color picker values by 255, as the color picker's values range between 0 and 1
        self.color = [n*255 for n in app_data]

    def update_point(self, sender, _, user_data):
        # The userdata is the index of the point that needs to be updates
        #   Drag points populate 4 values, whilst we only need the x and y coords, therefor the [:2]
        self.points[user_data] = dpg.get_value(sender)[:2]


def select_shape(sender, app_data, user_data):
    global active_drag_points, stored_shapes
    check_box_state = app_data
    selected_shape = user_data

    # Clean up old drag points
    #   Needs to be done in both true or false 'check_box_state'
    for drag_point in active_drag_points:
        dpg.delete_item(drag_point)
    active_drag_points.clear()

    # If the checkbox is deselected, don't need to do anything else.
    #   Safely exit function here
    if not check_box_state:
        return

    # Update the table to only make the current shape selected
    for shape_name, shape in stored_shapes.items(): #type: str, Shape
        if shape_name != selected_shape.name:
            dpg.set_value(item=f"ChkBox_{shape_name}", value=False)

    # Create drag points
    #   Index is stored for easily updating the shape later on
    for index, point in enumerate(selected_shape.points):
        drag_point = dpg.add_drag_point(
            parent="PlotEditor",
            default_value = point,
            user_data = index,
            callback=selected_shape.update_point
        )
        active_drag_points.append(drag_point)

def create_shape():
    global stored_shapes
    shape_name = dpg.get_value("InTxtShapeName")

    # Check if the shape name isn't in the stored shapes
    #   Also check for invalid shape names
    if not shape_name or shape_name is None or shape_name in stored_shapes:
        raise ValueError("No valid shape name was give")

    # Store the shape
    stored_shapes[shape_name] = (new_shape := Shape(name=shape_name))

    # Create the record in the table
    #   A table is used to make selecting the shapes easier
    with dpg.table_row(parent="TblShapes"):
        with dpg.group(horizontal=True):
            dpg.add_checkbox(
                tag=f"ChkBox_{new_shape.name}",
                user_data=new_shape,
                callback=select_shape
            )
            dpg.add_color_edit(
                no_inputs=True,
                callback=new_shape.update_color
            )
            dpg.add_text(default_value=f"| {new_shape.name}")

    # Cleanup
    dpg.set_value(item="InTxtShapeName", value="")

def custom_series_painter(sender,app_data):
    global stored_shapes

    # Because the custom series is made with two points at: [0,0] and [1,1]
    #   an easy calculation can be made to translate the Shape's points to pixelspace
    #   WARNING!
    #       Due to this quick fix of not constantly having to create a series for every shape,
    #       the code becomes unstable the further out you go from 0,0
    x0 = app_data[1][0]
    y0 = app_data[2][0]
    x1 = app_data[1][1]
    y1 = app_data[2][1]

    difference_x = x1 - x0
    difference_y = y1 - y0

    # Add mutex here to solve crashing issue when having to delete a large number of children
    with dpg.mutex():
        # delete old drawn items
        #   else we won't update, but simply append to the old image
        #   adding new layers on top of the drawn pieces
        dpg.delete_item(sender, children_only=True)
        dpg.push_container_stack(sender)

        for shape in stored_shapes.values():
            # Calculate all the points in pixel space
            points_offset = [
                [((x * difference_x) + x0),((y * difference_y) + y0)]
                for x,y in shape.points
            ]
            dpg.draw_polygon(
                points=points_offset,
                color= shape.color[:3],
                fill=shape.color[:3],
                thickness=0
            )

        dpg.configure_item(sender, tooltip=False)
        dpg.pop_container_stack()

def main():
    # Main entry of the function
    dpg.create_context()
    dpg.create_viewport(title="Plot as Shape Editor")

    with dpg.window(tag="PrimaryWindow"):
        with dpg.group(horizontal=True, tag="LytMain"):
            # Col 1 : Plot
            with dpg.group(tag="LytCol1"):
                with dpg.plot(tag="PlotEditor", width=500, height=500):
                    dpg.add_plot_axis(axis=dpg.mvXAxis, tag="PlotAxisX")
                    with dpg.plot_axis(axis=dpg.mvYAxis, tag="PlotAxisY"):
                        dpg.add_custom_series(
                            x= [0.,1.],
                            y= [0.,1.],
                            channel_count=2,
                            callback=custom_series_painter
                        )

            # Col 2 : Shape selector
            with dpg.group(tag="LytCol2"):
                with dpg.group(tag="LytCol2_NewShape", horizontal=True):
                    dpg.add_text("New shape's name")
                    dpg.add_input_text(
                        tag="InTxtShapeName",
                        on_enter=True,
                        callback=create_shape,
                        width=250
                    )
                    dpg.add_button(
                        tag="BtnCreateShape",
                        label="Create",
                        callback=create_shape
                    )

                # The Shape selection table
                #   Rows are created by the create_shape() function
                with dpg.table(tag="TblShapes", header_row=False):
                    dpg.add_table_column()

    dpg.set_primary_window("PrimaryWindow", True)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == '__main__':
    main()