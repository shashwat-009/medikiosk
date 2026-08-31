export default function ClinicalHistory({ history = [] }) { return <section>{history.map((item, index) => <p key={index}>{item}</p>)}</section>; }
