package org.kivy.android;

import android.content.Context;
import android.graphics.Bitmap;
import android.hardware.display.DisplayManager;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Environment;
import android.util.DisplayMetrics;
import android.view.WindowManager;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;

public class ScreenCaptureService {
    private MediaProjection mediaProjection;
    private ImageReader imageReader;
    private int width, height;
    
    public ScreenCaptureService(MediaProjection mediaProjection, Context context) {
        this.mediaProjection = mediaProjection;

        // Obtener el tamaño de la pantalla
        WindowManager windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
        DisplayMetrics metrics = new DisplayMetrics();
        windowManager.getDefaultDisplay().getMetrics(metrics);
        width = metrics.widthPixels;
        height = metrics.heightPixels;

        // Configurar ImageReader
        imageReader = ImageReader.newInstance(width, height, 1, 2);
        
        // Crear VirtualDisplay
        mediaProjection.createVirtualDisplay("ScreenCapture",
                width, height, metrics.densityDpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                imageReader.getSurface(), null, null);
    }

    public String captureScreenshot() {
        Image image = imageReader.acquireLatestImage();
        if (image == null) {
            return "Error: No se pudo capturar la imagen";
        }

        // Convertir Image a Bitmap
        Image.Plane[] planes = image.getPlanes();
        ByteBuffer buffer = planes[0].getBuffer();
        int pixelStride = planes[0].getPixelStride();
        int rowStride = planes[0].getRowStride();
        int rowPadding = rowStride - pixelStride * width;

        Bitmap bitmap = Bitmap.createBitmap(width + rowPadding / pixelStride, height, Bitmap.Config.ARGB_8888);
        bitmap.copyPixelsFromBuffer(buffer);
        image.close();

        // Guardar la imagen en almacenamiento externo
        File file = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES), "screenshot.png");
        try (FileOutputStream fos = new FileOutputStream(file)) {
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, fos);
            return "Screenshot guardado en: " + file.getAbsolutePath();
        } catch (Exception e) {
            return "Error al guardar la imagen: " + e.getMessage();
        }
    }
}
