"""VoxFlow Post-Processor — Auto-correction for transcribed text.

Fixes common Whisper transcription errors, especially for Polish:
- Removes repeated phrases (Whisper hallucination)
- Fixes capitalization (first letter of sentences) 
- Cleans up punctuation
- Fixes common Polish word confusions
- Removes filler words/sounds
"""
import re
from typing import Optional


# Common Polish filler words/sounds that Whisper sometimes outputs
POLISH_FILLERS = {
    "yyy", "eee", "eem", "hmm", "uhm", "aaa", "aam",
    "no tak", "no wiesz", "znaczy się",
}

# Common Whisper mistakes for Polish (pattern → replacement)
POLISH_CORRECTIONS = {
    # Common phonetic confusions
    r"\bwięc\s+ze\b": "więc że",
    r"\bprze\s+de\s+wszystkim\b": "przede wszystkim",
    r"\bw\s+ogóle\b": "w ogóle",
    r"\bna\s+przykład\b": "na przykład",
    r"\btak\s+że\b": "także",
    r"\bto\s+znaczy\b": "to znaczy",
    r"\bdla\s+tego\b": "dlatego",
    r"\bpomi\s+mo\b": "pomimo",
    r"\bponieważ\s+że\b": "ponieważ",
    # Common encoding issues  
    r"\bze\s+by\b": "żeby",
    r"\bw\s+łaściwie\b": "właściwie",
    # Whisper sometimes outputs "..." or overly long pauses as text
    r"\.{3,}": "...",
    # Remove Whisper artifacts like [music], (applause), etc.
    r"\[.*?\]": "",
    r"\(.*?\)": "",
}

# Common English Whisper corrections
ENGLISH_CORRECTIONS = {
    r"\bgonna\b": "going to",
    r"\bwanna\b": "want to",
    r"\bgotta\b": "got to",
}


def post_process(
    text: str,
    language: str = "auto",
    fix_capitalization: bool = True,
    fix_punctuation: bool = True,
    remove_fillers: bool = True,
    fix_repetitions: bool = True,
    apply_corrections: bool = True,
) -> str:
    """Apply post-processing corrections to transcribed text.
    
    Args:
        text: Raw transcription text
        language: Detected language ("pl", "en", or "auto")
        fix_capitalization: Fix sentence capitalization
        fix_punctuation: Clean up punctuation issues
        remove_fillers: Remove filler words (yyy, eee, etc.)
        fix_repetitions: Remove repeated phrases (Whisper hallucination)
        apply_corrections: Apply language-specific corrections
        
    Returns:
        Cleaned and corrected text
    """
    if not text or not text.strip():
        return ""

    result = text.strip()

    # 1. Remove Whisper hallucination artifacts
    result = _remove_artifacts(result)

    # 2. Fix repeated phrases (common Whisper issue)
    if fix_repetitions:
        result = _fix_repetitions(result)

    # 3. Remove filler words
    if remove_fillers and language in ("pl", "auto"):
        result = _remove_fillers(result)

    # 4. Apply language-specific corrections
    if apply_corrections:
        if language in ("pl", "auto"):
            result = _apply_corrections(result, POLISH_CORRECTIONS)
        if language in ("en", "auto"):
            result = _apply_corrections(result, ENGLISH_CORRECTIONS)

    # 5. Fix punctuation
    if fix_punctuation:
        result = _fix_punctuation(result)

    # 6. Fix capitalization
    if fix_capitalization:
        result = _fix_capitalization(result)

    # 7. Final cleanup
    result = _final_cleanup(result)

    return result


def _remove_artifacts(text: str) -> str:
    """Remove Whisper-specific artifacts like [music], timestamps, etc."""
    # Remove bracketed/parenthesized content
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    # Remove timestamps like "00:00:00"
    text = re.sub(r"\d{1,2}:\d{2}(:\d{2})?", "", text)
    # Remove "Napisy...", "Subtitles...", "Dziękuję." at end (Whisper hallucinations)
    text = re.sub(r"\b(Napisy|Subtitles|Subscribe|Subskrybuj|Dziękuję za oglądanie|Thanks for watching)\.?\s*$", "", text, flags=re.IGNORECASE)
    return text.strip()


