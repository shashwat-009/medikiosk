import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useKiosk } from "../../context/KioskContext";
import { translate } from "../../i18n";

import DocumentUploader from "../../components/patient/DocumentUploader";

import "./Documents.css";

const DOCUMENT_TYPES = [
  {
    id: "prescription",
    icon: "Rx",
  },
  {
    id: "labReport",
    icon: "LAB",
  },
  {
    id: "dischargeSummary",
    icon: "DOC",
  },
  {
    id: "other",
    icon: "FILE",
  },
];

export default function Documents() {
  const navigate = useNavigate();

  const { state } = useKiosk();

  const language = state.language || "en";

  const [documentType, setDocumentType] =
    useState("prescription");

  const [documents, setDocuments] = useState([]);

  const [error, setError] = useState("");

  function handleFileAdd(file) {
    if (!file) return;

    setDocuments((current) => [
      ...current,
      {
        id: `${Date.now()}-${file.name}`,
        file,
        type: documentType,
      },
    ]);

    setError("");
  }

  function handleRemove(id) {
    setDocuments((current) =>
      current.filter((document) => document.id !== id)
    );
  }

  function handleContinue() {
    navigate("/processing");
  }

  function handleSkip() {
    navigate("/processing");
  }

  function handleBack() {
    navigate("/interview");
  }

  return (
    <main className="documents">
      <section className="documents__container">

        {/* HEADER */}

        <header className="documents__header">
          <button
            type="button"
            className="documents__back"
            onClick={handleBack}
          >
            ← {translate(language, "common.back")}
          </button>
        </header>


        {/* INTRO */}

        <div className="documents__intro">
          <p className="documents__eyebrow">
            MEDICAL DOCUMENTS
          </p>

          <h1>
            {translate(
              language,
              "documents.title"
            )}
          </h1>

          <p>
            {translate(
              language,
              "documents.description"
            )}
          </p>
        </div>


        {/* DOCUMENT TYPE */}

        <section className="documents__card">

          <h2>
            {translate(
              language,
              "documents.documentType"
            )}
          </h2>

          <div className="documents__types">
            {DOCUMENT_TYPES.map((type) => (
              <button
                key={type.id}
                type="button"
                className={`documents__type ${
                  documentType === type.id
                    ? "documents__type--selected"
                    : ""
                }`}
                onClick={() => {
                  setDocumentType(type.id);
                  setError("");
                }}
              >
                <span className="documents__type-icon">
                  {type.icon}
                </span>

                <span>
                  {translate(
                    language,
                    `documents.${type.id}`
                  )}
                </span>
              </button>
            ))}
          </div>


          {/* UPLOADER */}

          <DocumentUploader
            onFileAdd={handleFileAdd}
          />


          {/* SELECTED DOCUMENTS */}

          {documents.length > 0 && (
            <div className="documents__selected">

              <h3>
                {translate(
                  language,
                  "documents.selected"
                )}
              </h3>

              <div className="documents__list">

                {documents.map((document) => (
                  <div
                    key={document.id}
                    className="documents__item"
                  >
                    <div>
                      <strong>
                        {document.file.name}
                      </strong>

                      <span>
                        {translate(
                          language,
                          `documents.${document.type}`
                        )}
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        handleRemove(document.id)
                      }
                    >
                      ×
                    </button>
                  </div>
                ))}

              </div>
            </div>
          )}


          {error && (
            <p className="documents__error">
              {error}
            </p>
          )}


          {/* ACTIONS */}

          <div className="documents__actions">

            <button
              type="button"
              className="documents__skip"
              onClick={handleSkip}
            >
              {translate(
                language,
                "documents.skip"
              )}
            </button>

            <button
              type="button"
              className="documents__continue"
              onClick={handleContinue}
            >
              {translate(
                language,
                "common.next"
              )}

              <span>→</span>
            </button>

          </div>

        </section>

      </section>
    </main>
  );
}