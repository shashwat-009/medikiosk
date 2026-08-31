import { useNavigate } from "react-router-dom";

import { useKiosk } from "../../context/KioskContext";
import { translate } from "../../i18n";

import "./Confirmation.css";

export default function Confirmation() {
  const navigate = useNavigate();

  const { state } = useKiosk();

  const language = state.language || "en";

  function handleContinue() {
    /*
     * Temporary MVP behavior.
     *
     * There is currently no consultation/HIS
     * handoff page in the patient architecture.
     *
     * Later this will be replaced with the
     * appropriate consultation handoff.
     */
    navigate("/");
  }

  return (
    <main className="confirmation">
      <section className="confirmation__container">

        <div className="confirmation__card">

          {/* Success indicator */}

          <div className="confirmation__icon">
            ✓
          </div>

          {/* Heading */}

          <p className="confirmation__eyebrow">
            {translate(
              language,
              "confirmation.eyebrow"
            )}
          </p>

          <h1>
            {translate(
              language,
              "confirmation.title"
            )}
          </h1>

          <p className="confirmation__description">
            {translate(
              language,
              "confirmation.description"
            )}
          </p>

          {/* Completion status */}

          <div className="confirmation__status">

            <div className="confirmation__status-item">
              <span>✓</span>

              <p>
                {translate(
                  language,
                  "confirmation.statusPatient"
                )}
              </p>
            </div>

            <div className="confirmation__status-item">
              <span>✓</span>

              <p>
                {translate(
                  language,
                  "confirmation.statusHistory"
                )}
              </p>
            </div>

            <div className="confirmation__status-item">
              <span>✓</span>

              <p>
                {translate(
                  language,
                  "confirmation.statusReview"
                )}
              </p>
            </div>

          </div>

          {/* Continue */}

          <button
            type="button"
            className="confirmation__continue"
            onClick={handleContinue}
          >
            {translate(
              language,
              "confirmation.continue"
            )}

            <span>→</span>
          </button>

          {/* Note */}

          <p className="confirmation__note">
            {translate(
              language,
              "confirmation.note"
            )}
          </p>

        </div>

      </section>
    </main>
  );
}