'use client';

import { useEffect, useMemo, useState } from 'react';
import RequirementInput from '../components/RequirementInput';
import GenerateButton from '../components/GenerateButton';
import TestCaseCard from '../components/TestCaseCard';
import CoverageScore from '../components/CoverageScore';
import LoadingSpinner from '../components/LoadingSpinner';
import Navbar from '../components/Navbar';
import { generateTestCases } from '../services/api';
import { TestCase, TestGenerationResponse } from '../types/testCase';

const loadingStages = [
  'Analyzing requirements...',
  'Parsing constraints...',
  'Generating boundary tests...',
  'Creating edge cases...',
  'Calculating coverage...',
];

const categoryLabels: Record<string, string> = {
  functional: 'Functional',
  boundary: 'Boundary',
  negative: 'Negative',
  edge: 'Edge',
  business_flow: 'Business Flow',
  validation: 'Validation',
};

function getConstraintCount(parsedConstraints?: TestGenerationResponse['parsed_constraints']) {
  if (!parsedConstraints?.fields) {
    return 0;
  }

  return Object.values(parsedConstraints.fields).reduce((count, config) => {
    const ruleCount = Object.keys(config || {}).length;
    return count + Math.max(ruleCount, 1);
  }, 0);
}

function describeRule(field: string, config: Record<string, unknown>) {
  if (config.type === 'email') {
    return `${field} -> valid format`;
  }
  if (typeof config.min_length === 'number') {
    return `${field} -> min length ${config.min_length}`;
  }
  if (typeof config.exact_length === 'number') {
    return `${field} -> exact length ${config.exact_length}`;
  }
  if (config.future_only) {
    return `${field} -> future date validation`;
  }
  if (config.required === false) {
    return `${field} -> optional`;
  }
  if (config.required === true) {
    return `${field} -> required`;
  }
  if (config.range && typeof config.range === 'object') {
    const range = config.range as { min?: number; max?: number };
    if (range.min !== undefined && range.max !== undefined) {
      return `${field} -> ${range.min}-${range.max}`;
    }
    return `${field} -> numeric boundaries`;
  }
  return `${field} -> validation rule`;
}

