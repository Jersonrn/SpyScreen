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

request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.CAPTURE_VIDEO_OUTPUT])

class SpyScreenApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.media_projection = None

    def on_start(self):
        # Solicitar MediaProjection
        self.request_media_projection()

    def request_media_projection(self):
        try:
            MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            media_projection_manager = cast('android.media.projection.MediaProjectionManager',
                                            activity.getSystemService(autoclass('android.content.Context').MEDIA_PROJECTION_SERVICE))
            intent = media_projection_manager.createScreenCaptureIntent()
            activity.startActivityForResult(intent, 1)
        except Exception as e:
            print(f"Error al solicitar MediaProjection: {e}")

    def on_activity_result(self, request_code, result_code, intent):
        if request_code == 1:
            try:
                MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                media_projection_manager = cast('android.media.projection.MediaProjectionManager',
                                                activity.getSystemService(autoclass('android.content.Context').MEDIA_PROJECTION_SERVICE))
                self.media_projection = media_projection_manager.getMediaProjection(result_code, intent)
            except Exception as e:
                print(f"Error al obtener MediaProjection: {e}")

    def take_screenshot(self, *args):
        """Llama al servicio Java para capturar la pantalla"""
        if self.media_projection is None:
            print("MediaProjection no está disponible")
            return

        try:
            ScreenCaptureService = autoclass("org.kivy.android.ScreenCaptureService")
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            service = ScreenCaptureService(self.media_projection, activity)
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

if __name__ == "__main__":
    SpyScreenApp().run()
