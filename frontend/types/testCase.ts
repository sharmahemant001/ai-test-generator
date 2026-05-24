export type TestCaseType = 'functional' | 'boundary' | 'negative' | 'edge' | 'validation' | 'business_flow';

export interface TestCase {
  id: string;
  type: TestCaseType;
  title: string;
  description: string;
  input: string;
  expectedResult: string;
  automationTemplate?: string;
}

export interface TestGenerationResponse {
  summary: string;
  coverage: number;
  testCases: TestCase[];
  coverage_details?: {
    category_coverage?: Record<string, boolean>;
    field_coverage?: Record<string, boolean>;
    business_flow_coverage?: boolean;
  };
  parsed_constraints?: {
    fields?: Record<string, Record<string, unknown>>;
    success_condition?: string;
  };
}

export interface ApiErrorResponse {
  error?: string;
  message?: string;
  generated_tests?: TestCase[];
}
