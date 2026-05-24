import { ApiErrorResponse, TestGenerationResponse } from '../types/testCase';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function generateTestCases(requirements: string): Promise<TestGenerationResponse> {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ requirements }),
  });

  if (!response.ok) {
    const errorBody = (await response.json().catch(() => ({}))) as ApiErrorResponse;
    throw new Error(errorBody.message || errorBody.error || 'Failed to generate test cases');
  }

  return response.json();
}
