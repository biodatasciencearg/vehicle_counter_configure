from __future__ import annotations
import dearpygui.dearpygui as dpg
from src.camera import Camera, Portada
from src.configuration import Configuration
from dataclasses import dataclass, field
import time 
import cv2
import pandas as pd
import ast 

# Custom Library
# globally accessed vars
stored_shapes:dict[str:Shape] = {}
active_drag_points:list[str | int] = []
# configuration object MAI credentials.
config = {'user': 'admin'
          , 'password': 'gesti0narc0s'
          , 'port': 554
          , 'ip': '10.111.58.36'
          , 'acronimo':'MAI'
          , 'country':'AR'
          , 'polygon':{}}

def read_db():
    df = pd.read_csv('./db.csv',sep=';')
    return df

# read database.
df = read_db()

country_list = df.COUNTRY.unique().tolist()
acro_list = df.ACRONIMO.unique().tolist()


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


def create_shape_db(shape_name):
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

def callback_country(sender, filter_string):
    dpg.set_value("filter_country_id", filter_string)

def callback_acro(sender, filter_string):
    dpg.set_value("filter_acro_id", filter_string)

def load_cam(sender, app_data, user_data):
    print(config)
    global df
    global stored_shapes
    try:
        seleccionado = df.loc[(df.ACRONIMO==config['acronimo'])&(df.COUNTRY==config['country'])]
        config['country'] = seleccionado['COUNTRY'].values[0]
        config['user'] = seleccionado['USER'].values[0]
        config['ip'] = seleccionado['IP'].values[0]
        config['password'] = seleccionado['PASSWORD'].values[0]
        config['polygon']= ast.literal_eval(seleccionado['POLYGON'].values[0])
    except ValueError  as e:
        print(e)
    # instantiate camera
    global cam
    cam = Camera(USER=config['user']
            , PASSWORD=config['password']
            , PORT = config['port']
            , IP = config['ip'])
    print
    for name, p in config['polygon'].items():
        create_shape_db(name)
        stored_shapes[name].points = p
        

def write_db(sender, app_data, user_data):
    global df
    global config
    global stored_shapes
    # save coordinates in config variable.
    config['polygon'] = {item.name: item.points for item in stored_shapes.values()}
    # convert dataset into object.
    df_c = df.astype('O')
    if 'POLYGON'  not in df_c.columns:
        df_c['POLYGON'] = ''
    
    # add new data over dataframe.
    df_c.loc[(df_c.COUNTRY==config['country'])\
             &(df_c.ACRONIMO==config['acronimo']),'POLYGON'] = str(config['polygon'])
    # get filename
    filepath = app_data['file_path_name']
    # save new db.
    df_c.to_csv(filepath,sep=';',index=None,quoting =1 )
    print(f"""Saved DB in file: {filepath}""")

def main():
    frame_rate = 20
    dpg.create_context()
    dpg.create_viewport(title='Lines Builder', width=1000, height=600,clear_color=[0.0,0.0,0.0,0.0])
    global cam
    cam = Portada()

    int_snap = cam.get_frame()

    with dpg.theme() as custom_listbox_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0,0)
            dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0, 0.5)


    with dpg.theme() as button_selected_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0,119,200,153))


    with dpg.theme() as button_normal_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 51, 55, 255))


    def custom_listbox_callback_country(sender):
        global config
        config['country'] = dpg.get_item_label(sender)
        for button in dpg.get_item_children(dpg.get_item_parent(sender))[1]:
            dpg.bind_item_theme(button, button_normal_theme)
        dpg.bind_item_theme(sender, button_selected_theme)

    def custom_listbox_callback_acro(sender):
        global config
        config['acronimo'] = dpg.get_item_label(sender)
        for button in dpg.get_item_children(dpg.get_item_parent(sender))[1]:
            dpg.bind_item_theme(button, button_normal_theme)
        dpg.bind_item_theme(sender, button_selected_theme)

    with dpg.texture_registry(show=False):
        dpg.add_raw_texture(int_snap.frame.shape[1]
                            , int_snap.frame.shape[0]
                            , int_snap.texture_data
                            , tag="texture_tag"
                            , format=dpg.mvFormat_Float_rgba)
    

    with dpg.file_dialog(directory_selector=False, show=False, callback=write_db , id="file_dialog_save", width=700 ,height=400):
        dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[csv]")
    
    with dpg.window(tag="AutomacWindow"):
        with dpg.group(tag="plotcontainer", horizontal=True):
            # Col 1 : Plot
            with dpg.plot(label="Drag Lines/Points", height=400, width=600, tag='PlotEditor') as plt_obj:
                dpg.draw_image(texture_tag="texture_tag", pmin=[0, 1], pmax=[1,0],parent='PlotEditor', tag='image')
                dpg.add_plot_axis(axis=dpg.mvXAxis, tag="PlotAxisX")
                with dpg.plot_axis(axis=dpg.mvYAxis, tag="PlotAxisY"):
                    dpg.add_custom_series(
                        x= [0,1],
                        y= [0.,1],
                        channel_count=2,
                        callback=custom_series_painter
                    )    

            # Col 2 : Shape selector
            with dpg.group(tag="Lyt"):
                with dpg.group(tag="save combo", horizontal=True):
                    dpg.add_button(
                        tag="BtnCreateShapeAutomac",
                        label="Load"
                        ,callback=load_cam
                    )
                    dpg.add_button(label="Save Changes"
                           , callback=lambda: dpg.show_item("file_dialog_save"))
                with dpg.group(tag="Select combo", horizontal=True):
                    with dpg.group(tag="select_country", horizontal=False, width=50):
                        dpg.add_input_text(label="Country", callback=callback_country)
                        with dpg.child_window(height=70, width=250, border=False):
                            with dpg.filter_set(id="filter_country_id"):
                                for item in country_list:
                                    dpg.add_button(label=item, width=-1
                                                   , callback=custom_listbox_callback_country, filter_key=item )
                    with dpg.group(tag="select_acro", horizontal=False, width=50):
                        dpg.add_input_text(label="Acro", callback=callback_acro)
                        with dpg.child_window(height=70, width=250, border=False):
                            with dpg.filter_set(id="filter_acro_id"):
                                for item in acro_list:
                                    dpg.add_button(label=item, width=-1
                                                   , callback=custom_listbox_callback_acro, filter_key=item )
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
                
    dpg.set_primary_window("AutomacWindow", True)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    prev = 0
    frame_rate = 10
    while dpg.is_dearpygui_running():
        time_elapsed = time.time() - prev
        if time_elapsed > 1./frame_rate:
            snap = cam.get_frame()
            texture_data = snap.texture_data
            dpg.set_value("texture_tag", texture_data)
            dpg.render_dearpygui_frame()

    cam.vid.release()
    dpg.destroy_context()
if __name__ == '__main__':
    main()