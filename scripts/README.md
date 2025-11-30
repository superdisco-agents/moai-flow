# MoAI Flow Scripts

Utility scripts for development, migration, validation, and maintenance.

## Directory Structure

```
scripts/
├── dev/               # Development utilities
├── migration/         # Migration and conversion scripts
├── validation/        # Validation and verification scripts
└── maintenance/       # Maintenance and cleanup scripts
```

## Development Scripts (dev/)

Scripts for development workflows:
- Environment setup
- Dependency management
- Local testing
- Development server

## Migration Scripts (migration/)

Scripts for data and code migration:
- Package structure migration
- Data format conversion
- Version upgrades
- Legacy code migration

## Validation Scripts (validation/)

Scripts for validation and verification:
- Configuration validation
- Code quality checks
- Dependency audits
- Security scans

## Maintenance Scripts (maintenance/)

Scripts for system maintenance:
- Log cleanup
- Cache management
- Backup and restore
- Health checks

## Usage

### Run Development Setup

```bash
python scripts/dev/setup_dev_environment.py
```

### Run Migration

```bash
python scripts/migration/migrate_package_structure.py
```

### Run Validation

```bash
python scripts/validation/validate_config.py
```

### Run Maintenance

```bash
python scripts/maintenance/cleanup_logs.py
```

## Contributing

When adding new scripts:
1. Place in appropriate directory
2. Add docstring and usage instructions
3. Update this README
4. Add to relevant CI/CD pipelines
