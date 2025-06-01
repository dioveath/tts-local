import re


def split_text_into_chunks(text: str, max_chars: int = 2000) -> list[str]:
    """
    Splits a string into chunks of a maximum size, ensuring chunks
    end at sentence boundaries (., ?, !) where possible.

    Args:
        text: The string to split.
        max_chars: The maximum character length for each chunk. Defaults to 2000.

    Returns:
        A list of string chunks.
    """
    chunks = []
    start_index = 0
    text_length = len(text)

    # Clean the input text once (optional, but good practice)
    text = text.strip()
    text_length = len(text)

    while start_index < text_length:
        # Remove potential leading whitespace for the next chunk
        while start_index < text_length and text[start_index].isspace():
            start_index += 1

        # Break if we've processed the whole string
        if start_index >= text_length:
            break

        # Determine the maximum possible end index for this chunk
        # We add +1 because we might need to include the char at max_chars index if it's the boundary
        potential_end_index = min(start_index + max_chars, text_length)

        # If the remaining text is within the limit, it's the last chunk
        if potential_end_index == text_length:
            chunks.append(text[start_index:])
            break

        # --- Find the best split point ---
        best_split_index = -1

        # 1. Prioritize Sentence Endings (. ? !)
        # Search backwards from the potential end index
        possible_sentence_ends = []
        for punctuation in [".", "?", "!"]:
            # rfind searches [start, end) -> searches up to potential_end_index - 1
            index = text.rfind(punctuation, start_index, potential_end_index)
            if index != -1:
                # Check if it looks like a real sentence end (e.g., followed by space/newline or end)
                # This simple check helps avoid splitting mid-abbreviation like "Mr." or "e.g."
                # If index+1 is the end of search range OR is whitespace.
                if index + 1 == potential_end_index or text[index + 1].isspace():
                    possible_sentence_ends.append(index)

        if possible_sentence_ends:
            best_split_index = max(possible_sentence_ends)  # Get the latest possible sentence end

        # 2. If no sentence ending found, fall back to the last space
        if best_split_index == -1:
            # Search for the last space within the range [start_index, potential_end_index)
            space_index = text.rfind(" ", start_index, potential_end_index)
            if space_index != -1:
                best_split_index = space_index  # Split at the space

        # 3. If no sentence end or space found (e.g., very long word/URL), split at max_chars
        if best_split_index == -1:
            # Force split at the max character limit for this chunk
            split_point = potential_end_index
        else:
            # Otherwise, split point is right after the found punctuation or space
            split_point = best_split_index + 1

        # --- Add the chunk and update start index ---
        chunk = text[start_index:split_point].strip()  # Strip whitespace from the extracted chunk
        if chunk:  # Avoid adding empty chunks if stripping removes everything
            chunks.append(chunk)
        start_index = split_point  # Move start index for the next iteration

    return chunks


