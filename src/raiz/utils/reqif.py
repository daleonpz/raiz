# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Dict, List, Optional
import uuid
import xml.etree.ElementTree as ET


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def _split_linked_tests(raw_value: Optional[str]) -> List[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def load_reqif(file_path: Path) -> List[Dict[str, object]]:
    try:
        tree = ET.parse(file_path)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid ReqIF XML file '{file_path}': {exc}") from exc
    root = tree.getroot()
    requirements: List[Dict[str, object]] = []

    for element in root.iter():
        if _local_name(element.tag) != "SPEC-OBJECT":
            continue

        req = {
            "id": element.attrib.get("LONG-NAME", ""),
            "uuid": element.attrib.get("IDENTIFIER", ""),
            "description": "",
            "type": "",
            "domain": "",
            "linked_tests": [],
        }

        raw_fields: Dict[str, str] = {}
        for value_node in element.iter():
            if not _local_name(value_node.tag).startswith("ATTRIBUTE-VALUE"):
                continue

            key = (
                value_node.attrib.get("DEFINITION")
                or value_node.attrib.get("LONG-NAME")
                or ""
            )
            key = _normalize_key(key)
            value = value_node.attrib.get("THE-VALUE")
            if value is None:
                value = (value_node.text or "").strip()
            if key:
                raw_fields[key] = value

        for key, value in raw_fields.items():
            value_text = str(value or "")
            if (
                key in {"id", "req_id", "requirement_id"}
                and value_text.startswith("REQ-")
                and not req["id"]
            ):
                req["id"] = value_text
            elif key in {"description", "desc"} and not req["description"]:
                req["description"] = value_text
            elif key in {"type", "req_type", "requirement_type"} and not req["type"]:
                req["type"] = value_text
            elif key == "domain" and not req["domain"]:
                req["domain"] = value_text
            elif (
                key in {"linked_tests", "linkedtest", "tests"}
                and not req["linked_tests"]
            ):
                req["linked_tests"] = _split_linked_tests(value_text)

        if not req["uuid"]:
            req["uuid"] = str(uuid.uuid4())

        requirements.append(req)

    return requirements


def dump_reqif(requirements: List[Dict[str, object]], file_path: Path) -> None:
    reqif = ET.Element("REQ-IF")
    core_content = ET.SubElement(reqif, "CORE-CONTENT")
    spec_objects = ET.SubElement(core_content, "SPEC-OBJECTS")

    for req in requirements:
        identifier = req.get("uuid") or str(uuid.uuid4())
        long_name = req.get("id") or ""

        spec_object = ET.SubElement(
            spec_objects,
            "SPEC-OBJECT",
            {"IDENTIFIER": str(identifier), "LONG-NAME": str(long_name)},
        )
        values = ET.SubElement(spec_object, "VALUES")

        ET.SubElement(
            values,
            "ATTRIBUTE-VALUE-STRING",
            {"DEFINITION": "id", "THE-VALUE": str(req.get("id", ""))},
        )
        ET.SubElement(
            values,
            "ATTRIBUTE-VALUE-STRING",
            {"DEFINITION": "description", "THE-VALUE": str(req.get("description", ""))},
        )
        ET.SubElement(
            values,
            "ATTRIBUTE-VALUE-STRING",
            {"DEFINITION": "type", "THE-VALUE": str(req.get("type", ""))},
        )
        ET.SubElement(
            values,
            "ATTRIBUTE-VALUE-STRING",
            {"DEFINITION": "domain", "THE-VALUE": str(req.get("domain", ""))},
        )

        linked_tests = req.get("linked_tests", [])
        if isinstance(linked_tests, list):
            linked_tests_value = ",".join(linked_tests)
        else:
            linked_tests_value = str(linked_tests)
        ET.SubElement(
            values,
            "ATTRIBUTE-VALUE-STRING",
            {"DEFINITION": "linked_tests", "THE-VALUE": linked_tests_value},
        )

    tree = ET.ElementTree(reqif)
    ET.indent(tree, space="  ")
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
