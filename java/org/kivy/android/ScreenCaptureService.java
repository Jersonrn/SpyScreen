package org.kivy.android;

import android.content.Context;
import android.graphics.Bitmap;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.util.DisplayMetrics;
import android.view.WindowManager;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class ScreenCaptureService {
    private MediaProjection mediaProjection;
    private ImageReader imageReader;
    private VirtualDisplay virtualDisplay;
    private int width, height, densityDpi;
    private Context context;
    
    public ScreenCaptureService(MediaProjection mediaProjection, Context context) {
        this.mediaProjection = mediaProjection;
        this.context = context;
        
        // Obtener el tamaño de la pantalla
        WindowManager windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
        DisplayMetrics metrics = new DisplayMetrics();
        windowManager.getDefaultDisplay().getMetrics(metrics);
        
        width = metrics.widthPixels;
        height = metrics.heightPixels;
        densityDpi = metrics.densityDpi;
    }
    
    public String captureScreenshot() {
        if (mediaProjection == null) {
            return "Error: MediaProjection no está inicializada";
        }
        
        // Configurar ImageReader
        imageReader = ImageReader.newInstance(width, height, android.graphics.PixelFormat.RGBA_8888, 2);
        
        // Crear VirtualDisplay
        virtualDisplay = mediaProjection.createVirtualDisplay(
                "ScreenCapture",
                width,
                height,
                densityDpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                imageReader.getSurface(),
                null,
                new Handler(Looper.getMainLooper())
        );
        
        // Dar tiempo para que la imagen se capture
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        // Capturar la imagen
        Image image = imageReader.acquireLatestImage();
        if (image == null) {
            cleanUp();
            return "Error: No se pudo capturar la imagen";
        }
        
        // Convertir Image a Bitmap
        Bitmap bitmap = imageToBitmap(image);
        image.close();
        
        // Guardar la imagen en almacenamiento externo
        String fileName = "screenshot_" + new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date()) + ".png";
        File picturesDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES);
        File file = new File(picturesDir, fileName);
        
        try {
            if (!picturesDir.exists()) {
                picturesDir.mkdirs();
            }
            
            FileOutputStream fos = new FileOutputStream(file);
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, fos);
            fos.flush();
            fos.close();
            
            cleanUp();
            return "Screenshot guardado en: " + file.getAbsolutePath();
        } catch (Exception e) {
            cleanUp();
            return "Error al guardar la imagen: " + e.getMessage();
        }
    }
    
    private Bitmap imageToBitmap(Image image) {
        Image.Plane[] planes = image.getPlanes();
        ByteBuffer buffer = planes[0].getBuffer();
        int pixelStride = planes[0].getPixelStride();
        int rowStride = planes[0].getRowStride();
        int rowPadding = rowStride - pixelStride * width;
        
        // Crear el bitmap
        Bitmap bitmap = Bitmap.createBitmap(width + rowPadding / pixelStride, height, Bitmap.Config.ARGB_8888);
        bitmap.copyPixelsFromBuffer(buffer);
        
        // Recortar el bitmap si es necesario
        if (bitmap.getWidth() > width || bitmap.getHeight() > height) {
            bitmap = Bitmap.createBitmap(bitmap, 0, 0, width, height);
        }
        
        return bitmap;
    }
    
    private void cleanUp() {
        if (virtualDisplay != null) {
            virtualDisplay.release();
            virtualDisplay = null;
        }
        
        if (imageReader != null) {
            imageReader.close();
            imageReader = null;
        }
    }
}
