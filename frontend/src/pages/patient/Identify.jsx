import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useKiosk } from "../../context/KioskContext";
import { translate } from "../../i18n";

import { createPatient } from "../../services/patientService";
import { createSession } from "../../services/sessionService";

import "./Identify.css";

export default function Identify() {
  const navigate = useNavigate();

  const {
    state,
    setPatient,
    setSession,
  } = useKiosk();

  const language = state.language || "en";

  const [form, setForm] = useState({
    name: "",
    age: "",
    gender: "",
    phone: "",
  });

  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));

    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    // =========================
    // Frontend validation
    // =========================

    if (!form.name.trim()) {
      setError(
        translate(
          language,
          "identify.nameRequired"
        )
      );
      return;
    }

    if (!form.age) {
      setError(
        translate(
          language,
          "identify.ageRequired"
        )
      );
      return;
    }

    if (!form.gender) {
      setError(
        translate(
          language,
          "identify.genderRequired"
        )
      );
      return;
    }

    if (!form.phone.trim()) {
      setError(
        translate(
          language,
          "identify.phoneRequired"
        )
      );
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      // =========================
      // Create patient
      // =========================

      const patient = await createPatient({
        name: form.name.trim(),
        age: Number(form.age),
        gender: form.gender,
        phone: form.phone.trim(),
      });

      // Store backend patient
      setPatient(patient);

      // =========================
      // Create session
      // =========================

      const session = await createSession(
        patient.id
      );

      // Store backend session
      setSession(session);

      // =========================
      // Continue kiosk flow
      // =========================

      navigate("/consent");

    } catch (err) {
      console.error(
        "Patient/session creation failed:",
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

  return (
    <main className="identify">
      <section className="identify__container">

        {/* Header */}

        <div className="identify__header">

          <button
            type="button"
            className="identify__back"
            onClick={() => navigate("/")}
            disabled={isSubmitting}
          >
            ←{" "}
            {translate(
              language,
              "common.back"
            )}
          </button>

          <div className="identify__step">
            1 / 3
          </div>

        </div>


        {/* Intro */}

        <div className="identify__intro">

          <p className="identify__eyebrow">
            {translate(
              language,
              "identify.eyebrow"
            )}
          </p>

          <h1>
            {translate(
              language,
              "identify.title"
            )}
          </h1>

          <p>
            {translate(
              language,
              "identify.description"
            )}
          </p>

        </div>


        {/* Form */}

        <form
          className="identify__card"
          onSubmit={handleSubmit}
        >

          {/* Name */}

          <div className="identify__field">

            <label htmlFor="name">
              {translate(
                language,
                "identify.name"
              )}
            </label>

            <input
              id="name"
              name="name"
              type="text"
              value={form.name}
              onChange={handleChange}
              placeholder={translate(
                language,
                "identify.namePlaceholder"
              )}
              autoComplete="name"
              disabled={isSubmitting}
            />

          </div>


          {/* Age + Gender */}

          <div className="identify__row">

            <div className="identify__field">

              <label htmlFor="age">
                {translate(
                  language,
                  "identify.age"
                )}
              </label>

              <input
                id="age"
                name="age"
                type="number"
                min="0"
                max="120"
                value={form.age}
                onChange={handleChange}
                placeholder={translate(
                  language,
                  "identify.agePlaceholder"
                )}
                disabled={isSubmitting}
              />

            </div>


            <div className="identify__field">

              <label htmlFor="gender">
                {translate(
                  language,
                  "identify.gender"
                )}
              </label>

              <select
                id="gender"
                name="gender"
                value={form.gender}
                onChange={handleChange}
                disabled={isSubmitting}
              >

                <option value="">
                  {translate(
                    language,
                    "identify.genderPlaceholder"
                  )}
                </option>

                <option value="male">
                  {translate(
                    language,
                    "identify.male"
                  )}
                </option>

                <option value="female">
                  {translate(
                    language,
                    "identify.female"
                  )}
                </option>

                <option value="other">
                  {translate(
                    language,
                    "identify.other"
                  )}
                </option>

              </select>

            </div>

          </div>


          {/* Phone */}

          <div className="identify__field">

            <label htmlFor="phone">
              {translate(
                language,
                "identify.phone"
              )}
            </label>

            <input
              id="phone"
              name="phone"
              type="tel"
              value={form.phone}
              onChange={handleChange}
              placeholder={translate(
                language,
                "identify.phonePlaceholder"
              )}
              autoComplete="tel"
              disabled={isSubmitting}
            />

          </div>


          {/* Error */}

          {error && (
            <p className="identify__error">
              {error}
            </p>
          )}


          {/* Submit */}

          <button
            type="submit"
            className="identify__continue"
            disabled={isSubmitting}
          >

            {isSubmitting
              ? translate(
                  language,
                  "common.loading"
                )
              : translate(
                  language,
                  "identify.continue"
                )}

            {!isSubmitting && (
              <span>→</span>
            )}

          </button>

        </form>

      </section>
    </main>
  );
}