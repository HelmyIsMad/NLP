let mediaRecorder;
let audioChunks = [];
const recordBtn = document.getElementById("recordBtn");
const audioPreview = document.getElementById("audio-preview");
const status = document.getElementById("status");
const result = document.getElementById("result");

recordBtn.addEventListener("click", async () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        stopRecording();
    } else {
        startRecording();
    }
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPreview.src = audioUrl;
            audioPreview.style.display = "block";
            transcribeAudio(audioBlob);
        };

        mediaRecorder.start();
        recordBtn.textContent = "Stop Recording";
        recordBtn.classList.add("recording");
        status.textContent = "Recording...";
    } catch (err) {
        status.textContent = "Error: " + err.message;
    }
}

function stopRecording() {
    mediaRecorder.stop();
    recordBtn.textContent = "Start Recording";
    recordBtn.classList.remove("recording");
    status.textContent = "";
}

async function transcribeAudio(audioBlob) {
    status.textContent = "Transcribing...";
    recordBtn.disabled = true;

    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");

    try {
        const response = await fetch("/transcribe", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            result.value = data.text || "No text detected";
            status.textContent = `Language: ${data.language}`;
        } else {
            result.value = "Error: " + data.error;
            status.textContent = "";
        }
    } catch (err) {
        result.value = "Error: " + err.message;
        status.textContent = "";
    } finally {
        recordBtn.disabled = false;
    }
}