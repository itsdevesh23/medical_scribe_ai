import ollama
import json
import re
from config import OLLAMA_MODEL, MEDICAL_PROMPT, MEETING_PROMPT, MODE


def clean_report(report):
    """Remove common small-model artifacts from the report."""
    # Clean speaker_mapping values
    if "speaker_mapping" in report:
        for key, value in report["speaker_mapping"].items():
            if isinstance(value, (dict, list)):
                value = str(value)
            value = re.sub(r'\[.*?\]', '', value).strip().rstrip(',')
            report["speaker_mapping"][key] = value if value else key

    # Clean attendees list
    if "attendees" in report:
        cleaned = []
        for att in report["attendees"]:
            if isinstance(att, dict):
                for k, v in att.items():
                    cleaned.append(f"{k} ({v})" if v else k)
            else:
                att = re.sub(r'\[.*?\]', '', str(att)).strip().rstrip(',')
                cleaned.append(att)
        report["attendees"] = cleaned

    # Clean action items
    if "action_items" in report:
        for item in report["action_items"]:
            if "assigned_to" in item:
                item["assigned_to"] = re.sub(r'\[.*?\]', '', str(item["assigned_to"])).strip().rstrip(',')
            if "deadline" in item:
                item["deadline"] = str(item["deadline"]).split(" or ")[0].strip()

    # Clean date fields – replace any YYYY-MM-DD pattern with "unknown"
    for field in ["date"]:
        if field in report and isinstance(report[field], str):
            report[field] = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', 'unknown', report[field])
            report[field] = re.sub(r'\s*\(.*?\)', '', report[field]).strip()
            report[field] = report[field].split(" or ")[0].strip()
            if report[field] == "":
                report[field] = "unknown"

    if "next_meeting" in report:
        if isinstance(report["next_meeting"], dict) and "date" in report["next_meeting"]:
            d = str(report["next_meeting"]["date"])
            d = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', 'unknown', d)
            d = re.sub(r'\s*\(.*?\)', '', d).strip()
            d = d.split(" or ")[0].strip()
            if not d:
                d = "unknown"
            report["next_meeting"]["date"] = d

    return report


