export default function Modal({ isOpen, children }) { return isOpen ? <div role="dialog" aria-modal="true">{children}</div> : null; }
