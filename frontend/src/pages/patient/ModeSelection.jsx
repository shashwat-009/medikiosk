import { useNavigate } from "react-router-dom";

import { useKiosk } from "../../context/KioskContext";
import { translate } from "../../i18n";

import "./ModeSelection.css";

export default function ModeSelection() {
  const navigate = useNavigate();

  const {
    state,
    setMode,
  } = useKiosk();

  const language = state.language || "en";

  function handleModeSelect(mode) {
    setMode(mode);
    navigate("/interview");
  }

  return (
    <main className="mode-selection">
      <section className="mode-selection__container">

        {/* Header */}

        <div className="mode-selection__header">

          <button
            type="button"
            className="mode-selection__back"
            onClick={() => navigate("/consent")}
          >
            ←{" "}
            {translate(
              language,
              "common.back"
            )}
          </button>

          <div className="mode-selection__step">
            3 / 4
          </div>

        </div>


        {/* Intro */}

        <div className="mode-selection__intro">

          <p className="mode-selection__eyebrow">
            {translate(
              language,
              "mode.eyebrow"
            )}
          </p>

          <h1>
            {translate(
              language,
              "mode.title"
            )}
          </h1>

          <p>
            {translate(
              language,
              "mode.description"
            )}
          </p>

        </div>


        {/* Mode options */}

        <div className="mode-selection__options">

          {/* Allopathy */}

          <button
            type="button"
            className="mode-selection__card"
            onClick={() =>
              handleModeSelect("allopathy")
            }
          >

            <div className="mode-selection__icon">
              +
            </div>

            <div className="mode-selection__content">

              <h2>
                {translate(
                  language,
                  "mode.allopathy.title"
                )}
              </h2>

              <p>
                {translate(
                  language,
                  "mode.allopathy.description"
                )}
              </p>

            </div>

            <span className="mode-selection__arrow">
              →
            </span>

          </button>


          {/* Ayurveda / AYUSH */}

          <button
            type="button"
            className="mode-selection__card"
            onClick={() =>
              handleModeSelect("ayush")
            }
          >

            <div className="mode-selection__icon">
              ॐ
            </div>

            <div className="mode-selection__content">

              <h2>
                {translate(
                  language,
                  "mode.ayush.title"
                )}
              </h2>

              <p>
                {translate(
                  language,
                  "mode.ayush.description"
                )}
              </p>

            </div>

            <span className="mode-selection__arrow">
              →
            </span>

          </button>

        </div>

      </section>
    </main>
  );
}