from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFabButton
from jnius import autoclass, cast
from android.permissions import request_permissions, Permission
from android.activity import bind

class SpyScreenApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.media_projection = None
        
        # Obtener la Activity y servicios
        self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
        self.Context = autoclass('android.content.Context')
        self.MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')
        self.activity = cast('android.app.Activity', self.PythonActivity.mActivity)
        self.media_projection_manager = self.activity.getSystemService(
            self.Context.MEDIA_PROJECTION_SERVICE
        )

    def start_media_projection(self):
        print("start_media_projection")
        intent = self.media_projection_manager.createScreenCaptureIntent()
        self.activity.startActivityForResult(intent, 1000)

    def on_activity_result(self, request_code, result_code, intent):
        print("on_activity_result")
        print(f"Resultado: {request_code}, {result_code}")
        if request_code == 1000 and result_code == -1:
            self.media_projection = self.media_projection_manager.getMediaProjection(result_code, intent)
            print("Proyección de medios lista!")
        else:
            print("Permiso denegado para captura")

    def take_screenshot(self, *args):
        print("take_screenshot")
        if not self.media_projection:
            print("Primero inicia la proyección")
            return
        
        try:
            ScreenCaptureService = autoclass("org.kivy.android.ScreenCaptureService")
            service = ScreenCaptureService(self.media_projection, self.activity)
            print(service.captureScreenshot())
        except Exception as e:
            print(f"Error: {e}")

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        
        # Vincular el callback de resultados
        bind(on_activity_result=self.on_activity_result)
        
        # Solicitar permisos
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE], self.on_permissions_result)
        
        return MDBoxLayout(
            MDFabButton(
                icon="record-circle",
                size_hint=(1, 1),
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                on_press=self.take_screenshot
            ),
            orientation="vertical"
        )

    def on_permissions_result(self, permissions, grants):
        if all(grants):
            print("Permisos concedidos")
            self.start_media_projection()
        else:
            print("Permisos denegados")

if __name__ == "__main__":
    SpyScreenApp().run()
