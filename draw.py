import dearpygui.dearpygui as dpg


VP_WIDTH = 640
VP_HEIGHT = 480

# Create Vieport, needed for Canvas coordinates
vp = dpg.create_viewport(title='Lines and Circles YO!',
                         width=VP_WIDTH, height=VP_HEIGHT)


with dpg.window(label="Example Window", id=1):
    # draw 10 paralel lines and circles 
    for i in range(10):
        dpg.draw_line((0, i*(VP_HEIGHT/10)), (VP_WIDTH, i*(VP_HEIGHT/10)),
                      color=(255, 255, 255, 255), thickness=2)
        dpg.draw_circle((i*(VP_WIDTH/10), i*(VP_HEIGHT/10)), radius=100)

# Viewport Setup
dpg.setup_dearpygui(viewport=vp)
dpg.show_viewport(vp)
dpg.set_primary_window(1, True)

dpg.start_dearpygui()
from time import sleep
sleep(300)