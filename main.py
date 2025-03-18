import time
import threading
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button.button import MDFabButton

from jnius import autoclass, cast
from android.permissions import request_permissions, Permission
from android import activity

# Solicitar permisos necesarios
request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.CAPTURE_VIDEO_OUTPUT])

class SpyScreenApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.media_projection = None
        self.media_projection_manager = None
        self.request_code = 100  # Código de solicitud para MediaProjection

    def on_start(self):
        # Inicializar MediaProjectionManager
        self.initialize_media_projection_manager()

    def initialize_media_projection_manager(self):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.activity = PythonActivity.mActivity
            Context = autoclass('android.content.Context')
            self.media_projection_manager = cast(
                'android.media.projection.MediaProjectionManager',
                self.activity.getSystemService(Context.MEDIA_PROJECTION_SERVICE)
            )
        except Exception as e:
            print(f"Error al inicializar MediaProjectionManager: {e}")

    def request_media_projection(self):
        if self.media_projection_manager is None:
            print("MediaProjectionManager no está inicializado")
            return

        try:
            # Crear el intent para solicitar MediaProjection
            intent = self.media_projection_manager.createScreenCaptureIntent()
            self.activity.startActivityForResult(intent, self.request_code)
        except Exception as e:
            print(f"Error al solicitar MediaProjection: {e}")

    def on_activity_result(self, request_code, result_code, intent):
        if request_code == self.request_code:
            try:
                # Obtener el MediaProjection
                self.media_projection = self.media_projection_manager.getMediaProjection(result_code, intent)
                print("MediaProjection obtenido correctamente")
            except Exception as e:
                print(f"Error al obtener MediaProjection: {e}")

    def take_screenshot(self, *args):
        """Captura la pantalla usando el servicio Java"""
        if self.media_projection is None:
            print("MediaProjection no está disponible")
            return

        try:
            ScreenCaptureService = autoclass("org.kivy.android.ScreenCaptureService")
            service = ScreenCaptureService(self.media_projection, self.activity)
            result = service.captureScreenshot()
            print(result)  # Muestra en consola la ruta donde se guardó la imagen
        except Exception as e:
            print(f"Error al capturar la pantalla: {e}")

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"

        return MDBoxLayout(
            MDFabButton(
                icon="record-circle",
                size_hint=(1, 1), pos_hint={"center_x": 0.5, "center_y": 0.5},
                on_press=self.take_screenshot
            ),
            orientation="vertical"
        )

# Registrar el callback para on_activity_result
def on_activity_result(request_code, result_code, intent):
    app = MDApp.get_running_app()
    if app:
        app.on_activity_result(request_code, result_code, intent)

activity.bind(on_activity_result=on_activity_result)

if __name__ == "__main__":
    SpyScreenApp().run()
