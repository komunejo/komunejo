#!/usr/bin/env python3
"""entity_lint.py — deterministic integrity engine for entity-managed Markdown projects.

This engine is GENERIC and STABLE: it knows nothing about any particular domain.
It reads schema declarations (YAML files) and validates entity records
(Markdown files with YAML frontmatter) against them. Schema evolution never
requires touching this script — schemas are data, this engine is infrastructure.

Commands:
    validate [paths...]   Validate schemas + all (or selected) entity files. Exit 1 on errors.
    index                 Print a Markdown index of all entities (--write to save INDEX.md).
    new <entity>          Print a stub record for a new entity with the next free ID.

Options:
    --root DIR            Project root (default: auto-detect by walking up from cwd
                          looking for entity-manager.yaml or a schemas/ directory).
    --json                Machine-readable output (for hooks).
    --write PATH          For `index`: write output to PATH instead of stdout.
    --title TEXT          For `new`: set the title field.

Exit codes: 0 = OK, 1 = integrity errors found, 2 = usage/configuration error.

Only dependency: PyYAML.
"""

import argparse
import datetime
import io
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "entity_lint: PyYAML is required. Install with: pip install pyyaml\n")
    sys.exit(2)

ENGINE_VERSION = "0.4.0"
CONFIG_FILENAME = "entity-manager.yaml"
DEFAULT_SCHEMAS_DIR = "schemas"
DEFAULT_ENTITIES_DIR = "entities"
RESERVED_FIELDS = {"id", "entity"}
VALID_TYPES = {"string", "text", "integer", "number", "boolean",
               "date", "datetime", "enum", "ref", "list"}
VALID_FIELD_KEYS = {"type", "required", "values", "entity", "items",
                    "min", "max", "pattern", "description", "default"}
BASE_FIELD_KEYS = {"type", "required", "description", "default"}
TYPE_SPECIFIC_KEYS = {
    "string": {"pattern"}, "text": {"pattern"},
    "integer": {"min", "max"}, "number": {"min", "max"},
    "boolean": set(), "date": set(), "datetime": set(),
    "enum": {"values"}, "ref": {"entity"}, "list": {"items"},
}
VALID_SCHEMA_KEYS = {"entity", "description", "id", "dir", "path", "strict", "fields", "constraints"}
VALID_CONSTRAINT_RULES = {"max_count_per", "unique"}
VALID_ID_KEYS = {"prefix", "width"}
INLINE_REF_RE = re.compile(r"\[\[([A-Za-z][A-Za-z0-9]*-\d+)(?:\|[^\]\n]*)?\]\]")
ID_RE_TEMPLATE = r"^{prefix}-\d{{{width},}}$"
FRONTMATTER_DELIM = "---"


class Issue:
    def __init__(self, level, file, message, field=None):
        self.level = level          # "error" | "warning"
        self.file = str(file)
        self.message = message
        self.field = field

    def to_dict(self):
        d = {"level": self.level, "file": self.file, "message": self.message}
        if self.field:
            d["field"] = self.field
        return d

    def __str__(self):
        loc = f"{self.file}"
        if self.field:
            loc += f" [{self.field}]"
        return f"{self.level.upper():7s} {loc}: {self.message}"


