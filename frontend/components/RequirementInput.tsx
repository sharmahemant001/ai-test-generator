type RequirementInputProps = {
  value: string;
  onChange: (value: string) => void;
};

export default function RequirementInput({ value, onChange }: RequirementInputProps) {
  return (
    <label className="input-group">
      <span>Paste API requirements, feature rules, or business validation logic</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={`Signup API\n\nFields:\nemail\npassword\nphone\n\nRules:\nEmail valid\nPassword minimum 8 characters\nPhone exactly 10 digits\n\nSignup succeeds only when all fields are valid`}
      />
      <span className="char-counter">{value.length} chars</span>
    </label>
  );
}
