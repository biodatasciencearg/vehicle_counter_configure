from __future__ import annotations
import dearpygui.dearpygui as dpg
from camera import Camera
from configuration import Configuration
from dataclasses import dataclass, field
import time 
# Custom Library
# globally accessed vars
stored_shapes:dict[str:Shape] = {}
active_drag_points:list[str | int] = []
# configuration object
config = Configuration()

@dataclass()
class Shape:
    # A simple data class to hold all information about a shape
    #   Note: Could have been done with properties, I know

    name:str
    color:list[float] = field(default_factory=lambda:[0.,0.,0.,1.])
    points:list[tuple] = field(default_factory=lambda:[[0.,0.5],[0.5,0.3]])

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

def create_shape(shape_name):
    global stored_shapes
    
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

def read_yaml(sender, app_data, user_data):
    # read filename
    selected_files = app_data['selections']
    filepath = selected_files[list(selected_files)[0]]
    # obtengo los valores del yaml
    config.read_yaml(filepath)
    print(config.data)


def write_yaml(sender, app_data, user_data):
    # read filename
    selected_files = app_data['selections']
    print(app_data)
    filepath = selected_files[list(selected_files)[0]]
    # obtengo los valores del yaml
    config.write_yaml(filepath)
    print(config.data)



def create_Lines():
    global stored_shapes
    create_shape('Automac')
    create_shape('Street')
    print(stored_shapes['Automac'])
    stored_shapes['Automac'].points = config.data['restaurant']['vehicle_counting']['automac_coordinates']
    stored_shapes['Street'].points = config.data['restaurant']['vehicle_counting']['street_coordinates']


def main():
    frame_rate = 20
    dpg.create_context()
    dpg.create_viewport(title='Lines Builder', width=1000, height=800,clear_color=[0.0,0.0,0.0,0.0])

    # instantiate camera
    cam = Camera()
    # get frames from camera.
    int_snap = cam.get_frame()
    # print configuration
    int_snap.get_conf()

    with dpg.texture_registry(show=False):
        dpg.add_raw_texture(int_snap.frame.shape[1]
                            , int_snap.frame.shape[0]
                            , int_snap.texture_data
                            , tag="texture_tag"
                            , format=dpg.mvFormat_Float_rgba)
       

    with dpg.file_dialog(directory_selector=False, show=False, callback=read_yaml , id="file_dialog_id", width=700 ,height=400):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(".yaml", color=(0, 255, 0, 255), custom_text="[YAML]")
    with dpg.file_dialog(directory_selector=False, show=False, callback=write_yaml , id="file_dialog_save", width=700 ,height=400):
        dpg.add_file_extension(".yaml", color=(0, 255, 0, 255), custom_text="[YAML]")
    
    with dpg.window(tag="AutomacWindow"):
        with dpg.group(tag="LytCol2_NewShape", horizontal=True):
            # Col 1 : Plot
            with dpg.plot(label="Drag Lines/Points", height=400, width=600, tag='PlotEditor') as plt_obj:
                dpg.draw_image(texture_tag="texture_tag", pmin=[0, 1], pmax=[1,0],parent='PlotEditor', tag='image')    

            # Col 2 : Shape selector
            with dpg.group(tag="LytCol2"):
                with dpg.group(tag="tablas", horizontal=True):
                    dpg.add_button(
                        tag="BtnCreateShapeAutomac",
                        label="Add Lines",
                        callback=create_Lines
                    )
                    dpg.add_button(label="Load Config File"
                           , callback=lambda: dpg.show_item("file_dialog_id"))
                    dpg.add_button(label="Save Config File"
                           , callback=lambda: dpg.show_item("file_dialog_save"))
            
                # The Shape selection table
                #   Rows are created by the create_shape() function
                with dpg.table(tag="TblShapes", header_row=False):
                    dpg.add_table_column()
                
    dpg.set_primary_window("AutomacWindow", True)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    prev = 0
    
    while dpg.is_dearpygui_running():

        # updating the texture in a while loop the frame rate will be limited to the camera frame rate.
        # commenting out the "ret, frame = vid.read()" line will show the full speed that operations and updating a texture can run at
        time_elapsed = time.time() - prev
        if time_elapsed > 1./frame_rate:
            prev = time.time()
            snap = cam.get_frame()
            texture_data = snap.texture_data
            dpg.set_value("texture_tag", texture_data)
            # to compare to the base example in the open cv tutorials uncomment below
            #cv.imshow('frame', frame)
            dpg.render_dearpygui_frame()

    cam.vid.release()
    #cv.destroyAllWindows() # when using upen cv window "imshow" call this also
    dpg.destroy_context()


if __name__ == '__main__':
    main()