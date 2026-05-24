from flask import Flask, request, jsonify
from flask_cors import CORS

# FIXED IMPORTS (remove backend.)
from services.parser import parse_requirements
from services.rule_engine import build_test_cases
from services.edge_case_generator import expand_edge_cases
from services.formatter import format_response
from utils.coverage import estimate_coverage

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)


@app.route("/", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "AI Test Case Generation Backend"
        }
    ), 200


@app.route("/generate", methods=["POST"])
def generate():

    data = request.get_json() or {}
    requirements = (data.get("requirements") or "").strip()

    if not requirements:
        return jsonify(
            {
                "error": "Requirements text is required.",
                "generated_tests": [],
            }
        ), 400

    constraints = parse_requirements(requirements)

    if constraints.get("error"):
        return jsonify(
            {
                "error": constraints["error"],
                "message": constraints.get(
                    "message",
                    "Provide API specs or feature requirements",
                ),
                "generated_tests": [],
            }
        ), 400

    baseline_cases = build_test_cases(
        requirements,
        constraints,
    )

    test_cases = expand_edge_cases(
        constraints,
        baseline_cases,
    )

    coverage_details = estimate_coverage(
        test_cases,
        constraints.get("fields", {}),
        constraints.get("success_condition", ""),
    )

    summary = (
        "Generated functional, boundary, negative, "
        "and edge-case tests from requirements."
    )

    response = format_response(
        summary,
        coverage_details["coverage_score"],
        test_cases,
    )

    response["coverage_details"] = coverage_details
    response["parsed_constraints"] = constraints

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
    )