class Project:
    """Loaded project: config, schemas, entity files."""

    def __init__(self, root):
        self.root = Path(root)
        self.issues = []
        self.config = self._load_config()
        for key, default in (("schemas_dir", DEFAULT_SCHEMAS_DIR),
                             ("entities_dir", DEFAULT_ENTITIES_DIR)):
            value = self.config.get(key, default)
            if not isinstance(value, str) or not value:
                self.error(self.root / CONFIG_FILENAME,
                           f"config key '{key}' must be a non-empty string, got {value!r} "
                           f"— falling back to default '{default}'")
                self.config[key] = default
        self.schemas_dir = self.root / self.config.get("schemas_dir", DEFAULT_SCHEMAS_DIR)
        self.entities_dir = self.root / self.config.get("entities_dir", DEFAULT_ENTITIES_DIR)
        self.schemas = {}           # entity name -> schema dict
        self.prefix_to_entity = {}  # "DEC" -> "decision"
        self.dir_to_entity = {}     # resolved records location (posix) -> entity name
        self.records = {}           # id -> {"entity":, "file":, "fields":, "body":}

    def _read_text(self, path):
        """Read a file as UTF-8, tolerating a Windows BOM. Returns None (and records an error) on undecodable or unreadable files — a crash is always worse than a violation report."""
        try:
            return Path(path).read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError) as e:
            self.error(path, f"cannot read file as UTF-8 text: {e}")
            return None

    def _load_config(self):
        cfg_path = self.root / CONFIG_FILENAME
        if not cfg_path.exists():
            return {}
        try:
            text = cfg_path.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError) as e:
            self.issues.append(Issue("error", cfg_path, f"cannot read config as UTF-8 text: {e}"))
            return {}
        try:
            data = yaml.safe_load(text) or {}
            if not isinstance(data, dict):
                self.error(cfg_path, "config must be a YAML mapping")
                return {}
            return data
        except yaml.YAMLError as e:
            self.error(cfg_path, f"config is not valid YAML: {e}")
            return {}

    def error(self, file, message, field=None):
        self.issues.append(Issue("error", self._rel(file), message, field))

    def warn(self, file, message, field=None):
        self.issues.append(Issue("warning", self._rel(file), message, field))

    def _rel(self, path):
        try:
            return Path(path).relative_to(self.root)
        except ValueError:
            return Path(path)

    # ---------------- schema loading & meta-validation ----------------

    def load_schemas(self):
        if not self.schemas_dir.is_dir():
            self.error(self.schemas_dir,
                       "schemas directory not found — is this an entity-managed project?")
            return
        for path in sorted(self.schemas_dir.glob("*.yaml")) + sorted(self.schemas_dir.glob("*.yml")):
            text = self._read_text(path)
            if text is None:
                continue
            try:
                data = yaml.safe_load(text)
            except yaml.YAMLError as e:
                self.error(path, f"schema is not valid YAML: {e}")
                continue
            if not isinstance(data, dict):
                self.error(path, "schema must be a YAML mapping")
                continue
            self._check_schema(path, data)

    def _check_schema(self, path, data):
        for key in data:
            if key not in VALID_SCHEMA_KEYS:
                self.error(path, f"unknown schema key '{key}' "
                                 f"(valid: {', '.join(sorted(VALID_SCHEMA_KEYS))})")
        name = data.get("entity")
        if not isinstance(name, str) or not name:
            self.error(path, "schema needs an 'entity' name (string)")
            return
        if name != path.stem:
            self.error(path, f"schema entity '{name}' should match filename '{path.stem}.yaml'")
        if name in self.schemas:
            self.error(path, f"duplicate schema for entity '{name}'")
            return

        id_spec = data.get("id")
        if not isinstance(id_spec, dict) or "prefix" not in id_spec:
            self.error(path, "schema needs an 'id:' mapping with at least a 'prefix'")
            return
        for key in id_spec:
            if key not in VALID_ID_KEYS:
                self.error(path, f"unknown id key '{key}' (valid: prefix, width)")
        prefix = id_spec["prefix"]
        if not isinstance(prefix, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", prefix):
            self.error(path, f"id prefix must be alphanumeric starting with a letter, got {prefix!r}")
            return
        if prefix in self.prefix_to_entity:
            self.error(path, f"id prefix '{prefix}' already used by entity "
                             f"'{self.prefix_to_entity[prefix]}' — prefixes must be unique")
            return
        width = id_spec.get("width", 3)
        if not isinstance(width, int) or width < 1:
            self.error(path, f"id width must be a positive integer, got {width!r}")
            width = 3

        dir_val = data.get("dir", name)
        if not isinstance(dir_val, str) or not dir_val:
            self.error(path, f"'dir' must be a non-empty string, got {dir_val!r}")
            return
        path_val = data.get("path")
        if path_val is not None:
            if not isinstance(path_val, str) or not path_val:
                self.error(path, f"'path' must be a non-empty string, got {path_val!r}")
                return
            rel = Path(path_val)
            if rel.is_absolute() or ".." in rel.parts:
                self.error(path, f"'path' must be relative to the project root, "
                                 f"without '..': {path_val!r}")
                return
            type_dir = self.root / rel
        else:
            type_dir = self.entities_dir / dir_val
        loc_key = type_dir.resolve().as_posix()
        for other_key, other_name in self.dir_to_entity.items():
            if other_key == loc_key:
                self.error(path, f"records location '{type_dir}' already used by entity "
                                 f"'{other_name}' — entity locations must be unique")
                return
            if other_key.startswith(loc_key + "/") or loc_key.startswith(other_key + "/"):
                self.error(path, f"records location '{type_dir}' is nested with entity "
                                 f"'{other_name}''s location — entity locations must not nest")
                return

        fields = data.get("fields")
        if not isinstance(fields, dict) or not fields:
            self.error(path, "schema needs a non-empty 'fields' mapping")
            return
        ok = True
        for fname, spec in fields.items():
            if fname in RESERVED_FIELDS:
                self.error(path, f"field '{fname}' is reserved (added automatically)", fname)
                ok = False
                continue
            if not self._check_field_spec(path, fname, spec):
                ok = False
        self._check_constraints_spec(path, data)
        if not ok:
            return

        data["_path"] = path
        data["_width"] = width
        data["_id_re"] = re.compile(ID_RE_TEMPLATE.format(prefix=re.escape(prefix), width=width))
        data.setdefault("strict", True)
        data["dir"] = dir_val
        data["_type_dir"] = type_dir
        self.schemas[name] = data
        self.prefix_to_entity[prefix] = name
        self.dir_to_entity[loc_key] = name

    def _check_field_spec(self, path, fname, spec, ctx=None):
        label = ctx or fname
        if not isinstance(spec, dict):
            self.error(path, f"field spec must be a mapping, got {type(spec).__name__}", label)
            return False
        ok = True
        for key in spec:
            if key not in VALID_FIELD_KEYS:
                self.error(path, f"unknown field key '{key}'", label)
                ok = False
        ftype = spec.get("type")
        if ftype not in VALID_TYPES:
            self.error(path, f"unknown or missing type {ftype!r} "
                             f"(valid: {', '.join(sorted(VALID_TYPES))})", label)
            return False
        allowed = BASE_FIELD_KEYS | TYPE_SPECIFIC_KEYS[ftype]
        for key in spec:
            if key in VALID_FIELD_KEYS and key not in allowed:
                self.error(path, f"key '{key}' does not apply to type '{ftype}' "
                                 f"— it would be silently dead configuration", label)
                ok = False
        if ftype in ("integer", "number"):
            for bound in ("min", "max"):
                if bound in spec and (isinstance(spec[bound], bool)
                                      or not isinstance(spec[bound], (int, float))):
                    self.error(path, f"'{bound}' must be a number, got {spec[bound]!r}", label)
                    ok = False
        if "pattern" in spec:
            if not isinstance(spec["pattern"], str):
                self.error(path, f"'pattern' must be a string, got {spec['pattern']!r}", label)
                ok = False
            else:
                try:
                    re.compile(spec["pattern"])
                except re.error as e:
                    self.error(path, f"'pattern' is not a valid regex: {e}", label)
                    ok = False
        if ftype == "enum" and not (isinstance(spec.get("values"), list) and spec["values"]):
            self.error(path, "enum needs a non-empty 'values' list", label)
            ok = False
        if ftype == "ref" and not isinstance(spec.get("entity"), str):
            self.error(path, "ref needs an 'entity' (target entity name)", label)
            ok = False
        if ftype == "list":
            items = spec.get("items")
            if items is None:
                self.error(path, "list needs an 'items' field spec", label)
                ok = False
            elif not self._check_field_spec(path, fname, items, ctx=f"{label}.items"):
                ok = False
        return ok

    def _check_constraints_spec(self, path, data):
        """Meta-validate the optional 'constraints' list. Invalid entries are reported as errors and pruned, so a bad constraint never disables record validation for the whole schema."""
        constraints = data.get("constraints")
        if constraints is None:
            return
        if not isinstance(constraints, list):
            self.error(path, "'constraints' must be a list")
            data["constraints"] = []
            return
        valid = []
        for i, c in enumerate(constraints):
            label = f"constraints[{i}]"
            if not isinstance(c, dict):
                self.error(path, "constraint must be a mapping", label)
                continue
            rule = c.get("rule")
            if rule not in VALID_CONSTRAINT_RULES:
                self.error(path, f"unknown or missing rule {rule!r} "
                                 f"(valid: {', '.join(sorted(VALID_CONSTRAINT_RULES))})", label)
                continue
            allowed = {"rule", "description"} | (
                {"group_by", "max"} if rule == "max_count_per" else {"fields"})
            entry_ok = True
            for key in c:
                if key not in allowed:
                    self.error(path, f"unknown constraint key '{key}'", label)
                    entry_ok = False
            if rule == "max_count_per":
                if not isinstance(c.get("group_by"), str) or not c["group_by"]:
                    self.error(path, "max_count_per needs a 'group_by' field or ref-path", label)
                    entry_ok = False
                if not isinstance(c.get("max"), int) or c["max"] < 0:
                    self.error(path, "max_count_per needs a non-negative integer 'max'", label)
                    entry_ok = False
            else:  # unique
                flds = c.get("fields")
                if not (isinstance(flds, list) and flds
                        and all(isinstance(f, str) for f in flds)):
                    self.error(path, "unique needs a non-empty 'fields' list of field names", label)
                    entry_ok = False
            if entry_ok:
                valid.append(c)
        data["constraints"] = valid

    def check_ref_targets(self):
        """Refs must point at entity types that actually exist (schema level)."""
        for name, schema in self.schemas.items():
            for fname, spec in schema["fields"].items():
                for s, label in self._iter_specs(fname, spec):
                    if s.get("type") == "ref" and s.get("entity") not in self.schemas:
                        self.error(schema["_path"],
                                   f"ref targets unknown entity '{s.get('entity')}'", label)

    def check_constraint_paths(self):
        """Constraint fields/paths must exist; every intermediate hop must be a ref."""
        for name, schema in self.schemas.items():
            for i, c in enumerate(schema.get("constraints") or []):
                label = f"constraints[{i}]"
                if c.get("rule") == "unique":
                    for f in c.get("fields", []):
                        if f not in RESERVED_FIELDS and f not in schema["fields"]:
                            self.error(schema["_path"],
                                       f"unique references undeclared field '{f}'", label)
                elif c.get("rule") == "max_count_per" and isinstance(c.get("group_by"), str):
                    hops = c["group_by"].split(".")
                    current = schema
                    for j, hop in enumerate(hops):
                        spec = current["fields"].get(hop)
                        if spec is None:
                            self.error(schema["_path"],
                                       f"group_by path '{c['group_by']}': '{hop}' is not a "
                                       f"declared field of entity '{current['entity']}'", label)
                            break
                        if j < len(hops) - 1:
                            if spec.get("type") != "ref":
                                self.error(schema["_path"],
                                           f"group_by path '{c['group_by']}': '{hop}' must be "
                                           f"a ref to continue the path", label)
                                break
                            target = self.schemas.get(spec.get("entity"))
                            if target is None:
                                break  # already reported by check_ref_targets
                            current = target

    @staticmethod
    def _iter_specs(fname, spec):
        yield spec, fname
        if isinstance(spec, dict) and spec.get("type") == "list" and isinstance(spec.get("items"), dict):
            yield spec["items"], f"{fname}.items"

    # ---------------- entity loading ----------------

    def load_records(self):
        # A file named like its own directory (entities/entities.md,
        # registry/skill/skill.md) is an Obsidian folder note — typically the
        # generated index — never a record.
        def is_folder_note(p):
            return p.stem == p.parent.name

        scanned = set()
        for name in sorted(self.schemas):
            type_dir = self.schemas[name]["_type_dir"]
            if not type_dir.is_dir():
                continue
            for path in sorted(type_dir.rglob("*.md")):
                if is_folder_note(path):
                    continue
                scanned.add(path.resolve())
                self._load_record(path, name)

        # Stray detection: anything under entities_dir that no schema claimed.
        uses_default_location = any(s.get("path") is None for s in self.schemas.values())
        if not self.entities_dir.is_dir():
            if uses_default_location or not self.schemas:
                self.error(self.entities_dir, "entities directory not found")
            return
        def rel_to_root(p):
            try:
                return p.relative_to(self.root).as_posix()
            except ValueError:
                return p.as_posix()
        known = sorted(rel_to_root(s["_type_dir"]) for s in self.schemas.values())
        for path in sorted(self.entities_dir.rglob("*.md")):
            if path.resolve() in scanned or is_folder_note(path):
                continue
            self.error(path, "file is not inside any declared entity directory "
                             f"(known: {', '.join(known) or 'none'})")

    def _load_record(self, path, expected_entity):
        text = self._read_text(path)
        if text is None:
            return
        fm, body = split_frontmatter(text)
        if fm is None:
            self.error(path, "missing YAML frontmatter block (--- ... ---) at top of file")
            return
        try:
            fields = yaml.safe_load(fm)
        except yaml.YAMLError as e:
            self.error(path, f"frontmatter is not valid YAML: {e}")
            return
        if not isinstance(fields, dict):
            self.error(path, "frontmatter must be a YAML mapping")
            return

        rid = fields.get("id")
        if not isinstance(rid, str) or not rid:
            self.error(path, "missing or non-string 'id' in frontmatter", "id")
            return
        if rid in self.records:
            self.error(path, f"duplicate id '{rid}' (also in "
                             f"{self._rel(self.records[rid]['file'])})", "id")
            return
        if not path.name.startswith(rid):
            self.error(path, f"filename should start with the id '{rid}' "
                             f"(e.g. {rid}-short-slug.md)", "id")
        self.records[rid] = {"entity": expected_entity, "file": path,
                             "fields": fields, "body": body}

    # ---------------- record validation ----------------

    def validate_records(self, only_paths=None):
        """Validate records; with only_paths, restrict to those files (resolved against cwd, then against the project root). Returns the filter paths that matched no loaded record — a typo'd filter must surface as an error, never as a false green."""
        if not only_paths:
            for rid, rec in self.records.items():
                self._validate_record(rid, rec)
            return []
        record_files = {rec["file"].resolve(): rid for rid, rec in self.records.items()}
        selected, unmatched = set(), []
        for p in only_paths:
            hit = None
            for candidate in (Path(p), self.root / p):
                try:
                    resolved = candidate.resolve()
                except OSError:
                    continue
                if resolved in record_files:
                    hit = record_files[resolved]
                    break
            if hit is None:
                unmatched.append(str(p))
            else:
                selected.add(hit)
        for rid in sorted(selected):
            self._validate_record(rid, self.records[rid])
        return unmatched

    def _validate_record(self, rid, rec):
        path, fields = rec["file"], rec["fields"]
        schema = self.schemas.get(rec["entity"])
        if schema is None:
            return  # schema itself failed meta-validation; already reported

        if not schema["_id_re"].match(rid):
            self.error(path, f"id '{rid}' does not match pattern "
                             f"{schema['id']['prefix']}-<{schema['_width']}+ digits>", "id")
        declared = fields.get("entity")
        if declared != rec["entity"]:
            self.error(path, f"frontmatter entity '{declared}' does not match "
                             f"directory-implied entity '{rec['entity']}'", "entity")

        for fname in fields:
            if fname in RESERVED_FIELDS:
                continue
            if fname not in schema["fields"]:
                if schema.get("strict", True):
                    self.error(path, f"unknown field '{fname}' not declared in schema "
                                     f"'{rec['entity']}'", fname)
                else:
                    self.warn(path, f"field '{fname}' not declared in schema", fname)

        for fname, spec in schema["fields"].items():
            value = fields.get(fname)
            if value is None:
                if spec.get("required"):
                    self.error(path, f"required field '{fname}' is missing or null", fname)
                continue
            self._check_value(path, fname, spec, value)

        self._check_inline_refs(path, rec["body"])

    def _check_value(self, path, fname, spec, value):
        ftype = spec["type"]
        if ftype in ("string", "text"):
            if not isinstance(value, str):
                self._type_error(path, fname, "string", value)
            elif spec.get("pattern") and not re.fullmatch(spec["pattern"], value):
                self.error(path, f"value {value!r} does not match pattern "
                                 f"{spec['pattern']!r}", fname)
        elif ftype == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                self._type_error(path, fname, "integer", value)
            else:
                self._check_range(path, fname, spec, value)
        elif ftype == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                self._type_error(path, fname, "number", value)
            else:
                self._check_range(path, fname, spec, value)
        elif ftype == "boolean":
            if not isinstance(value, bool):
                self._type_error(path, fname, "boolean", value)
        elif ftype == "date":
            if isinstance(value, datetime.datetime) or not isinstance(value, datetime.date):
                self._type_error(path, fname, "date (YYYY-MM-DD, unquoted)", value)
        elif ftype == "datetime":
            if not isinstance(value, (datetime.date, datetime.datetime)):
                self._type_error(path, fname, "datetime (ISO 8601, unquoted)", value)
        elif ftype == "enum":
            if value not in spec["values"]:
                self.error(path, f"value {value!r} not in enum "
                                 f"{spec['values']}", fname)
        elif ftype == "ref":
            self._check_ref(path, fname, spec, value)
        elif ftype == "list":
            if not isinstance(value, list):
                self._type_error(path, fname, "list", value)
            else:
                for i, item in enumerate(value):
                    self._check_value(path, f"{fname}[{i}]", spec["items"], item)

    def _check_ref(self, path, fname, spec, value):
        if not isinstance(value, str):
            self._type_error(path, fname, "ref (entity id string)", value)
            return
        target = self.records.get(value)
        if target is None:
            self.error(path, f"reference '{value}' does not resolve to any entity", fname)
        elif target["entity"] != spec["entity"]:
            self.error(path, f"reference '{value}' points at a "
                             f"'{target['entity']}', expected '{spec['entity']}'", fname)

    def _check_range(self, path, fname, spec, value):
        if "min" in spec and value < spec["min"]:
            self.error(path, f"value {value} below min {spec['min']}", fname)
        if "max" in spec and value > spec["max"]:
            self.error(path, f"value {value} above max {spec['max']}", fname)

    def _type_error(self, path, fname, expected, value):
        hint = ""
        if isinstance(value, bool):
            hint = " (YAML parses yes/no/true/false as boolean — quote it if you meant text)"
        elif isinstance(value, (datetime.date, datetime.datetime)):
            hint = " (YAML parsed this as a date — quote it if you meant text)"
        self.error(path, f"expected {expected}, got "
                         f"{type(value).__name__} {value!r}{hint}", fname)

    def _check_inline_refs(self, path, body):
        """Validate [[ID]] wiki-style references in prose, skipping fenced code."""
        in_fence = False
        for line in body.splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in INLINE_REF_RE.finditer(line):
                ref = m.group(1)
                prefix = ref.split("-", 1)[0]
                if prefix not in self.prefix_to_entity:
                    self.error(path, f"inline reference [[{ref}]] uses unknown prefix "
                                     f"'{prefix}'")
                elif ref not in self.records:
                    self.error(path, f"inline reference [[{ref}]] does not resolve "
                                     f"to any entity")

    def validate_constraints(self):
        """Aggregate (cross-record) constraints; always evaluated project-wide."""
        for name, schema in self.schemas.items():
            recs = [(rid, r) for rid, r in self.records.items() if r["entity"] == name]
            for c in schema.get("constraints") or []:
                desc = f" — {c['description']}" if c.get("description") else ""
                if c.get("rule") == "unique":
                    seen = {}
                    for rid, rec in sorted(recs):
                        key = tuple(_hashable(rec["fields"].get(f)) if f != "id" else rid
                                    for f in c["fields"])
                        if any(v is None for v in key):
                            continue
                        if key in seen:
                            self.error(rec["file"],
                                       f"constraint 'unique' on {c['fields']} violated: "
                                       f"same values as {seen[key]}{desc}")
                        else:
                            seen[key] = rid
                elif c.get("rule") == "max_count_per":
                    groups = {}
                    for rid, rec in sorted(recs):
                        value = _hashable(self._resolve_path(rec, c["group_by"].split(".")))
                        if value is not None:
                            groups.setdefault(value, []).append(rid)
                    for value, ids in sorted(groups.items(), key=lambda kv: str(kv[0])):
                        if len(ids) > c["max"]:
                            self.error(schema["_path"],
                                       f"constraint 'max_count_per {c['group_by']}' violated: "
                                       f"'{value}' has {len(ids)} records (max {c['max']}): "
                                       f"{', '.join(ids)}{desc}")

    def _resolve_path(self, rec, hops):
        value = rec["fields"].get(hops[0])
        for hop in hops[1:]:
            if not isinstance(value, str):
                return None
            target = self.records.get(value)
            if target is None:
                return None  # broken ref: reported by record validation, not here
            value = target["fields"].get(hop)
        return value

    # ---------------- utilities ----------------

    def next_id(self, entity):
        schema = self.schemas[entity]
        prefix, width = schema["id"]["prefix"], schema["_width"]
        best = 0
        for rid, rec in self.records.items():
            if rec["entity"] == entity:
                try:
                    best = max(best, int(rid.split("-", 1)[1]))
                except (IndexError, ValueError):
                    pass
        return f"{prefix}-{best + 1:0{width}d}"

    @property
    def errors(self):
        return [i for i in self.issues if i.level == "error"]


def _hashable(value):
    """Canonicalize list/dict values so aggregate constraints never crash on unhashable types. Such values are type errors reported elsewhere; here they must merely not take the engine down."""
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, default=str)
    return value


