import { useNavigate } from "react-router-dom";
import "./RedFlagOverlay.css";

export default function RedFlagOverlay({ flag, onClose }) {
  const navigate = useNavigate();

  if (!flag) {
    return null;
  }

  function handleClose() {
    onClose?.();
  }

  function handleSeekHelp() {
    /*
     * MVP behavior:
     * take the patient back to the kiosk/home screen
     * where staff assistance can be requested.
     *
     * Later this can trigger a hospital-specific
     * emergency/staff workflow.
     */
    onClose?.();
    navigate("/");
  }

  return (
    <div
      className="red-flag-overlay"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="red-flag-title"
    >
      <div className="red-flag-overlay__backdrop" />

      <section className="red-flag-overlay__card">
        <div className="red-flag-overlay__icon">
          !
        </div>

        <p className="red-flag-overlay__eyebrow">
          IMPORTANT
        </p>

        <h2 id="red-flag-title">
          Please speak with a healthcare professional
        </h2>

        <p className="red-flag-overlay__message">
          Some of the information provided may require
          prompt medical attention.
        </p>

        {flag.symptom && (
          <div className="red-flag-overlay__symptom">
            <span>Reported concern</span>
            <strong>{flag.symptom}</strong>
          </div>
        )}

        <div className="red-flag-overlay__actions">
          <button
            type="button"
            className="red-flag-overlay__primary"
            onClick={handleSeekHelp}
          >
            Request assistance
          </button>

          <button
            type="button"
            className="red-flag-overlay__secondary"
            onClick={handleClose}
          >
            Continue
          </button>
        </div>
      </section>
    </div>
  );
}