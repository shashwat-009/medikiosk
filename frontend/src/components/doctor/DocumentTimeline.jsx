export default function DocumentTimeline({ documents = [] }) { return <ol>{documents.map(document => <li key={document.id ?? document.name}>{document.name ?? document}</li>)}</ol>; }
