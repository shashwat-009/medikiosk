import "./ProgressTracker.css";
export default function ProgressTracker({ current, total }) {
  const percentage = Math.round((current / total) * 100);

  return (
    <div className="progress-tracker">
      <div className="progress-tracker__text">
        <span>
          Question {current} of {total}
        </span>

        <span>
          {percentage}%
        </span>
      </div>

      <div className="progress-tracker__track">
        <div
          className="progress-tracker__fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}