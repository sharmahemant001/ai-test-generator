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
  return (
    <article className="test-card fade-in" style={{ animationDelay: `${Math.min(index, 12) * 35}ms` }}>
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
