# Employability scoring contract

The salary model and the employability score are separate systems.

The employability score is a deterministic readiness indicator. It is not a
validated psychometric or hiring prediction. Its weights live in
`config/employability_weights.json` so they can be reviewed and changed
without changing the ML/DVC pipeline.

Each component is normalized to 0–100:

- Technical skills: average of the student's declared skill levels on the
  frontend 0–5 scale.
- Assessment: latest completed assessment percentage, or 0 when there is no
  completed assessment.
- Academic: CGPA normalized against 10.
- Projects: up to three documented projects.
- Certifications: up to two documented certifications.
- Internships: 100 when at least one internship is documented, otherwise 0.
- Profile completeness: normalized completion percentage.

The weighted sum is rounded to the nearest whole number. Missing evidence is
shown as missing evidence; it is not replaced with salary-model output or
fabricated history.

Readiness bands are presentation labels only:

- 80–100: Band A / Job-ready
- 60–79: Band B / Near-ready
- 0–59: Band C / Building