import time
import threading
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button.button import MDFabButton

from jnius import autoclass
from android.permissions import request_permissions, Permission
from android import activity

request_permissions([Permission.WRITE_EXTERNAL_STORAGE])


class SpyScreenApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def take_screenshot(self):
        """Llama al servicio Java para capturar la pantalla"""
        try:
            ScreenCaptureService = autoclass("org.kivy.android.ScreenCaptureService")
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            service = ScreenCaptureService(activity)
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
