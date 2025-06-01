# subtitle_generator.py

import json
import os
from typing import Optional
import logging

import whisper
from whisper.utils import SubtitlesWriter

from typing import TextIO

logger = logging.getLogger(__name__)

class SubtitleGenerator:
    """
    A class to generate subtitles for audio files using Whisper AI.

    Attributes:
        model_size (str): The size of the Whisper model to use.
        model (whisper.Whisper): The Whisper model instance.
        writer (SubtitlesWriterTimed): The subtitle writer instance.
        language (str): The language code for transcription.
    """

    def __init__(self):
        self.model_size = "tiny"
        self.language = "en"
        self.max_line_count = 1
        self.max_line_length = 20

        # Initialize model and writer
        self.model = self._load_model()
        self.writer = SubtitlesWriterTimed(
            max_line_count=self.max_line_count, max_line_length=self.max_line_length
        )
        logger.info("Subtitle generator initialized successfully. 🚀")

    def _load_model(self) -> whisper.Whisper:
        """
        Loads the Whisper model based on the configured model size.
        Returns:
            whisper.Whisper: The loaded Whisper model.
        """
        logger.info(f"Loading Whisper model '{self.model_size}' for subtitle generation...")
        return whisper.load_model(self.model_size)

    def generate_subtitles(
        self,
        audio_path: str,
        subtitle_path: str,
        caption_settings: dict[str, Optional[str]],
    ) -> bool:
        """
        Generates subtitles for a given audio file.

        Args:
            audio_path (str): The path to the audio file.
            subtitle_path (str): The path to save the generated subtitle file.
            caption_settings (Dict[str, Optional[str]]): A dictionary of settings for the caption generation.

        Returns:
            bool: True if subtitles were generated successfully, False otherwise.
        """
        if not os.path.exists(audio_path):
            logger.info(f"Audio file not found: {audio_path}")
            return False

        try:
            if not self.model:
                logger.info("Whisper model not loaded. Cannot generate subtitles.")
                return False

            new_max_line_count = caption_settings.get(
                "max_line_count", self.max_line_count
            )
            new_max_line_length = caption_settings.get(
                "max_line_length", self.max_line_length
            )
            self.writer.max_line_count = new_max_line_count
            self.writer.max_line_length = new_max_line_length

            result = self.model.transcribe(
                audio_path, word_timestamps=True, language=self.language
            )

            with open(subtitle_path, "w", encoding="utf-8") as f:
                self.writer.write_result(result, f, caption_settings)

            # save result settings to a json file
            result_json_path = os.path.splitext(subtitle_path)[0] + ".json"
            with open(result_json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4)

            logger.info(f"Transcript json saved to {result_json_path}")
            logger.info(f"Subtitles saved to {subtitle_path}")
            return True

        except Exception as e:
            logger.info(f"Error generating subtitles for {audio_path}: {e}")
            return False


class SubtitleBlock:
    def __init__(self, max_line_count, max_line_length):
        self.max_line_count = max_line_count
        self.max_line_length = max_line_length
        self.block_start = None
        self.block_end = None
        self.lines = [[] for _ in range(max_line_count)]
        self.current_line = 0
        self.delay = 0.0  # delay in seconds
        self.words = []  # Store word-level details (for animations)

    def add_word(self, word_timed):
        word = word_timed["word"]
        word_start = word_timed["start"]
        word_end = word_timed["end"]

        if self.block_start is None:
            self.block_start = word_start
        self.block_end = word_end  # Update end time

        # Check for line length and manage hyphenation
        current_line_length = sum(len(w["word"]) for w in self.lines[self.current_line])
        if current_line_length + len(word) > self.max_line_length and word[0] != "-":
            if self.current_line + 1 < self.max_line_count:
                self.current_line += 1
            else:
                return False  # Block is full

        # Add word to the current line
        self.lines[self.current_line].append(
            {"word": word, "start": word_start, "end": word_end}
        )
        self.words.append(
            {
                "word": word,
                "start": word_start,
                "end": word_end,
                "line": self.current_line,
            }
        )
        return True

    def is_complete_before(self, word_timed) -> bool:
        """Indicate if the upcoming word won't fit and a new block should be started"""
        word = word_timed["word"]
        current_line_length = sum(len(w["word"]) for w in self.lines[self.current_line])
        if current_line_length + len(word) > self.max_line_length and word[0] != "-":
            if self.current_line + 1 >= self.max_line_count:
                return True
        return False

    def do_yield(self, formatter, caption_settings: dict):
        delayed_start = self.block_start + self.delay
        delayed_end = self.block_end + self.delay

        primary_colour = caption_settings.get("primary_colour", "&H00FFFFFF")
        secondary_colour = caption_settings.get("secondary_colour", "&H00FF0000")

        default_color = f"\\1c&{primary_colour[4:]}"
        effect_color = f"\\1c&{secondary_colour[4:]}"

        blocktext = ""
        for line_num, line in enumerate(self.lines):
            animated_line = ""
            for word_data in line:
                word = word_data["word"]
                word_start = max(word_data["start"] + self.delay - delayed_start, 0.001)
                word_end = max(
                    word_data["end"] + self.delay - delayed_start, word_start
                )

                word_start = int(word_start * 1000)  # Convert to ms
                word_end = int(word_end * 1000)  # Convert to ms

                effect_str = "{"
                effect_str += default_color
                effect_str += f"\\t({word_start},{word_start},{effect_color})"
                effect_str += f"\\t({word_end},{word_end},{default_color})"
                effect_str += "}"

                animated_line += f"{effect_str}{word} "

            blocktext += animated_line.strip() + r"\N"  # Use \N for new line

        blocktext = blocktext.rstrip(r"\N")  # Remove trailing \N
        yield formatter(delayed_start), formatter(delayed_end), blocktext