def split_frontmatter(text):
    """Return (frontmatter_str, body_str) or (None, text) if absent."""
    if not text.startswith(FRONTMATTER_DELIM):
        return None, text
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return None, text
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONTMATTER_DELIM:
            return "".join(lines[1:i]), "".join(lines[i + 1:])
    return None, text


def find_root(start):
    p = Path(start).resolve()
    for candidate in [p] + list(p.parents):
        if (candidate / CONFIG_FILENAME).exists() or (candidate / DEFAULT_SCHEMAS_DIR).is_dir():
            return candidate
    return None


def load_project(root_arg):
    root = Path(root_arg).resolve() if root_arg else find_root(Path.cwd())
    if root is None:
        sys.stderr.write("entity_lint: could not find project root (no "
                         f"{CONFIG_FILENAME} or {DEFAULT_SCHEMAS_DIR}/ upwards from cwd). "
                         "Use --root.\n")
        sys.exit(2)
    project = Project(root)
    project.load_schemas()
    project.check_ref_targets()
    project.check_constraint_paths()
    project.load_records()
    return project


def cmd_validate(args):
    project = load_project(args.root)
    unmatched = project.validate_records(only_paths=args.paths or None)
    if unmatched:
        sys.stderr.write("entity_lint: these path filters matched no loaded record: "
                         + ", ".join(unmatched) + "\n")
        return 2
    project.validate_constraints()
    errors = project.errors
    warnings = [i for i in project.issues if i.level == "warning"]
    if args.json:
        print(json.dumps({
            "engine_version": ENGINE_VERSION,
            "ok": not errors,
            "errors": len(errors),
            "warnings": len(warnings),
            "entities": len(project.records),
            "schemas": sorted(project.schemas),
            "issues": [i.to_dict() for i in project.issues],
        }, indent=2, default=str))
    else:
        for issue in project.issues:
            print(issue)
        status = "FAIL" if errors else "OK"
        print(f"{status}: {len(project.records)} entities across "
              f"{len(project.schemas)} schemas — "
              f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def cmd_index(args):
    project = load_project(args.root)
    # Links are computed relative to where the index itself will live
    # (stdout falls back to the project root), so --write works at any path.
    target = Path(args.write) if args.write else None
    link_base = target.resolve().parent if target else Path(project.root).resolve()
    out = io.StringIO()
    out.write("# Entity index\n\n_Generated by entity_lint.py — do not edit by hand._\n")
    for name in sorted(project.schemas):
        recs = sorted((rid, r) for rid, r in project.records.items() if r["entity"] == name)
        out.write(f"\n## {name} ({len(recs)})\n\n")
        if not recs:
            out.write("_none yet_\n")
            continue
        out.write("| id | title | file |\n|---|---|---|\n")
        for rid, r in recs:
            title = str(r["fields"].get("title", "") or r["fields"].get("name", ""))
            title = " ".join(title.split()).replace("|", "\\|")
            try:
                rel = r["file"].relative_to(project.root).as_posix()
            except ValueError:
                rel = r["file"].as_posix()
            link = os.path.relpath(str(r["file"].resolve()), str(link_base)).replace(os.sep, "/")
            out.write(f"| {rid} | {title} | [{rel}]({link}) |\n")
    content = out.getvalue()
    if target is not None:
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        except OSError as e:
            sys.stderr.write(f"entity_lint: cannot write index to {target}: {e}\n")
            return 2
        print(f"wrote {args.write}")
    else:
        print(content)
    return 1 if project.errors else 0


def cmd_new(args):
    project = load_project(args.root)
    if args.entity not in project.schemas:
        sys.stderr.write(f"entity_lint: no schema for entity '{args.entity}' "
                         f"(known: {', '.join(sorted(project.schemas)) or 'none'})\n")
        return 2
    schema = project.schemas[args.entity]
    rid = project.next_id(args.entity)
    lines = ["---", f"id: {rid}", f"entity: {args.entity}"]
    for fname, spec in schema["fields"].items():
        if fname == "title" and args.title:
            lines.append(f"title: {args.title}")
            continue
        placeholder = {
            "enum": f"  # one of: {', '.join(map(str, spec.get('values', [])))}",
            "ref": f"  # id of a {spec.get('entity')}",
            "date": f"  # YYYY-MM-DD",
        }.get(spec.get("type"), "")
        marker = "" if spec.get("required") else "  # optional"
        lines.append(f"{fname}:{placeholder or marker}")
    lines += ["---", "", "(prose body — free-form Markdown; link entities inline as [[ID]])", ""]
    stub = "\n".join(lines)
    slug = re.sub(r"[^a-z0-9]+", "-", (args.title or "new").lower()).strip("-")[:40]
    suggested = schema["_type_dir"] / f"{rid}-{slug}.md"
    print(stub)
    try:
        shown = suggested.relative_to(project.root).as_posix()
    except ValueError:
        shown = suggested.as_posix()
    sys.stderr.write(f"suggested path: {shown}\n")
    return 0


def main(argv=None):
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", help="project root directory")
    parser = argparse.ArgumentParser(prog="entity_lint.py", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", parents=[common],
                           help="validate schemas and entity records")
    p_val.add_argument("paths", nargs="*", help="restrict record validation to these files")
    p_val.add_argument("--json", action="store_true", help="machine-readable output")

    p_idx = sub.add_parser("index", parents=[common],
                           help="generate a Markdown index of all entities")
    p_idx.add_argument("--write", help="write index to this path")

    p_new = sub.add_parser("new", parents=[common],
                           help="print a stub record with the next free id")
    p_new.add_argument("entity", help="entity type name")
    p_new.add_argument("--title", help="title for the new record")

    args = parser.parse_args(argv)
    return {"validate": cmd_validate, "index": cmd_index, "new": cmd_new}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
