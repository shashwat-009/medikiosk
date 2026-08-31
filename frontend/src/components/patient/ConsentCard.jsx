export default function ConsentCard({ consent, onAccept }) { return <section><p>{consent?.text}</p><button onClick={onAccept}>Accept</button></section>; }
