import json
import os


def create_migration_map():
    """Create detailed file migration mapping"""
    migration_map = {
        "api": {},
        "core": {},
        "domain": {},
        "infrastructure": {},
        "shared": {},
    }

    # API migrations
    migration_map["api"] = {
        "backend/api/": "api/",
        "backend/fastapi_main.py": "api/main.py",
        "backend/app/main.py": "api/app.py",  # merge into main.py
        "backend/app/api_models.py": "api/models/",
        "backend/presentation/": "api/serializers/",
    }

    # Core migrations
    migration_map["core"] = {
        "backend/agents/core/": "core/agents/",
        "backend/agents/specialized/": "core/use_cases/",
        "backend/orchestration/": "core/workflows/",
        "backend/application/": "core/application/",
        "backend/services/": "core/services/",  # business logic only
        "backend/workflows/": "core/workflows/",
    }

    # Domain migrations
    migration_map["domain"] = {
        "backend/models/": "domain/models/",
        "backend/domain/": "domain/",
        "backend/core/models/": "domain/models/",
    }

    # Infrastructure migrations
    migration_map["infrastructure"] = {
        "backend/integrations/": "infrastructure/integrations/",
        "backend/mcp_servers/": "infrastructure/mcp_servers/",
        "backend/etl/": "infrastructure/etl/",
        "backend/monitoring/": "infrastructure/monitoring/",
        "backend/security/": "infrastructure/security/",
        "backend/database/": "infrastructure/database/",
        "backend/services/external/": "infrastructure/services/",
    }

    # Shared migrations
    migration_map["shared"] = {
        "backend/utils/": "shared/utils/",
        "backend/prompts/": "shared/prompts/",
        "backend/core/constants.py": "shared/constants.py",
        "backend/core/config.py": "shared/config.py",
        "backend/rag/": "shared/rag/",
    }

    # Save mapping
    os.makedirs("config", exist_ok=True)
    with open("config/migration_map.json", "w") as f:
        json.dump(migration_map, f, indent=2)

    return migration_map


def generate_file_list(migration_map):
    """Generate detailed file-by-file migration list"""
    file_migrations = []

    for layer, mappings in migration_map.items():
        for old_path, new_path in mappings.items():
            if os.path.exists(old_path):
                if os.path.isdir(old_path):
                    for root, _dirs, files in os.walk(old_path):
                        for file in files:
                            if file.endswith(".py"):
                                old_file = os.path.join(root, file)
                                new_file = old_file.replace(old_path, new_path)
                                file_migrations.append(
                                    {"old": old_file, "new": new_file, "layer": layer}
                                )
                else:
                    file_migrations.append(
                        {"old": old_path, "new": new_path, "layer": layer}
                    )

    with open("config/file_migrations.json", "w") as f:
        json.dump(file_migrations, f, indent=2)

    return file_migrations


if __name__ == "__main__":
    migration_map = create_migration_map()
    file_migrations = generate_file_list(migration_map)
