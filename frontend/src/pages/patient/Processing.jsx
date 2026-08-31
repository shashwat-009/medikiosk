import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { useKiosk } from "../../context/KioskContext";
import { translate } from "../../i18n";

import "./Processing.css";

export default function Processing() {
  const navigate = useNavigate();

  const { state } = useKiosk();

  const language = state.language || "en";

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/confirmation");
    }, 2500);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <main className="processing">
      <section className="processing__container">
        <div className="processing__card">

          {/* Loading indicator */}

          <div className="processing__indicator">
            <div className="processing__spinner" />
          </div>

          {/* Heading */}

          <p className="processing__eyebrow">
            {translate(
              language,
              "processing.eyebrow"
            )}
          </p>

          <h1>
            {translate(
              language,
              "processing.title"
            )}
          </h1>

          <p className="processing__description">
            {translate(
              language,
              "processing.description"
            )}
          </p>

          {/* Processing steps */}

          <div className="processing__steps">

            <div className="processing__step processing__step--active">
              <span>✓</span>

              <p>
                {translate(
                  language,
                  "processing.stepResponses"
                )}
              </p>
            </div>

            <div className="processing__step processing__step--active">
              <span>✓</span>

              <p>
                {translate(
                  language,
                  "processing.stepHistory"
                )}
              </p>
            </div>

            <div className="processing__step">
              <span className="processing__dot" />

              <p>
                {translate(
                  language,
                  "processing.stepReview"
                )}
              </p>
            </div>

          </div>

          {/* Privacy / instruction */}

          <p className="processing__note">
            {translate(
              language,
              "processing.note"
            )}
          </p>

        </div>
      </section>
    </main>
  );
}