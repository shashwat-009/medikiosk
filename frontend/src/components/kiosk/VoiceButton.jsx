import { useRef, useState } from "react";

import "./VoiceButton.css";

export default function VoiceButton({
  state = "idle",
  onStart,
  onResult,
  onError,
}) {
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const [isRecording, setIsRecording] = useState(false);

  const isListening =
    state === "listening" || isRecording;

  const isProcessing =
    state === "processing";

  async function startRecording() {
    if (isRecording || isProcessing) {
      return;
    }

    try {
      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      const recorder = new MediaRecorder(stream);

      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        stream
          .getTracks()
          .forEach((track) => track.stop());

        const audioBlob = new Blob(
          chunksRef.current,
          {
            type: recorder.mimeType,
          }
        );

        setIsRecording(false);

        try {
          const formData = new FormData();

          formData.append(
            "file",
            audioBlob,
            "interview.webm"
          );

          const response = await fetch(
            `${
              import.meta.env.VITE_API_BASE_URL ??
              "http://localhost:8000"
            }/asr/transcribe`,
            {
              method: "POST",
              body: formData,
            }
          );

          if (!response.ok) {
            const errorData =
              await response.json().catch(
                () => null
              );

            throw new Error(
              errorData?.detail ||
                `ASR request failed: ${response.status}`
            );
          }

          const result =
            await response.json();

          if (!result.text?.trim()) {
            throw new Error(
              "No speech was detected."
            );
          }

          onResult?.(result.text);
        } catch (error) {
          console.error(
            "ASR transcription failed:",
            error
          );

          onError?.(error);
        }
      };

      recorder.start();

      setIsRecording(true);
      onStart?.();
    } catch (error) {
      console.error(
        "Microphone access failed:",
        error
      );

      setIsRecording(false);
      onError?.(error);
    }
  }

  function stopRecording() {
    if (
      !mediaRecorderRef.current ||
      mediaRecorderRef.current.state ===
        "inactive"
    ) {
      return;
    }

    mediaRecorderRef.current.stop();
  }

  function handleClick() {
    if (isRecording) {
      stopRecording();
      return;
    }

    if (isProcessing) {
      return;
    }

    startRecording();
  }

  const label = isListening
    ? "Listening..."
    : isProcessing
      ? "Processing..."
      : "Speak";

  return (
    <div className="voice-button">
      <button
        type="button"
        className={`voice-button__control ${
          isListening
            ? "voice-button__control--listening"
            : ""
        }`}
        onClick={handleClick}
        disabled={isProcessing}
        aria-label={label}
      >
        <span className="voice-button__icon">
          {isListening ? "●" : "🎙"}
        </span>
      </button>

      <span className="voice-button__label">
        {label}
      </span>
    </div>
  );
}