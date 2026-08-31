import "./VoiceButton.css";

export default function VoiceButton({
  state = "idle",
  onStart,
  onResult,
}) {
  const isListening = state === "listening";
  const isProcessing = state === "processing";

  function handleClick() {
    if (isListening || isProcessing) {
      return;
    }

    onStart?.();
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