import { ApiErrorResponse, TestGenerationResponse } from '../types/testCase';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  'https://ai-test-generator-fc41.onrender.com';

export async function generateTestCases(
  requirements: string
): Promise<TestGenerationResponse> {

  if (!API_BASE_URL) {
    throw new Error(
      'Backend unavailable. Please try again.'
    );
  }

  const controller = new AbortController();

  const timeoutId = window.setTimeout(
    () => controller.abort(),
    15000
  );

  try {

    const response = await fetch(
      `${API_BASE_URL}/generate`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          requirements,
        }),
        signal: controller.signal,
      }
    );

    // FIX:
    // READ RESPONSE ONLY ONCE

    const result =
      (await response
        .json()
        .catch(() => ({}))) as
      TestGenerationResponse &
      ApiErrorResponse;

    if (!response.ok) {

      if (response.status === 400) {

        throw new Error(
          result.message ||
          result.error ||
          'Unable to extract requirements'
        );

      }

      if (response.status >= 500) {

        throw new Error(
          'Server error. Try again.'
        );

      }

      throw new Error(
        result.message ||
        result.error ||
        'Failed to generate test cases'
      );

    }

    return result;

  } catch (error) {

    if (error instanceof Error) {

      if (
        error.name === 'AbortError'
      ) {

        throw new Error(
          'Backend unavailable'
        );

      }

      if (
        error.message === 'Failed to fetch' ||
        error.message.includes(
          'NetworkError'
        )
      ) {

        throw new Error(
          'Backend unavailable'
        );

      }

      throw error;

    }

    throw new Error(
      'Backend unavailable'
    );

  } finally {

    window.clearTimeout(
      timeoutId
    );

  }

}