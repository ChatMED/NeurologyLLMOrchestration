import json
from collections import OrderedDict


def sort_report_keys(report_json: dict) -> OrderedDict:
    key_order = [
        "compressed_summary",
        "anatomical_localisations",
        "pathophysiologies",
        "questions",
        "investigations",
        "treatments"
    ]
    sorted_report = OrderedDict()
    for key in key_order:
        if key in report_json:
            sorted_report[key] = report_json[key]
    for key in report_json:
        if key not in sorted_report:
            sorted_report[key] = report_json[key]
    return json.dumps(sorted_report, indent=2)