def _fix_repetitions(text: str) -> str:
    """Remove repeated phrases — a common Whisper hallucination.
    
    Detects patterns like "To jest test. To jest test. To jest test."
    and reduces them to a single occurrence.
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) <= 1:
        return text

    # Remove consecutive duplicate sentences
    deduped = [sentences[0]]
    for s in sentences[1:]:
        # Normalize for comparison (lowercase, strip)
        if s.strip().lower() != deduped[-1].strip().lower():
            deduped.append(s)

    result = " ".join(deduped)

    # Also detect repeated short phrases within a sentence
    # Pattern: "word word word word" → "word word" if repeated
    result = re.sub(r'\b(\w+(?:\s+\w+){1,4})\s+\1\b', r'\1', result, flags=re.IGNORECASE)

    return result


def _remove_fillers(text: str) -> str:
    """Remove filler words/sounds."""
    for filler in POLISH_FILLERS:
        # Remove filler as standalone word (with possible punctuation)
        pattern = r'\b' + re.escape(filler) + r'[,.]?\s*'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text.strip()


def _apply_corrections(text: str, corrections: dict) -> str:
    """Apply regex-based corrections."""
    for pattern, replacement in corrections.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _fix_punctuation(text: str) -> str:
    """Clean up punctuation issues."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Fix space before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    # Ensure space after punctuation
    text = re.sub(r'([.,!?;:])([A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż])', r'\1 \2', text)
    # Fix multiple punctuation
    text = re.sub(r'([.!?]){2,}', r'\1', text)
    # Remove dangling commas at start/end
    text = re.sub(r'^[,\s]+', '', text)
    text = re.sub(r'[,\s]+$', '', text)
    # Ensure sentence ends with punctuation
    text = text.strip()
    if text and text[-1] not in '.!?':
        text += '.'
    return text


def _fix_capitalization(text: str) -> str:
    """Fix capitalization: first letter of each sentence should be uppercase."""
    if not text:
        return text
    
    # Capitalize first character
    result = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # Capitalize after sentence-ending punctuation
    result = re.sub(
        r'([.!?]\s+)([a-ząćęłńóśźż])',
        lambda m: m.group(1) + m.group(2).upper(),
        result,
    )
    
    return result


def _final_cleanup(text: str) -> str:
    """Final cleanup pass."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Remove empty result edge case
    if text in ('.', '!', '?', ','):
        return ''
    return text


# ─── Polish-specific prompts to help Whisper ──────────────────────────────────

POLISH_INITIAL_PROMPT = (
    "Transkrypcja nagrania w języku polskim. "
    "Tekst zawiera poprawną polskę z użyciem znaków diakrytycznych: "
    "ą, ć, ę, ł, ń, ó, ś, ź, ż. "
    "Zdania są poprawne gramatycznie i ortograficznie."
)

ENGLISH_INITIAL_PROMPT = (
    "Transcription of a recording in English. "
    "The text uses proper grammar and punctuation."
)

AUTO_INITIAL_PROMPT = (
    "Transkrypcja nagrania. Tekst może być po polsku lub angielsku. "
    "Polski tekst zawiera poprawne znaki diakrytyczne: ą, ć, ę, ł, ń, ó, ś, ź, ż."
)


def get_initial_prompt(language: str) -> str:
    """Get the initial prompt for Whisper based on language.
    
    The initial_prompt biases Whisper towards producing correct output
    in the target language with proper diacritics and grammar.
    """
    if language == "pl":
        return POLISH_INITIAL_PROMPT
    elif language == "en":
        return ENGLISH_INITIAL_PROMPT
    else:
        return AUTO_INITIAL_PROMPT
