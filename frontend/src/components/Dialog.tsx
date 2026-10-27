import { useEffect, useRef, type ReactNode } from 'react';

interface DialogProps {
  labelledBy: string;
  onDismiss: () => void;
  children: ReactNode;
}

/** Native modality keeps keyboard focus inside and restores it on close. */
export function Dialog({ labelledBy, onDismiss, children }: DialogProps) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    const previousFocus = document.activeElement;
    dialog?.showModal();
    return () => {
      dialog?.close();
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) {
        previousFocus.focus();
      }
    };
  }, []);

  return (
    <dialog
      ref={ref}
      className="app-dialog"
      aria-labelledby={labelledBy}
      onCancel={(event) => {
        event.preventDefault();
        onDismiss();
      }}
    >
      {children}
    </dialog>
  );
}
