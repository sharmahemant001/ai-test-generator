import { useEffect, useRef, useState } from 'react';
import { TestCase } from '../types/testCase';

type TestCaseCardProps = {
  testCase: TestCase;
  index?: number;
};

function copyText(value: string) {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(value);
  }
}

function CodeBlock({ label, value }: { label: string; value: string }) {
  return (
    <details className="test-card-block" open>
      <summary>{label}</summary>
      <div className="code-shell">
        <button type="button" onClick={() => copyText(value)} className="copy-button">
          Copy
        </button>
        <pre>{value}</pre>
      </div>
    </details>
  );
}

export default function TestCaseCard({ testCase, index = 0 }: TestCaseCardProps) {
  const ref = useRef<HTMLElement | null>(null);
  const prefersReducedMotion = typeof window !== 'undefined' &&
    (window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches ?? false);
  const [visible, setVisible] = useState(prefersReducedMotion);

  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === 'undefined') return;

    if (prefersReducedMotion) {
      // If user prefers reduced motion, reveal immediately and skip observer.
      setVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true);
            if (el) observer.unobserve(el);
          }
        });
      },
      { threshold: 0.12 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [prefersReducedMotion]);

  const delayMs = prefersReducedMotion ? 0 : Math.min(index, 20) * 70; // cap delay for safety

  const style: React.CSSProperties = {
    opacity: visible ? 1 : 0,
    transform: visible ? 'translateY(0)' : 'translateY(20px)',
    transition: prefersReducedMotion ? 'none' : 'opacity 450ms ease, transform 450ms ease',
    transitionDelay: `${visible ? delayMs : 0}ms`,
  };

  return (
    <article ref={ref} className="test-card" style={style}>
      <div className="test-card-header">
        <span className={`tag tag-${testCase.type}`}>{testCase.type.toUpperCase()}</span>
        <h3>{testCase.title}</h3>
      </div>

      <p>{testCase.description}</p>

      <CodeBlock label="Input" value={testCase.input} />
      <CodeBlock label="Expected Result" value={testCase.expectedResult} />

      {testCase.automationTemplate ? (
        <CodeBlock label="Automation Template" value={testCase.automationTemplate} />
      ) : null}
    </article>
  );
}
