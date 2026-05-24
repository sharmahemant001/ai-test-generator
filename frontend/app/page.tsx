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
  'Parsing Constraints',
  'Generating Boundary Tests',
  'Expanding Edge Cases',
  'Coverage Analysis',
];

const categoryLabels: Record<string, string> = {
  functional: 'Functional',
  boundary: 'Boundary',
  negative: 'Negative',
  edge: 'Edge',
  business_flow: 'Business Flow',
  validation: 'Validation',
};

const exampleRequirements: Record<string, string> = {
  Signup: `Signup API
Fields:
email
password
phone

Rules:
Email valid
Password minimum 8 characters
Phone exactly 10 digits

Signup succeeds only when all fields are valid`,
  Payment: `Payment API
Fields:
amount
currency
coupon

Rules:
Amount > 0
Maximum amount 50000
Currency required
Coupon optional

Payment succeeds only when validations pass`,
  Checkout: `Checkout API
Fields:
customerEmail
deliveryAddress
contactNumber

Rules:
Email valid
Address required
Phone exactly 10

Checkout succeeds only when validations pass`,
};

function getConstraintCount(
  parsedConstraints?: TestGenerationResponse['parsed_constraints']
) {

  if (!parsedConstraints?.fields) {
    return 0;
  }

  return Object.values(
    parsedConstraints.fields
  ).reduce((count, config) => {

    const ruleCount =
      Object.keys(config || {}).length;

    return count + Math.max(ruleCount,1);

  },0);

}

function describeRule(
  field:string,
  config:Record<string,unknown>
){

  if(config.type==='email'){
    return `${field} → valid format`;
  }

  if(typeof config.min_length==='number'){
    return `${field} → min length ${config.min_length}`;
  }

  if(typeof config.exact_length==='number'){
    return `${field} → exact length ${config.exact_length}`;
  }

  if(config.future_only){
    return `${field} → future only`;
  }

  if(config.required===false){
    return `${field} → optional`;
  }

  if(config.required===true){
    return `${field} → required`;
  }

  if(config.range){

    const range =
      config.range as {
        min?:number;
        max?:number;
      };

    if(
      range.min!==undefined &&
      range.max!==undefined
    ){

      return `${field} → ${range.min}-${range.max}`;

    }

  }

  return `${field} → validation`;

}

