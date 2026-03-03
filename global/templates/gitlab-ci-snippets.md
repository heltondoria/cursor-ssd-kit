# GitLab CI Snippets

Reference snippets for `.gitlab-ci.yml` using the pipeline-components.

## Python Library (Pyright Strict)

```yaml
include:
  - component: $CI_SERVER_FQDN/luxtekna/devops/pipeline-components/templates/library-python-pyright@v1.9.0
    inputs:
      python_version: "3.12"
      package_manager: uv
      coverage_threshold: 100
      test_args: "--junitxml=report.xml --cov=<package_name> --cov-report=xml:coverage.xml --cov-report=term"
      enable_ruff: true
      enable_ruff_format: true
      enable_pyright: true
      pyright_args: "src/"
      enable_xenon: true
      xenon_args: "--max-absolute A --max-modules A --max-average A src/"
      enable_vulture: true
      vulture_args: "src/<package_name>"
      enable_pypi: false
      enable_gitlab_registry: true
      verify_version: true
      lint_config_mode: project
```

## Python Microservice

```yaml
include:
  - component: $CI_SERVER_FQDN/luxtekna/devops/pipeline-components/templates/microservice-python@v1.9.0
    inputs:
      python_version: "3.12"
      package_manager: uv
      coverage_threshold: 100
      enable_ruff: true
      enable_ruff_format: true
      enable_pyright: true
      pyright_args: "src/"
      enable_xenon: true
      enable_vulture: true
      enable_sast: true
      enable_dependency_scan: true
      enable_secret_detection: true
      enable_container_scan: true
      lint_config_mode: project
```

## Notes

- `lint_config_mode: project` uses the project's own `pyproject.toml` ruff/pyright config (our golden config)
- `lint_config_mode: enforced` uses centralized configs from the lint Docker image (overrides project config)
- For new projects using the golden `pyproject.toml` template, `project` mode is recommended since configs are already strict
- TypeScript pipeline components are not yet available (planned in pipeline-components roadmap)
