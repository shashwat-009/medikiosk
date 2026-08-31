import "./InterviewQuestion.css";

export default function InterviewQuestion({ question }) {
  return (
    <div className="interview-question">
      <p className="interview-question__label">
        QUESTION
      </p>

      <h2 className="interview-question__text">
        {question}
      </h2>
    </div>
  );
}