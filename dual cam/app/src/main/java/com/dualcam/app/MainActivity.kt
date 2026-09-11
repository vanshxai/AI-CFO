package com.dualcam.app

import android.Manifest
import android.content.ContentValues
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.provider.MediaStore
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.Camera
import androidx.camera.core.CameraInfo
import androidx.camera.core.CameraSelector
import androidx.camera.core.ConcurrentCamera
import androidx.camera.core.Preview
import androidx.camera.core.UseCaseGroup
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.MediaStoreOutputOptions
import androidx.camera.video.Quality
import androidx.camera.video.QualitySelector
import androidx.camera.video.Recorder
import androidx.camera.video.Recording
import androidx.camera.video.VideoCapture
import androidx.camera.video.VideoRecordEvent
import androidx.core.content.ContextCompat
import com.dualcam.app.databinding.ActivityMainBinding
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var cameraProvider: ProcessCameraProvider

    private var backPreview: Preview? = null
    private var frontPreview: Preview? = null
    private var backCamera: Camera? = null
    private var backVideoCapture: VideoCapture<Recorder>? = null
    private var frontVideoCapture: VideoCapture<Recorder>? = null
    private var backRecording: Recording? = null
    private var frontRecording: Recording? = null

    private var isRecording = false
    private var isBackMain = true
    private var torchOn = false
    private var recordingStartTime = 0L
    private val timerHandler = Handler(Looper.getMainLooper())

    private val requiredPermissions = arrayOf(Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO)

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { results ->
        if (results.values.all { it }) {
            startCamera()
        } else {
            binding.permissionOverlay.visibility = View.VISIBLE
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.recordButton.setOnClickListener { toggleRecording() }
        binding.swapButton.setOnClickListener { swapPreviews() }
        binding.torchButton.setOnClickListener { toggleTorch() }
        binding.grantPermissionButton.setOnClickListener { requestPermissions() }
        binding.closeButton.setOnClickListener { finish() }

        if (hasPermissions()) {
            startCamera()
        } else {
            requestPermissions()
        }
    }

    private fun hasPermissions() = requiredPermissions.all {
        ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
    }

    private fun requestPermissions() {
        permissionLauncher.launch(requiredPermissions)
    }

    private fun startCamera() {
        binding.permissionOverlay.visibility = View.GONE
        val providerFuture = ProcessCameraProvider.getInstance(this)
        providerFuture.addListener({
            cameraProvider = providerFuture.get()
            bindConcurrentCameras()
        }, ContextCompat.getMainExecutor(this))
    }

    private fun bindConcurrentCameras() {
        val concurrentInfos = cameraProvider.availableConcurrentCameraInfos
        val pair = concurrentInfos.firstOrNull { infos ->
            infos.any { it.lensFacing == CameraSelector.LENS_FACING_BACK } &&
                infos.any { it.lensFacing == CameraSelector.LENS_FACING_FRONT }
        }

        if (pair == null) {
            binding.unsupportedOverlay.visibility = View.VISIBLE
            return
        }

        val backInfo = pair.first { it.lensFacing == CameraSelector.LENS_FACING_BACK }
        val frontInfo = pair.first { it.lensFacing == CameraSelector.LENS_FACING_FRONT }

        val newBackPreview = Preview.Builder().build()
        val newFrontPreview = Preview.Builder().build()

        val qualitySelector = QualitySelector.from(Quality.SD)
        val backCapture = VideoCapture.withOutput(Recorder.Builder().setQualitySelector(qualitySelector).build())
        val frontCapture = VideoCapture.withOutput(Recorder.Builder().setQualitySelector(qualitySelector).build())

        val backGroup = UseCaseGroup.Builder().addUseCase(newBackPreview).addUseCase(backCapture).build()
        val frontGroup = UseCaseGroup.Builder().addUseCase(newFrontPreview).addUseCase(frontCapture).build()

        val backConfig = ConcurrentCamera.SingleCameraConfig(selectorFor(backInfo), backGroup, this)
        val frontConfig = ConcurrentCamera.SingleCameraConfig(selectorFor(frontInfo), frontGroup, this)

        cameraProvider.unbindAll()
        val concurrentCamera = cameraProvider.bindToLifecycle(listOf(backConfig, frontConfig))

        backPreview = newBackPreview
        frontPreview = newFrontPreview
        backVideoCapture = backCapture
        frontVideoCapture = frontCapture
        backCamera = concurrentCamera.cameras.getOrNull(0)

        isBackMain = true
        applyPreviewRouting()
    }

    private fun selectorFor(cameraInfo: CameraInfo): CameraSelector {
        return CameraSelector.Builder().addCameraFilter { infos ->
            infos.filter { it == cameraInfo }
        }.build()
    }

    private fun applyPreviewRouting() {
        val mainView = binding.previewMain
        val pipView = binding.previewPip
        if (isBackMain) {
            backPreview?.setSurfaceProvider(mainView.surfaceProvider)
            frontPreview?.setSurfaceProvider(pipView.surfaceProvider)
        } else {
            frontPreview?.setSurfaceProvider(mainView.surfaceProvider)
            backPreview?.setSurfaceProvider(pipView.surfaceProvider)
        }
    }

    private fun swapPreviews() {
        if (isRecording) return
        isBackMain = !isBackMain
        applyPreviewRouting()
    }

    private fun toggleTorch() {
        val camera = backCamera ?: return
        if (!camera.cameraInfo.hasFlashUnit()) {
            Toast.makeText(this, "Flash not available", Toast.LENGTH_SHORT).show()
            return
        }
        torchOn = !torchOn
        camera.cameraControl.enableTorch(torchOn)
        binding.torchButton.setImageResource(if (torchOn) R.drawable.ic_flash else R.drawable.ic_flash_off)
    }

    private fun toggleRecording() {
        if (isRecording) stopRecording() else startRecording()
    }

    private fun startRecording() {
        val backCapture = backVideoCapture ?: return
        val frontCapture = frontVideoCapture ?: return

        backRecording = startSingleRecording(backCapture, "dualcam_back")
        frontRecording = startSingleRecording(frontCapture, "dualcam_front")

        isRecording = true
        recordingStartTime = SystemClock.elapsedRealtime()
        binding.recordButton.setImageResource(R.drawable.ic_stop)
        binding.timerText.visibility = View.VISIBLE
        binding.swapButton.isEnabled = false
        timerHandler.post(timerRunnable)
    }

    private fun startSingleRecording(videoCapture: VideoCapture<Recorder>, prefix: String): Recording {
        val name = "${prefix}_${SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())}.mp4"
        val contentValues = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, name)
            put(MediaStore.MediaColumns.MIME_TYPE, "video/mp4")
            put(MediaStore.MediaColumns.RELATIVE_PATH, "Movies/DualCam")
        }
        val outputOptions = MediaStoreOutputOptions.Builder(
            contentResolver, MediaStore.Video.Media.EXTERNAL_CONTENT_URI
        ).setContentValues(contentValues).build()

        val hasAudio = ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) ==
            PackageManager.PERMISSION_GRANTED

        var pending = videoCapture.output.prepareRecording(this, outputOptions)
        if (hasAudio) {
            pending = pending.withAudioEnabled()
        }

        return pending.start(ContextCompat.getMainExecutor(this)) { event ->
            if (event is VideoRecordEvent.Finalize) {
                if (event.hasError()) {
                    Toast.makeText(this, "Recording error ($prefix): ${event.error}", Toast.LENGTH_LONG).show()
                } else {
                    Toast.makeText(this, "Saved: $name", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun stopRecording() {
        backRecording?.stop()
        frontRecording?.stop()
        backRecording = null
        frontRecording = null
        isRecording = false
        binding.recordButton.setImageResource(R.drawable.ic_record)
        binding.timerText.visibility = View.GONE
        binding.swapButton.isEnabled = true
        timerHandler.removeCallbacks(timerRunnable)
    }

    private val timerRunnable = object : Runnable {
        override fun run() {
            val elapsed = SystemClock.elapsedRealtime() - recordingStartTime
            val minutes = (elapsed / 1000) / 60
            val seconds = (elapsed / 1000) % 60
            binding.timerText.text = String.format(Locale.US, "%02d:%02d", minutes, seconds)
            timerHandler.postDelayed(this, 500)
        }
    }

    override fun onDestroy() {
        if (isRecording) stopRecording()
        if (::cameraProvider.isInitialized) {
            cameraProvider.unbindAll()
        }
        super.onDestroy()
    }
}