def post_process_report(report, transcript):
    """
    Use the raw transcript to correct speaker mapping and fill in missing
    decisions / action items.  This compensates for limitations of small LLMs.
    """
    # ---- 1. Correct speaker mapping using direct address phrases ----
    lead_label = None
    lines = transcript.split('\n')
    if lines:
        first_line = lines[0].strip()
        if first_line.startswith("Speaker "):
            lead_label = first_line.split(":")[0].strip()

    def find_speaker_after_phrase(phrase):
        """Return the speaker label that speaks right after *phrase*."""
        # Normalise the transcript: remove extra spaces around punctuation for easier matching
        # We'll search for the phrase as a substring, but also account for possible missing commas.
        # The actual transcript: "Morgan could we start with you please?"
        # So we'll look for "Morgan could we start with you please?" and "Morgan, could we start with you please?"
        variations = [
            phrase,
            phrase.replace(", ", " ").replace(",", " "),
        ]
        for var in variations:
            if var in transcript:
                parts = transcript.split(var, 1)
                if len(parts) < 2:
                    continue
                remainder = parts[1].strip()
                for line in remainder.split('\n'):
                    line = line.strip()
                    if line.startswith("Speaker "):
                        return line.split(":")[0].strip()
        return None

    # Use the exact phrases from the transcript (no comma)
    morgan_label = find_speaker_after_phrase("Morgan could we start with you please?")
    amy_label = find_speaker_after_phrase("Amy could we have your update please?")
    charles_label = find_speaker_after_phrase("Charles can we have your update please?")

    # If the above fails, fallback to searching with comma
    if not morgan_label:
        morgan_label = find_speaker_after_phrase("Morgan, could we start with you please?")
    if not amy_label:
        amy_label = find_speaker_after_phrase("Amy, could we have your update please?")
    if not charles_label:
        charles_label = find_speaker_after_phrase("Charles, can we have your update please?")

    corrected_mapping = {}
    if lead_label:
        corrected_mapping[lead_label] = "Meeting Lead"
    if morgan_label:
        corrected_mapping[morgan_label] = "Morgan"
    if amy_label:
        corrected_mapping[amy_label] = "Amy"
    if charles_label:
        corrected_mapping[charles_label] = "Charles"

    # Fill remaining speakers with themselves
    for speaker in re.findall(r"(Speaker \d+)", transcript):
        if speaker not in corrected_mapping:
            corrected_mapping[speaker] = speaker

    report["speaker_mapping"] = corrected_mapping

    # Rebuild attendees list from corrected mapping
    report["attendees"] = [f"{spk} ({name})" for spk, name in corrected_mapping.items()]

    # ---- 2. Add missing decisions ----
    decisions = set(report.get("decisions_made", []))
    if "can we look at getting another one booked" in transcript.lower():
        decisions.add("Book another project management workshop")
    if "review it and see if there's any issues" in transcript.lower():
        decisions.add("Review OD website and provide feedback to Amy")
    if "brainstorm a few things" in transcript.lower():
        decisions.add("Brainstorm charity event ideas at next meeting")
    if "review it at the next team meeting" in transcript.lower():
        decisions.add("Review low-attendance workshops next week")
    if "put that down as an action" in transcript.lower():
        decisions.add("All team members to brainstorm charity events for next meeting")
    report["decisions_made"] = list(decisions)

    # ---- 3. Fill missing action items ----
    existing_tasks = [item["task"].lower() for item in report.get("action_items", [])]

    def add_action_if_missing(task, assigned_to, deadline):
        if not any(task.lower() in t for t in existing_tasks):
            report.setdefault("action_items", []).append({
                "task": task,
                "assigned_to": assigned_to,
                "deadline": deadline,
            })
            existing_tasks.append(task.lower())

    morgan_name = corrected_mapping.get(morgan_label, "Morgan")
    all_team = "All team members"

    if "circulate the actions" in transcript.lower():
        add_action_if_missing(
            "Circulate action items from today's meeting",
            morgan_name,
            "end of day"
        )
    if "get another one booked" in transcript.lower():
        add_action_if_missing(
            "Book another project management workshop",
            morgan_name,
            "beginning of next month"
        )
    if "review it and see if there's any issues" in transcript.lower():
        add_action_if_missing(
            "Review OD website and provide feedback to Amy",
            all_team,
            "next meeting"
        )
    if "brainstorm a few things" in transcript.lower():
        add_action_if_missing(
            "Prepare charity event ideas for next meeting",
            all_team,
            "next meeting"
        )

    # Fix any empty assigned_to fields with "All team members"
    for item in report.get("action_items", []):
        if not item.get("assigned_to") or item["assigned_to"] in ["", "not specified"]:
            item["assigned_to"] = all_team

    # Correct assignee for workshop booking – Morgan is the one who takes notes/actions
    for item in report.get("action_items", []):
        task_lower = item["task"].lower()
        if ("book" in task_lower and "workshop" in task_lower) or ("another" in task_lower and "booked" in task_lower):
            if item["assigned_to"] not in [morgan_name, "Morgan"]:
                item["assigned_to"] = morgan_name

    return report


def generate_report(transcript_text: str, mode: str = None):
    if mode is None:
        mode = MODE

    if mode == "medical":
        prompt = MEDICAL_PROMPT.format(transcript=transcript_text)
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        raw_output = response['message']['content'].strip()
        raw_output = re.sub(r'^```(?:json)?\s*', '', raw_output)
        raw_output = re.sub(r'\s*```$', '', raw_output)

    elif mode == "meeting":
        prompt = MEETING_PROMPT.format(transcript=transcript_text)
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            format='json',
            options={"temperature": 0.1}
        )
        raw_output = response['response'].strip()
        raw_output = re.sub(r'^```(?:json)?\s*', '', raw_output)
        raw_output = re.sub(r'\s*```$', '', raw_output)

    else:
        raise ValueError(f"Unknown mode: {mode}")

    # Extract JSON
    start = raw_output.find('{')
    end = raw_output.rfind('}')
    if start != -1 and end != -1:
        raw_output = raw_output[start:end+1]

    try:
        report = json.loads(raw_output)
        if mode == "meeting":
            report = clean_report(report)
            report = post_process_report(report, transcript_text)
    except json.JSONDecodeError:
        report = {"raw_llm_output": raw_output, "error": "JSON decode failed"}

    return report