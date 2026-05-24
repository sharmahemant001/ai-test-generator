type GenerateButtonProps = {
  onClick: () => void;
  disabled?: boolean;
  label?: string;
};

export default function GenerateButton({ onClick, disabled, label }: GenerateButtonProps) {
  return (
    <button className="generate-button" onClick={onClick} disabled={disabled}>
      {disabled ? <span className="button-spinner" aria-hidden="true" /> : null}
      <span>{disabled ? label || 'Generating...' : 'Generate Test Cases'}</span>
    </button>
  );
}
