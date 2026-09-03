import { useNavigate } from "react-router-dom";
import "./RedFlagOverlay.css";

const RED_FLAG_TEXT = {
  en: {
    eyebrow: "IMPORTANT",
    title: "Please speak with a healthcare professional",
    message:
      "Some of the information provided may require prompt medical attention.",
    reported: "Reported concern",
    assistance: "Request assistance",
    continue: "Continue",
  },

  hi: {
    eyebrow: "महत्वपूर्ण",
    title: "कृपया स्वास्थ्य सेवा पेशेवर से बात करें",
    message:
      "दी गई कुछ जानकारी के लिए तुरंत चिकित्सा सहायता की आवश्यकता हो सकती है।",
    reported: "बताई गई समस्या",
    assistance: "सहायता का अनुरोध करें",
    continue: "जारी रखें",
  },

  bn: {
    eyebrow: "গুরুত্বপূর্ণ",
    title: "অনুগ্রহ করে একজন স্বাস্থ্যসেবা পেশাদারের সঙ্গে কথা বলুন",
    message:
      "আপনার দেওয়া কিছু তথ্যের জন্য দ্রুত চিকিৎসার প্রয়োজন হতে পারে।",
    reported: "জানানো সমস্যা",
    assistance: "সহায়তার অনুরোধ করুন",
    continue: "চালিয়ে যান",
  },

  mr: {
    eyebrow: "महत्त्वाचे",
    title: "कृपया आरोग्यसेवा तज्ज्ञाशी बोला",
    message:
      "आपण दिलेल्या काही माहितीसाठी त्वरित वैद्यकीय मदतीची आवश्यकता असू शकते.",
    reported: "सांगितलेली समस्या",
    assistance: "मदतीची विनंती करा",
    continue: "पुढे जा",
  },
};

export default function RedFlagOverlay({
  flag,
  onClose,
  language = "en",
}) {
  const navigate = useNavigate();

  if (!flag) {
    return null;
  }

  const text =
    RED_FLAG_TEXT[language] ?? RED_FLAG_TEXT.en;

  function handleClose() {
    onClose?.();
  }

  function handleSeekHelp() {
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
          {text.eyebrow}
        </p>

        <h2 id="red-flag-title">
          {text.title}
        </h2>

        <p className="red-flag-overlay__message">
          {text.message}
        </p>

        {flag && (
  <div className="red-flag-overlay__symptom">
    <span>
      {text.reported}
    </span>

    <strong>
      {flag.matched_text ||
        flag.symptom?.matched_text ||
        flag.category ||
        flag.flag_id ||
        ""}
    </strong>
  </div>
)}
        <div className="red-flag-overlay__actions">

          <button
            type="button"
            className="red-flag-overlay__primary"
            onClick={handleSeekHelp}
          >
            {text.assistance}
          </button>

          <button
            type="button"
            className="red-flag-overlay__secondary"
            onClick={handleClose}
          >
            {text.continue}
          </button>

        </div>

      </section>
    </div>
  );
}