class SubtitlesWriterTimed(SubtitlesWriter):
    """Write an .srt file after transcribing with word_timestamps enabled,
    imposing a maximum line length and number of lines per entry.
    """

    always_include_hours = True
    decimal_marker = "."

    def __init__(self, max_line_count=1, max_line_length=42):
        self.max_line_count = max_line_count
        self.max_line_length = max_line_length

    def iterate_result(self, result: dict, caption_settings: dict[str, Optional[str]]):
        block = SubtitleBlock(self.max_line_count, self.max_line_length)
        for segment in result["segments"]:
            for word_timed in segment["words"]:  # .word, .start, .end
                if block.is_complete_before(word_timed):
                    yield from block.do_yield(self.format_timestamp, caption_settings)
                    block = SubtitleBlock(self.max_line_count, self.max_line_length)
                block.add_word(word_timed)
        yield from block.do_yield(self.format_timestamp, caption_settings)

    def format_timestamp(self, seconds):
        """Converts time in seconds to ASS timestamp format (H:MM:SS.CS)."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)  # Convert fractional part to centiseconds
        return f"{h}:{m:02}:{s:02}.{cs:02}"

    def write_result(
        self, result: dict, file: TextIO, caption_settings: dict[str, Optional[str]]
    ):
        """
        Writes the subtitle result to an .ass file, including custom settings and animations.

        Args:
            result (dict): The transcription result containing subtitle segments.
            file (TextIO): The file object to write the subtitle output.
            caption_settings (dict): The dictionary containing font and animation settings.
        """

        # Extract and format settings from caption_settings
        font_name = caption_settings.get("font_name", "Arial")
        font_size = caption_settings.get("font_size", 50)
        primary_colour = caption_settings.get("primary_colour", "&H00FFFFFF")
        secondary_colour = caption_settings.get("secondary_colour", "&H00000000")
        outline_colour = caption_settings.get("outline_colour", "&H00000000")
        back_colour = caption_settings.get("back_colour", "&H00000000")
        bold = caption_settings.get("bold", 0)
        italic = caption_settings.get("italic", 0)
        underline = caption_settings.get("underline", 0)
        strikeout = caption_settings.get("strikeout", 0)
        border_style = caption_settings.get("border_style", 1)
        outline = caption_settings.get("outline", 1)
        shadow = caption_settings.get("shadow", 0)
        alignment = caption_settings.get("alignment", 5)
        playres_x = caption_settings.get("playres_x", 1080)
        playres_y = caption_settings.get("playres_y", 1920)

        # Extract animation settings
        # animation = caption_settings.get("animation", {})
        # effect = animation.get("effect", "")
        # duration_in = animation.get("duration_in", 0)
        # duration_out = animation.get("duration_out", 0)
        # x_movement = animation.get("x_movement", 0)
        # y_movement = animation.get("y_movement", 0)

        # Write the .ass file header
        file.write("[Script Info]\n")
        file.write("Title: Generated Subtitles with Animation\n")
        file.write("ScriptType: v4.00+\n")
        file.write(f"PlayResX: {playres_x}\n")
        file.write(f"PlayResY: {playres_y}\n")
        file.write("Timer: 100.0000\n\n")

        # Write styles
        file.write("[V4+ Styles]\n")
        file.write(
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        )
        file.write(
            f"Style: Default,{font_name},{font_size},{primary_colour},{secondary_colour},{outline_colour},{back_colour},{bold},{italic},{underline},{strikeout},100,100,0,0,{border_style},{outline},{shadow},{alignment},0,0,0,1\n\n"
        )

        # Write subtitle events
        file.write("[Events]\n")
        file.write(
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )

        for i, (start, end, text) in enumerate(
            self.iterate_result(result, caption_settings), start=1
        ):
            # Construct the effect string for animations
            # effect_str = f"{effect};fade({duration_in},{duration_out},{x_movement},{y_movement})" if effect else ""
            effect_str = ""
            file.write(
                f"Dialogue: 0,{start},{end},Default,,0,0,0,{effect_str},{text}\n"
            )


# Data types for Ass Subtitle
# Color
# Color values are expressed in hexadecimal BGR format as &HBBGGRR& or ABGR (with alpha channel) as &HAABBGGRR&. Transparency (alpha) can be expressed as &HAA&. Note that in the alpha channel, 00 is opaque and FF is transparent.
# Boolean values (Styles section)
# -1 is true, 0 is false.
# Alignment
# Alignment values are based on the numeric keypad. 1 - bottom left, 2 - bottom center, 3 - bottom right, 4 - center left, 5 - center center, 6 - center right, 7 - top left, 8 - top center, 9 - top right. In addition to determining the position of the subtitle, this also determines the alignment of the text itself.
# Time
# Time is expressed as h:mm:ss:xx (xx being hundredths of seconds). The hour can only be a single digit.
