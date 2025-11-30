# Migration Scripts

Scripts for data and code migration tasks.

## Available Scripts

### migrate_package_structure.py
Migrate package structure from old layout to new layout.

```bash
python scripts/migration/migrate_package_structure.py
python scripts/migration/migrate_package_structure.py --dry-run
```

### convert_config_format.py
Convert configuration files between formats.

```bash
python scripts/migration/convert_config_format.py config.json config.yaml
```

### upgrade_dependencies.py
Upgrade dependencies to latest compatible versions.

```bash
python scripts/migration/upgrade_dependencies.py
python scripts/migration/upgrade_dependencies.py --check
```

### migrate_tests.py
Migrate tests to new structure.

```bash
python scripts/migration/migrate_tests.py
```

## Usage Examples

### Full Migration Workflow

```bash
# Dry run to preview changes
python scripts/migration/migrate_package_structure.py --dry-run

# Execute migration
python scripts/migration/migrate_package_structure.py

# Migrate tests
python scripts/migration/migrate_tests.py

# Upgrade dependencies
python scripts/migration/upgrade_dependencies.py
```

### Rollback

Most migration scripts support rollback:

```bash
python scripts/migration/migrate_package_structure.py --rollback
```