export default function HomePage() {
  const [requirements, setRequirements] = useState('');
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [summary, setSummary] = useState('');
  const [coverage, setCoverage] = useState(0);
  const [parsedConstraints, setParsedConstraints] = useState<TestGenerationResponse['parsed_constraints']>();
  const [coverageDetails, setCoverageDetails] = useState<TestGenerationResponse['coverage_details']>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [loadingIndex, setLoadingIndex] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      setLoadingIndex(0);
      return;
    }

    const interval = window.setInterval(() => {
      setLoadingIndex((current) => (current + 1) % loadingStages.length);
    }, 700);

    return () => window.clearInterval(interval);
  }, [isLoading]);

  const constraintCount = useMemo(() => getConstraintCount(parsedConstraints), [parsedConstraints]);
  const categoryCounts = useMemo(() => {
    return testCases.reduce<Record<string, number>>((counts, testCase) => {
      counts[testCase.type] = (counts[testCase.type] || 0) + 1;
      return counts;
    }, {});
  }, [testCases]);
  const categoriesCovered = useMemo(() => {
    if (coverageDetails?.category_coverage) {
      return Object.values(coverageDetails.category_coverage).filter(Boolean).length;
    }
    return Object.values(categoryCounts).filter((count) => count > 0).length;
  }, [categoryCounts, coverageDetails]);
  const detectedFields = parsedConstraints?.fields ? Object.keys(parsedConstraints.fields) : [];
  const detectedRules = parsedConstraints?.fields
    ? Object.entries(parsedConstraints.fields).map(([field, config]) => describeRule(field, config))
    : [];
  const hasUnderstanding = detectedFields.length > 0 || detectedRules.length > 0;
  const dynamicSummary = testCases.length
    ? `Generated ${testCases.length} test cases with ${coverage}% coverage across ${constraintCount} parsed constraints. Includes ${[
        categoryCounts.boundary ? 'boundary tests' : '',
        categoryCounts.negative ? 'negative tests' : '',
        categoryCounts.business_flow ? 'business flow tests' : '',
        categoryCounts.edge ? 'edge cases' : '',
      ]
        .filter(Boolean)
        .join(', ')}.`
    : summary;

  const handleGenerate = async () => {
    if (!requirements.trim()) {
      setError('Please provide requirements or API specification text.');
      setSummary('');
      setTestCases([]);
      setCoverage(0);
      setParsedConstraints(undefined);
      setCoverageDetails(undefined);
      return;
    }

    setError('');
    setSummary('');
    setTestCases([]);
    setCoverage(0);
    setParsedConstraints(undefined);
    setCoverageDetails(undefined);
    setIsLoading(true);

    try {
      const response = await generateTestCases(requirements.trim());
      setSummary(response.summary || 'Generated test cases based on your requirements.');
      setTestCases(response.testCases || []);
      setCoverage(response.coverage ?? Math.min(100, 40 + (response.testCases?.length || 0) * 10));
      setParsedConstraints(response.parsed_constraints);
      setCoverageDetails(response.coverage_details);
    } catch (err) {
      setError('Try improving requirements or retry.');
      setSummary('');
      setTestCases([]);
      setCoverage(0);
      setParsedConstraints(undefined);
      setCoverageDetails(undefined);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="page-shell">
      <Navbar />

      <section className="hero-panel">
        <div className="hero-copy">
          <h1>AI Test Case Generation</h1>
          <p>Paste requirements, API specs, or feature stories and generate comprehensive test cases instantly.</p>
        </div>

        <div className="architecture-visual" aria-hidden="true">
          {['Requirements', 'Parser', 'Rule Engine', 'AI Generator', 'Coverage Engine', 'Test Cases'].map((item, index) => (
            <div className="architecture-step" key={item}>
              <span>{item}</span>
              {index < 5 ? <b>↓</b> : null}
            </div>
          ))}
        </div>

        <div className="action-panel">
          <RequirementInput value={requirements} onChange={setRequirements} />
          <GenerateButton onClick={handleGenerate} disabled={isLoading} label={loadingStages[loadingIndex]} />
          {error ? (
            <div className="error-card" role="alert">
              <strong>Warning</strong>
              <h2>Unable to generate test cases</h2>
              <p>{error}</p>
            </div>
          ) : null}
        </div>
      </section>

      {isLoading ? (
        <div className="loading-panel">
          <LoadingSpinner />
          <p>{loadingStages[loadingIndex]}</p>
        </div>
      ) : null}

      {!isLoading && !error && !testCases.length ? (
        <section className="empty-state">
          <div className="empty-illustration" aria-hidden="true">
            <span>QA</span>
            <i />
            <i />
            <i />
          </div>
          <p>Paste requirements, API specs, or feature stories to generate test coverage instantly.</p>
        </section>
      ) : null}

      {hasUnderstanding ? (
        <section className="understanding-panel fade-in">
          <div>
            <span className="panel-kicker">AI Understanding</span>
            <h2>Detected constraints extracted from requirements</h2>
          </div>
          <div className="understanding-grid">
            <div>
              <h3>Detected Fields</h3>
              <div className="field-list">
                {detectedFields.map((field) => (
                  <span key={field}>✓ {field}</span>
                ))}
              </div>
            </div>
            <div>
              <h3>Detected Rules</h3>
              <div className="rule-list">
                {detectedRules.map((rule) => (
                  <span key={rule}>✓ {rule}</span>
                ))}
                {parsedConstraints?.success_condition ? <span>✓ Business flow validation</span> : null}
              </div>
            </div>
          </div>
        </section>
      ) : null}

      {summary && testCases.length > 0 ? (
        <section className="summary-panel">
          <h2>Quick Summary</h2>
          <p>{dynamicSummary}</p>
        </section>
      ) : null}

      {testCases.length > 0 ? (
        <section className="results-panel">
          <div className="results-header">
            <div>
              <h2>Generated Test Cases</h2>
              <div className="category-chips">
                {Object.entries(categoryLabels).map(([key, label]) =>
                  categoryCounts[key] ? (
                    <span className={`category-chip chip-${key}`} key={key}>
                      {label} {categoryCounts[key]}
                    </span>
                  ) : null,
                )}
              </div>
            </div>
            <CoverageScore
              count={testCases.length}
              score={coverage}
              constraintsParsed={constraintCount}
              categoriesCovered={categoriesCovered}
            />
          </div>

          <div className="cards-grid">
            {testCases.map((testCase, index) => (
              <TestCaseCard key={testCase.id} testCase={testCase} index={index} />
            ))}
          </div>
        </section>
      ) : null}
    </main>
  );
}
