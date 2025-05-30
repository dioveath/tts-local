import re


def parse_ass(ass_file):
    """Parses an ASS file into a list of subtitle entries."""
    entries = []
    with open(ass_file, "r", encoding="utf-8") as f:
        content = f.readlines()
        event_section = False
        for line in content:
            line = line.strip()
            if line.startswith("[Events]"):
                event_section = True
                continue
            if event_section and line.startswith("Dialogue:"):
                parts = line.split(",", 9)  # Split only on the first 9 commas
                start = parts[1].strip()
                end = parts[2].strip()
                text = parts[-1].strip()
                entries.append({"start": start, "end": end, "text": text, "line": line})
    return entries


def ass_time_to_seconds(ass_time):
    """Converts ASS timestamp format (H:MM:SS.CS) to seconds."""
    try:
        # Split on the last period to separate the integer part of seconds and decimal part
        main_part, ms_part = ass_time.rsplit(".", 1)
        h, m, s = map(int, main_part.split(":"))
        ms = float(f"0.{ms_part}")
        return h * 3600 + m * 60 + s + ms
    except ValueError:
        raise ValueError(f"Invalid ASS timestamp format: {ass_time}")


def seconds_to_ass_time(seconds):
    """Converts seconds to ASS timestamp format (H:MM:SS.CS)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02}:{s:05.2f}"


def concatenate_ass(file_a, file_b, output_file, length_a):
    """
    Concatenates two ASS files such that subtitles from file_b start right after file_a.
    The length_a parameter allows specifying the actual length of file_a in seconds.
    """
    entries_a = parse_ass(file_a)
    entries_b = parse_ass(file_b)

    # Calculate the end time of the last entry in `file_a`
    last_end_time_a = ass_time_to_seconds(entries_a[-1]["end"])
    if length_a is not None:
        last_end_time_a = max(last_end_time_a, length_a)

    # Shift `file_b` timings
    for entry in entries_b:
        start_seconds = ass_time_to_seconds(entry["start"]) + last_end_time_a
        end_seconds = ass_time_to_seconds(entry["end"]) + last_end_time_a
        entry["start"] = seconds_to_ass_time(start_seconds)
        entry["end"] = seconds_to_ass_time(end_seconds)

    # Write output ASS file
    with open(file_a, "r", encoding="utf-8") as f:
        header = []
        events_started = False
        for line in f:
            if line.startswith("[Events]"):
                events_started = True
            if not events_started:
                header.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(header)
        f.write("[Events]\n")
        f.write(
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )

        for entry in entries_a + entries_b:
            # Reconstruct the line without removing commas in dialogue text
            fields = entry["line"].split(",", 9)  # Split only on the first 9 commas
            fields[1] = entry["start"]  # Update start time
            fields[2] = entry["end"]  # Update end time
            f.write(
                ",".join(fields) + "\n"
            )  # Rejoin all fields including the full dialogue text

    print(f"Concatenated ASS saved to {output_file}")


def shift_ass(input_file, output_file, length_shift):
    """
    Shifts the start and end times of subtitles in an ASS file by a given length.

    Parameters:
        input_file (str): Path to the input ASS file.
        output_file (str): Path to save the shifted ASS file.
        length_shift (float): Time in seconds to shift all subtitles.
    """
    entries = parse_ass(input_file)

    # Shift the timings
    for entry in entries:
        start_seconds = ass_time_to_seconds(entry["start"]) + length_shift
        end_seconds = ass_time_to_seconds(entry["end"]) + length_shift
        entry["start"] = seconds_to_ass_time(
            max(0, start_seconds)
        )  # Ensure no negative times
        entry["end"] = seconds_to_ass_time(max(0, end_seconds))

    # Write the shifted ASS file
    with open(input_file, "r", encoding="utf-8") as f:
        header = []
        events_started = False
        for line in f:
            if line.startswith("[Events]"):
                events_started = True
            if not events_started:
                header.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(header)
        f.write("[Events]\n")
        f.write(
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )

        for entry in entries:
            # Reconstruct the line without removing commas in dialogue text
            fields = entry["line"].split(",", 9)  # Split only on the first 9 commas
            fields[1] = entry["start"]  # Update start time
            fields[2] = entry["end"]  # Update end time
            f.write(
                ",".join(fields) + "\n"
            )  # Rejoin all fields including the full dialogue text

    print(f"Shifted ASS saved to {output_file}")


###############################################################################################################################
# Test code to verify the functionality of the ASS file utility functions

# MAIN

if __name__ == "__main__":
    ass_file_a_content = """[Script Info]
Title: Test A
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,1,1,1,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:05.00,Default,,0,0,0,,Hello from A!
    """

    ass_file_b_content = """[Script Info]
Title: Test B
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,1,1,1,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:02.00,0:00:06.00,Default,,0,0,0,,Hello from B!
    """

    # Write sample .ass files for testing
    with open("tests/test_a.ass", "w", encoding="utf-8") as f:
        f.write(ass_file_a_content)

    with open("tests/test_b.ass", "w", encoding="utf-8") as f:
        f.write(ass_file_b_content)

    # Run the concatenate function
    concatenate_ass(
        "tests/test_a.ass", "tests/test_b.ass", "tests/concatenated_output.ass"
    )

    # Run the shift function
    shift_ass("tests/test_a.ass", "tests/test_b.ass", "tests/shifted_output.ass")

    # Display the output paths for review
    print("Test files created:")
    print("Concatenated file: tests/concatenated_output.ass")
    print("Shifted file: tests/shifted_output.ass")
