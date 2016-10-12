from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
from objloader import ObjFile


class Renderer(Widget):
    
    def __init__(self, **kwargs):
        self.lastx = None
        self.lasty = None
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        self.scene = ObjFile(resource_find("luci.obj"))
        super(Renderer, self).__init__(**kwargs)
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        Clock.schedule_interval(self.update_glsl, 1 / 60.)
        self._touches = []

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, *largs):
        asp = self.width / float(self.height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = proj
        self.canvas['diffuse_light'] = (1.0, 1.0, 0.8)
        self.canvas['ambient_light'] = (0.1, 0.1, 0.1)
        
    def setup_scene(self):
        Color(1, 0, 1, 1)
        PushMatrix()
        Translate(0, 0, -3)
        self.rotx = Rotate(0, 0, 1, 0)
        self.roty = Rotate(0, 1, 0, 0)
        m = list(self.scene.objects.values())[0]
        UpdateNormalMatrix()
        self.mesh = Mesh(
            vertices=m.vertices,
            indices=m.indices,
            fmt=m.vertex_format,
            mode='triangles',
        )
        PopMatrix()

    def define_rotate_angle(self, touch):
        x_angle = (touch.dx/self.width)*360
        y_angle = -1*(touch.dy/self.height)*360
        return x_angle, y_angle
    
    def on_touch_down(self, touch):
        touch.grab(self)
        self._touches.append(touch)
        self.tdx = touch.x
        self.tdy = touch.y
        
    def on_touch_up(self, touch):
        touch.ungrab(self)
        self._touches.remove(touch)
        if abs(int(touch.x-self.tdx)) == 0 and abs(int(touch.y-self.tdy)) == 0:
            self.rotx.axis = (1,1,0)
            self.rotx.angle = 165
            self.roty.axis = (1,1,0)
            self.roty.angle = -15
            self.rotx.axis = (0,1,0)
            self.roty.axis = (1,0,0)

    def on_touch_move(self, touch):
        if touch in self._touches and touch.grab_current == self:
            if len(self._touches) == 1:   
                ax, ay = self.define_rotate_angle(touch)
                self.rotx.angle += ax
                self.roty.angle += ay
            self.update_glsl()

class RendererApp(App):
    def build(self):
        return Renderer()

if __name__ == "__main__":
    RendererApp().run()
