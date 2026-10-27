import { Component, Suspense, type ReactNode } from 'react';

/** Keep navigation available when a page is loading or cannot be rendered. */
export class PageBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  render() {
    if (this.state.failed) {
      return (
        <div role="alert" className="my-8 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 space-y-3">
          <h1 className="text-xl font-bold">This page could not be opened</h1>
          <p className="text-sm text-[var(--foreground-muted)]">
            Reload to try again, or use the navigation to open another page.
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-lg bg-[var(--foreground)] px-4 py-2 text-sm font-semibold text-[var(--surface)]"
          >
            Reload page
          </button>
        </div>
      );
    }

    return (
      <Suspense fallback={
        <div role="status" className="min-h-64 py-16 text-center text-[var(--foreground-muted)]">
          Loading page…
        </div>
      }>
        {this.props.children}
      </Suspense>
    );
  }
}
