import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useKiosk } from "../../context/KioskContext";
import { translate } from "../../i18n";
import { interviewScript } from "../../data/interviewScript";

import { createResponse } from "../../services/responseService";

import ProgressTracker from "../../components/kiosk/ProgressTracker";
import VoiceButton from "../../components/kiosk/VoiceButton";
import TouchOptions from "../../components/kiosk/TouchOptions";
import RedFlagOverlay from "../../components/kiosk/RedFlagOverlay";
import InterviewQuestion from "../../components/patient/InterviewQuestion";

import "./Interview.css";

export default function Interview() {
  const navigate = useNavigate();

  const {
    state,
    pushTranscript,
    clearRedFlag,
  } = useKiosk();

  const language = state.language || "en";

  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [inputMode, setInputMode] = useState("idle");
  const [inputType, setInputType] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const currentQuestion = interviewScript[currentIndex];

  const isLastQuestion =
    currentIndex === interviewScript.length - 1;

  /*
   * =========================
   * Voice input
   * =========================
   */

  function handleVoiceStart() {
    setError("");
    setInputMode("listening");
    setInputType("voice");

    /*
     * TEMPORARY FRONTEND MOCK
     *
     * Real ASR will replace this later.
     */
    setTimeout(() => {
      setInputMode("idle");
    }, 1500);
  }

  function handleVoiceResult(transcript) {
    if (!transcript) return;

    setAnswer(transcript);
    setInputMode("answered");
    setInputType("voice");
    setError("");
  }

  /*
   * =========================
   * Touch input
   * =========================
   */

  function handleTouchAnswer(value) {
    setAnswer(value);
    setInputMode("answered");
    setInputType("touch");
    setError("");
  }

  /*
   * =========================
   * Text input
   * =========================
   */

  function handleTextChange(event) {
    setAnswer(event.target.value);
    setInputMode("answered");
    setInputType("touch");
    setError("");
  }

  /*
   * =========================
   * Save response
   * =========================
   */

  async function saveCurrentResponse() {
    if (!state.session?.id) {
      throw new Error(
        "No active session found."
      );
    }

    const response = await createResponse({
      session_id: state.session.id,

      question: translate(
        language,
        currentQuestion.questionKey
      ),

      answer: answer.trim(),

      input_type: inputType || "touch",

      language,
    });

    /*
     * Keep local transcript as well.
     */
    pushTranscript({
      questionId: currentQuestion.id,

      question: translate(
        language,
        currentQuestion.questionKey
      ),

      answer: answer.trim(),

      language,

      inputType: inputType || "touch",

      timestamp: new Date().toISOString(),

      backendResponseId: response.id,
    });

    return response;
  }

  /*
   * =========================
   * Continue
   * =========================
   */

  async function handleContinue() {
    if (!answer.trim()) {
      setError(
        translate(
          language,
          "interview.errors.answerRequired"
        )
      );

      return;
    }

    if (!state.session?.id) {
      setError(
        "No active session found. Please restart the visit."
      );

      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      /*
       * Save answer to backend.
       */
      await saveCurrentResponse();

      /*
       * Last question → Documents
       */
      if (isLastQuestion) {
        navigate("/documents");
        return;
      }

      /*
       * Move to next question.
       */
      setCurrentIndex(
        (current) => current + 1
      );

      setAnswer("");
      setInputMode("idle");
      setInputType("");
      setError("");

    } catch (err) {
      console.error(
        "Failed to save interview response:",
        err
      );

      setError(
        err.message ||
        translate(
          language,
          "common.error"
        )
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  /*
   * =========================
   * Back
   * =========================
   */

  function handleBack() {
    if (isSubmitting) return;

    if (currentIndex === 0) {
      navigate("/consent");
      return;
    }

    setCurrentIndex(
      (current) => current - 1
    );

    setAnswer("");
    setInputMode("idle");
    setInputType("");
    setError("");
  }

  /*
   * =========================
   * Safety
   * =========================
   */

  if (!currentQuestion) {
    return null;
  }

  const hasTouchOptions =
    Array.isArray(currentQuestion.options) &&
    currentQuestion.options.length > 0;

  return (
    <main className="interview">
      <section className="interview__container">

        {/* =========================
            Header
            ========================= */}

        <header className="interview__header">

          <button
            type="button"
            className="interview__back"
            onClick={handleBack}
            disabled={isSubmitting}
          >
            ←{" "}
            {translate(
              language,
              "common.back"
            )}
          </button>

          <ProgressTracker
            current={currentIndex + 1}
            total={interviewScript.length}
          />

        </header>


        {/* =========================
            Intro
            ========================= */}

        <div className="interview__intro">

          <p className="interview__eyebrow">
            {translate(
              language,
              "interview.eyebrow"
            )}
          </p>

          <h1>
            {translate(
              language,
              "interview.title"
            )}
          </h1>

          <p>
            {translate(
              language,
              "interview.description"
            )}
          </p>

        </div>


        {/* =========================
            Main Card
            ========================= */}

        <section className="interview__card">

          <InterviewQuestion
            question={translate(
              language,
              currentQuestion.questionKey
            )}
          />


          {/* =========================
              Voice Input
              ========================= */}

          <div className="interview__voice-section">

            <p className="interview__input-hint">
              {translate(
                language,
                "interview.speak"
              )}
            </p>

            <VoiceButton
              state={inputMode}
              onStart={handleVoiceStart}
              onResult={handleVoiceResult}
            />

            {inputMode === "listening" && (
              <p className="interview__listening">
                {translate(
                  language,
                  "interview.listening"
                )}
              </p>
            )}

          </div>


          {/* =========================
              Touch Options
              ========================= */}

          {hasTouchOptions && (
            <TouchOptions
              label={translate(
                language,
                "interview.tap"
              )}
              options={currentQuestion.options.map(
                (option) =>
                  translate(
                    language,
                    `interview.${option}`
                  )
              )}
              values={currentQuestion.options}
              selected={answer}
              onSelect={handleTouchAnswer}
            />
          )}
          {/* =========================
              Text Input
              ONLY for open-ended questions
              ========================= */}

          {!hasTouchOptions && (
            <>
              <div className="interview__divider">
                <span>
                  {translate(
                    language,
                    "interview.type"
                  )}
                </span>
              </div>

              <div className="interview__text-input">

                <textarea
                  value={answer}
                  onChange={handleTextChange}
                  placeholder={translate(
                    language,
                    "interview.answerLabel"
                  )}
                  disabled={isSubmitting}
                />

              </div>
            </>
          )}


          {/* =========================
              Answer Preview
              ========================= */}

          {answer && (
            <div className="interview__answer">

              <span className="interview__answer-label">
                {translate(
                  language,
                  "interview.answerLabel"
                )}
              </span>

              <p>
                {hasTouchOptions &&
                  currentQuestion.options.includes(answer)
                  ? translate(
                    language,
                    `interview.${answer}`
                  )
                  : answer}
              </p>

            </div>
          )}


          {/* =========================
              Error
              ========================= */}

          {error && (
            <p className="interview__error">
              {error}
            </p>
          )}


          {/* =========================
              Continue
              ========================= */}

          <div className="interview__actions">

            <button
              type="button"
              className="interview__continue"
              onClick={handleContinue}
              disabled={isSubmitting}
            >

              {isSubmitting
                ? translate(
                  language,
                  "common.loading"
                )
                : translate(
                  language,
                  "interview.continue"
                )}

              {!isSubmitting && (
                <span>→</span>
              )}

            </button>

          </div>

        </section>


        {/* =========================
            Privacy
            ========================= */}

        <p className="interview__privacy">
          {translate(
            language,
            "interview.privacy"
          )}
        </p>

      </section>


      {/* =========================
          Red Flag
          ========================= */}

      <RedFlagOverlay
        flag={state.redFlag}
        onClose={clearRedFlag}
      />

    </main>
  );
}