import { useRef } from "react";

import { useKiosk } from "../../context/KioskContext";
import { translate } from "../../i18n";

import "./DocumentUploader.css";

export default function DocumentUploader({ onFileAdd }) {
  const inputRef = useRef(null);

  const { state } = useKiosk();

  const language = state.language || "en";

  function handleChange(event) {
    const file = event.target.files?.[0];

    if (!file) return;

    onFileAdd(file);

    // Allow the same file to be selected again later.
    event.target.value = "";
  }

  function handleClick() {
    inputRef.current?.click();
  }

  return (
    <div className="document-uploader">

      <input
        ref={inputRef}
        type="file"
        accept="image/*,.pdf"
        onChange={handleChange}
        hidden
      />

      <button
        type="button"
        className="document-uploader__button"
        onClick={handleClick}
      >
        <span className="document-uploader__icon">
          ↑
        </span>

        <span>
          {translate(
            language,
            "documents.upload"
          )}
        </span>
      </button>

      <p className="document-uploader__hint">
        {translate(
          language,
          "documents.fileHint"
        )}
      </p>

    </div>
  );
}