import json
from pathlib import Path

import allure
from jsonschema import validate, ValidationError

from utils.logger import get_logger

logger = get_logger(__name__)

SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"
_schema_cache: dict = {}


def validate_schema(response_json: dict, schema_filename: str) -> bool:
    """Validate a JSON response against a JSON Schema file.

    Schemas are cached after first load to avoid repeated disk I/O.
    """
    if schema_filename not in _schema_cache:
        schema_path = SCHEMAS_DIR / schema_filename
        with open(schema_path, "r") as f:
            _schema_cache[schema_filename] = json.load(f)

    schema = _schema_cache[schema_filename]

    try:
        validate(instance=response_json, schema=schema)
        logger.info(f"Schema validation passed for {schema_filename}")
        allure.attach(
            json.dumps(response_json, indent=2),
            name="Validated Response",
            attachment_type=allure.attachment_type.JSON,
        )
        return True
    except ValidationError as e:
        logger.error(f"Schema validation failed: {e.message}")
        allure.attach(
            f"Schema: {schema_filename}\nError: {e.message}\nPath: {list(e.path)}",
            name="Schema Validation Error",
            attachment_type=allure.attachment_type.TEXT,
        )
        raise
