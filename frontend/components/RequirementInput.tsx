type RequirementInputProps = {
  value: string;
  onChange: (value: string) => void;
};

export default function RequirementInput({ value, onChange }: RequirementInputProps) {
  return (
    <label className="input-group">
      <span>Paste requirements or API spec</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={`Signup API

Fields:

email

password

phone

Rules:

Email valid

Password minimum 8 characters

Phone exactly 10 digits

Signup succeeds only when all fields are valid`}
      />
      <span className="char-counter">{value.length} chars</span>
    </label>
  );
}