# --- Example Usage with your text ---
if __name__ == "__main__":
    post_text = """
    (r/scarystories) The King's Will\n\nPosted by u/Liam_Inheritance Blues\n\nOkay, i don't know where else to put this. Maybe i'm just freaking myself out in this huge old house, but things are getting weird, and i need to write it down somewhere. My grandfather died a couple of months back. I barely knew him, saw him maybe twice my whole life. He was rich, like old money rich, and lived out in this massive, crumbling estate miles from anywhere. Everyone locally called him 'The King' behind his back, partly because of the money, partly because he was just strange, kept to himself mostly.\n\nSo i get a call from a lawyer. Turns out, grandpa left me everything. The house, the grounds, the money, the whole lot. There was just one catch, laid out in his will, very specific. I have to live in this house, alone, for thirty days straight. No leaving the property overnight. And there are rules. Every single night, at midnight precisely, i have to go down to the main hall and wind the huge grandfather clock that stands there. Then, immediately after, i have to unlock the heavy oak door at the back of the kitchen. Just unlock it, not open it. Leave it unlocked until sunrise. I also have to read one page, just one, from his personal leather-bound journal before i go to sleep each night. Oh, and the big one: i must never, under any circumstances, open the door to the cellar.\n\nThirty days. That's it. Then i inherit a fortune that could sort my life out forever. I'm broke, like seriously struggling, so this felt like a lottery win, even with the weird conditions. Who wouldn't do it?\n\nI'm on day twelve now.\n\nThe first few days were just... strange. The house is enormous, way too big for one person. Every floorboard creaks, every pipe gurgles, the wind howls around the eaves like something trying to get in. It's dusty, filled with grandpa's collections \u2013 stuffed birds with glass eyes that seem to follow you, old maps of places that don't exist, creepy porcelain dolls lined up on shelves. Just endless rooms of shadows and silence.\n\nFollowing the rules felt stupid at first. Winding the clock is easy enough. It's a beautiful old thing, ornate carvings, deep resonant chime. But walking through the dark house to the kitchen afterwards, my footsteps echoing, fumbling with the heavy bolt on the back door... it feels wrong. Leaving a door unlocked all night in the middle of nowhere? Every instinct screams against it. But the lawyer was clear: follow the instructions exactly, or the deal's off, everything goes to some obscure historical society.\n\nThe journal is the weirdest part. It's not like a diary. The entries are short, fragmented. Early ones were just rambling thoughts, notes on the weather, complaints about taxes. But lately, they've gotten darker.\n\n*Day 5 entry: The wind carries whispers tonight. Must remember the schedule. It dislikes impatience.*\n\n*Day 7 entry: The lock requires oil. The mechanism must be smooth. Compliance ensures peace.*\n\n*Day 9 entry: Footsteps on the gravel path again. Fainter this time. It is learning the boundaries.*\n\nReading this stuff alone in a giant four-poster bed, with the wind moaning outside and knowing that back door is unlocked... it doesn't make for restful sleep. I started locking my bedroom door, even though that wasn't in the rules.\n\nThen, three nights ago, things changed. I wound the clock at midnight. The chime seemed louder that night, deeper, like it vibrated in my bones. I went to the kitchen, slid the bolt back on the oak door. Unlocked. As i turned to leave, i heard it. A faint scratching sound. From outside the back door.\n\nI froze. My heart felt like it jumped into my throat. It wasn't an animal, not a branch scraping. It was rhythmic. Slow. Scratch. Pause. Scratch. Pause. Like fingernails dragging down wood. I stood there in the dark kitchen for what felt like an hour, barely breathing, listening. The scratching continued for maybe a minute, then stopped. Silence rushed back in, thick and heavy. I didn't sleep at all that night. Just lay there, eyes wide open, listening to every creak of the house.\n\nThe next morning, i forced myself to check the back door. There were marks on it. Thin, parallel scratches in the weathered oak, near the bottom. They weren't deep, but they were definitely new. I touched them, my fingers trembling slightly. They felt almost smooth, worn down.\n\nLast night was worse. Midnight came. The clock chimed, each note hitting me like a hammer blow. I went downstairs, my legs feeling like lead. The air felt cold, colder than usual. I wound the clock. The winding key felt greasy in my hand, though i knew it wasn't. I walked to the kitchen. Unlocked the door. This time, the scratching started almost immediately. Louder. Faster. Desperate. And then, a low sound, like a breath being let out right on the other side of the wood. A long, slow, wet sigh.\n\nI backed away fast, bumping into the kitchen table. A plate rattled on the counter. The scratching stopped instantly. The sighing stopped. I ran back upstairs, didn't even bother with the journal, just locked my bedroom door and huddled under the covers. I could hear my own blood pounding in my ears.\n\nToday, i haven't left my room much. I keep thinking about the cellar. The door is at the end of the main hallway, near the grandfather clock. It's thick wood, like the back door, but with heavy iron bands across it and a huge, rusty padlock. Why can't i go in there? What did grandpa keep down there? The journal hasn't mentioned it directly, but some entries feel related.\n\n*Day 11 entry (last night's, i forced myself to read it this morning): It grows restless. The barrier weakens with neglect. Sustenance must be provided. The old ways must be honoured.*\n\nBarrier? Sustenance? What the hell did my grandfather get himself involved in? Was he keeping something *out* with the locked back door ritual? Or was he letting something *in*? And what's in the cellar? Is it connected?\n\nI keep hearing noises now, even during the day. Floorboards creaking upstairs when i'm downstairs. Doors clicking softly shut down long corridors. Whispers that vanish when i turn my head. I feel watched constantly. Not just by the creepy doll eyes or the stuffed birds. It feels like the whole house is watching me. Waiting.\n\nI have eighteen more days. Eighteen more nights of winding that clock, unlocking that door, listening for scratching, reading that cursed journal. The money feels less important now. But the thought of breaking the rules, of what might happen if i do... that feels even scarier than staying. The lawyer said grandpa was very insistent on these specific terms. Like his life, or something else, depended on it.\n\nAnd the cellar door. I keep finding myself standing near it. My hand hovers over the cold metal of the padlock. What happens if i just look? What was the 'sustenance'? What 'barrier'? Is whatever is scratching at the back door trying to get to something down there? Or is *it* down there, and the scratching is something else entirely?\n\nI don't know. I just know i'm scared. Really scared. The silence right now feels worse than the noises. It feels like it's holding its breath. Waiting for midnight.
    """

    max_characters = 2000
    chunks = split_text_into_chunks(post_text, max_chars=max_characters)

    # Print the results
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} (Length: {len(chunk)}) ---")
        print(chunk)
        print("-" * (len(f"--- Chunk {i+1} (Length: {len(chunk)}) ---") + 5) + "\n")

    # Verify lengths
    all_under_limit = all(len(chunk) <= max_characters for chunk in chunks)
    print(f"\nAll chunks under {max_characters} characters: {all_under_limit}")