export default function HomePage(){

const [
requirements,
setRequirements
]=useState('');

const [
testCases,
setTestCases
]=useState<TestCase[]>([]);

const [
summary,
setSummary
]=useState('');

const [
coverage,
setCoverage
]=useState(0);

const [parsedConstraints, setParsedConstraints] = useState<TestGenerationResponse['parsed_constraints']>();

const [coverageDetails, setCoverageDetails] = useState<TestGenerationResponse['coverage_details']>();

const [
isLoading,
setIsLoading
]=useState(false);

const [
error,
setError
]=useState('');

const [
loadingIndex,
setLoadingIndex
]=useState(0);

const [
selectedCategory,
setSelectedCategory
]=useState('ALL');

useEffect(()=>{

if(!isLoading){

setLoadingIndex(0);

return;

}

const interval =
window.setInterval(()=>{

setLoadingIndex(
(current)=>
(current+1)
%
loadingStages.length
);

},700);

return ()=>window.clearInterval(interval);

},[isLoading]);

const constraintCount =
useMemo(
()=>getConstraintCount(parsedConstraints),
[parsedConstraints]
);

const categoryCounts =
useMemo(()=>{

return testCases.reduce<
Record<string,number>
>((counts,test)=>{

counts[test.type]=
(counts[test.type]||0)+1;

return counts;

},{});

},[testCases]);

const filteredTestCases =
  selectedCategory === 'ALL'
    ? testCases
    : testCases.filter((test) => test.type.toUpperCase() === selectedCategory);

const categoriesCovered =
useMemo(()=>{

if(
coverageDetails?.category_coverage
){

return Object
.values(
coverageDetails
.category_coverage
)
.filter(Boolean)
.length;

}

return Object
.values(categoryCounts)
.filter(
count=>count>0
)
.length;

},
[
categoryCounts,
coverageDetails
]
);

const detectedFields =
parsedConstraints?.fields
?
Object.keys(
parsedConstraints.fields
)
:
[];

const detectedRules =
parsedConstraints?.fields
?
Object.entries(
parsedConstraints.fields
)
.map(
([field,config])=>
describeRule(
field,
config
)
)
:
[];

const hasParserOutput =
detectedRules.length > 0 ||
!!parsedConstraints?.success_condition;

const dynamicSummary =
testCases.length

?

`Generated
${testCases.length}
test cases with
${coverage}% coverage
across
${constraintCount}
parsed constraints.`

:

summary;

const showEmptyState =
!testCases.length && !isLoading && !error;

const parserErrorDetails =
error.includes('Provide API fields')
? [
  'API fields',
  'Validation rules',
  'Feature requirements',
]
: [];

const downloadJson = () => {
  const payload = {
    summary,
    coverage,
    coverage_details: coverageDetails,
    parsed_constraints: parsedConstraints,
    testCases,
  };

  const blob = new Blob(
    [JSON.stringify(payload, null, 2)],
    { type: 'application/json' }
  );

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'generated_tests.json';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

const handleGenerate = async () => {
  if (!requirements.trim()) {
    setError('Please provide requirements.');
    return;
  }

  setError('');
  setIsLoading(true);

  try {
    const response = await generateTestCases(requirements);
    setSummary(response.summary);
    setTestCases(response.testCases || []);
    setCoverage(response.coverage || 0);
    setParsedConstraints(response.parsed_constraints);
    setCoverageDetails(response.coverage_details);
  } catch (error) {
    setError(error instanceof Error ? error.message : 'Unable to generate test cases');
  } finally {
    setIsLoading(false);
  }
};

return (
  <main className="page-shell">

<Navbar />
  <section className="hero-panel hero-premium">
    <div className="hero-left">
      <div className="hero-top">
        <span className="badge">⚡ Hackathon Demo Ready</span>
        <h1 className="hero-title">AI Test Case Generation Agent</h1>
        <p className="hero-sub">Generate Functional, Boundary, Negative, Edge, and Business Flow test cases instantly.</p>
        <div className="value-chips">
          <span className="chip small">Constraint Parser</span>
          <span className="chip small">Coverage Engine</span>
          <span className="chip small">Rule Engine</span>
          <span className="chip small">Export JSON</span>
        </div>
      </div>

      <div className="hero-action">
        <div className="input-card">
          <RequirementInput value={requirements} onChange={setRequirements} />
        </div>

        <div className="right-controls">
          <div className="examples-card">
            <h4>Try Examples</h4>
            <div className="example-buttons">
              {Object.entries(exampleRequirements).map(([name, value]) => (
                <button
                  key={name}
                  type="button"
                  className="example-button"
                  onClick={() => setRequirements(value)}
                >
                  {name}
                </button>
              ))}
            </div>
          </div>

          <div className="action-cta">
            <GenerateButton onClick={handleGenerate} disabled={isLoading} label={loadingStages[loadingIndex]} />
            <button className="export-quick" onClick={downloadJson}>Export JSON</button>
          </div>
        </div>
      </div>
    </div>

    <aside className="architecture-visual">
      <div className="arch-node">Requirements</div>
      <div className="arch-arrow">↓</div>
      <div className="arch-node">Constraint Parser</div>
      <div className="arch-arrow">↓</div>
      <div className="arch-node">Rule Engine</div>
      <div className="arch-arrow">↓</div>
      <div className="arch-node">Edge Generator</div>
      <div className="arch-arrow">↓</div>
      <div className="arch-node">Coverage Engine</div>
      <div className="arch-arrow">↓</div>
      <div className="arch-node">Export</div>
    </aside>
  </section>

<section className="example-section">
  <h3 className="example-title">Try examples</h3>
  <div className="example-buttons">
    {Object.entries(exampleRequirements).map(([name, value]) => (
      <button
        key={name}
        type="button"
        className="example-button"
        onClick={() => setRequirements(value)}
      >
        {name}
      </button>
    ))}
  </div>
</section>

<RequirementInput value={requirements} onChange={setRequirements} />

<GenerateButton
  onClick={handleGenerate}
  disabled={isLoading}
  label={loadingStages[loadingIndex]}
/>

{showEmptyState && (
  <section className="empty-state">
    <div>
      <h2>Ready to generate your first test suite</h2>
      <p>
        Paste API requirements and let the parser infer fields, validation rules, and business flow.
      </p>
    </div>
    <div className="empty-actions">
      {Object.keys(exampleRequirements).map((name) => (
        <button
          key={name}
          type="button"
          className="example-button"
          onClick={() => setRequirements(exampleRequirements[name])}
        >
          {name} example
        </button>
      ))}
    </div>
  </section>
)}

{error && (
  <div className="error-card">
    <p className="error-title">⚠ {error}</p>
    {parserErrorDetails.length > 0 && (
      <div className="error-details">
        <p>Please provide:</p>

  
        <ul>
          {parserErrorDetails.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)}

{isLoading && (
  <div className="loading-panel">
    <LoadingSpinner />
    <div className="loading-copy">
      <p>{loadingStages[loadingIndex]}</p>
      <div className="loading-steps">
        {loadingStages.map((stage, index) => (
          <span
            key={stage}
            className={index === loadingIndex ? 'loading-step active' : 'loading-step'}
          >
            {stage}
          </span>
        ))}
      </div>
    </div>
  </div>
)}

{hasParserOutput && (
  <section className="understanding-panel">
    <div className="understanding-header">
      <h2>Constraint Parser Output</h2>
      <p>Detected fields and validation rules from your description.</p>
    </div>
    <div className="rule-list">
      {detectedRules.map((rule) => (
        <span key={rule}>✓ {rule}</span>
      ))}
      {parsedConstraints?.success_condition ? <span>✓ business flow validation</span> : null}
    </div>
  </section>
)}

{!!testCases.length && (
  <section className="results-panel">

<div className="results-header">

<div>

<h2>Generated Test Cases</h2>

<div className="filter-row">

<button
  onClick={() => setSelectedCategory('ALL')}
  className={`filter-chip filter-chip-all ${selectedCategory === 'ALL' ? 'active' : ''}`}
>
  All ({testCases.length})
</button>

{Object.entries(categoryLabels).map(([key, label]) =>
  categoryCounts[key] ? (
    <button
      key={key}
      onClick={() => setSelectedCategory(key.toUpperCase())}
      className={`filter-chip filter-chip-${key} ${
        selectedCategory === key.toUpperCase() ? 'active' : ''
      }`}
    >
      {label} ({categoryCounts[key]})
    </button>
  ) : null
)}

</div>

</div>

<div className="results-side">
  <CoverageScore
    count={testCases.length}
    score={coverage}
    constraintsParsed={constraintCount}
    categoriesCovered={categoriesCovered}
  />
  <button
    type="button"
    className="export-button"
    onClick={downloadJson}
  >
    Export JSON
  </button>
</div>

</div>

<p>

{dynamicSummary}

</p>

<div className="cards-grid">
  {filteredTestCases.map((test, index) => (
    <TestCaseCard key={test.id} testCase={test} index={index} />
  ))}
</div>

</section>
)}

  <Footer />
</main>
);
}

function Footer() {
  return (
    <footer className="app-footer">
      <div>
        <strong>AI Test Case Generation Agent</strong>
        <div>Constraint Parser • Rule Engine • Coverage Engine • Edge Case Generator</div>
      </div>
      <div style={{ opacity: 0.85 }}>Built for Agentic AI Hackathon</div>
    </footer>
  );
}
