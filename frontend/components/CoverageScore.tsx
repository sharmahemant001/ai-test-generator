type CoverageScoreProps = {
  count: number;
  score: number;
  constraintsParsed?: number;
  categoriesCovered?: number;
};

export default function CoverageScore({ count, score, constraintsParsed = 0, categoriesCovered = 0 }: CoverageScoreProps) {
  return (
    <div className="coverage-score">
      <div className="coverage-topline">
        <span className="coverage-label">Coverage</span>
        <strong>{score}%</strong>
      </div>
      <div className="coverage-metrics">
        <span>{count} Tests Generated</span>
        <span>{constraintsParsed} Constraints Parsed</span>
        <span>{categoriesCovered} Categories Covered</span>
      </div>
      <div className="coverage-bar">
        <div className="coverage-fill" style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}
