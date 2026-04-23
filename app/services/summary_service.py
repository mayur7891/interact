import time
import threading
from collections import Counter

import requests
from flask import current_app

# Per-video lock: prevents duplicate simultaneous Gemini calls for the same video
_generation_locks: dict = {}
_locks_mutex = threading.Lock()


def _get_video_lock(video_id: int) -> threading.Lock:
    with _locks_mutex:
        if video_id not in _generation_locks:
            _generation_locks[video_id] = threading.Lock()
        return _generation_locks[video_id]


def _get_gemini_url() -> str:
    model_name = current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash")
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"


def _call_gemini(prompt: str, retries: int = 3) -> str:
    """Send a prompt to Gemini with exponential backoff on 429."""
    api_key = current_app.config.get("GEMINI_API_KEY", "")
    model_name = current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    for attempt in range(retries):
        current_app.logger.info(
            "Gemini request started",
            extra={"attempt": attempt + 1, "retries": retries, "model": model_name},
        )
        resp = requests.post(
            _get_gemini_url(),
            params={"key": api_key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        if resp.status_code == 404:
            current_app.logger.error(
                "Gemini model not found",
                extra={"model": model_name, "response": resp.text[:300]},
            )
            raise RuntimeError(
                f"Configured Gemini model '{model_name}' is unavailable for this API key."
            )
        if resp.status_code == 429:
            wait = 2 ** attempt  # 1s, 2s, 4s
            current_app.logger.warning(
                "Gemini rate limited",
                extra={"attempt": attempt + 1, "wait_seconds": wait, "model": model_name},
            )
            time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    raise RuntimeError("Gemini API rate limit exceeded after retries. Try again shortly.")


def generate_fallback_summary(comments: list) -> str:
    """Build a deterministic local summary when Gemini is unavailable."""
    if not comments:
        return "No comments available to summarize."

    cleaned_comments = [comment.strip() for comment in comments if isinstance(comment, str) and comment.strip()]
    if not cleaned_comments:
        return "No comments available to summarize."

    token_counter = Counter()
    stop_words = {
        "the", "and", "for", "that", "this", "with", "have", "your", "you", "are", "was",
        "but", "not", "just", "they", "from", "their", "about", "really", "very", "video",
        "like", "love", "good", "great", "nice", "more", "would", "could", "what", "when",
    }
    for comment in cleaned_comments:
        for token in comment.lower().split():
            normalized = "".join(ch for ch in token if ch.isalnum())
            if len(normalized) >= 4 and normalized not in stop_words:
                token_counter[normalized] += 1

    top_topics = [token for token, _ in token_counter.most_common(5)]
    sample_comments = cleaned_comments[:3]

    summary_parts = [
        f"This summary is a local fallback built from {len(cleaned_comments)} comments because the AI summary service is currently unavailable.",
    ]
    if top_topics:
        summary_parts.append(f"The most common discussion themes are: {', '.join(top_topics)}.")
    if sample_comments:
        summary_parts.append("Representative feedback includes: " + " | ".join(sample_comments) + ".")
    summary_parts.append("Retry later to refresh this with a richer AI-generated summary.")
    return " ".join(summary_parts)


def generate_full_summary(comments: list, video_id: int = 0) -> str:
    """
    Generate a summary from scratch. Uses a per-video lock so concurrent
    requests don't trigger duplicate Gemini calls.
    """
    if not comments:
        return "No comments available to summarize."

    lock = _get_video_lock(video_id)
    if not lock.acquire(blocking=False):
        # Another request is already generating — wait for it then return cached
        current_app.logger.info(
            "Summary generation already in progress",
            extra={"video_id": video_id},
        )
        lock.acquire()
        lock.release()
        return None  # signal to caller to re-check cache

    try:
        current_app.logger.info(
            "Generating summary",
            extra={"video_id": video_id, "comment_count": len(comments)},
        )
        combined = "\n".join(f"- {c}" for c in comments[:200])
        prompt = (
            "You are an AI assistant helping a content creator understand audience feedback.\n"
            "Below are viewer comments for a video. Write a concise, insightful summary (3-5 sentences) "
            "covering the main themes, sentiment, and any recurring suggestions or complaints.\n\n"
            f"Comments:\n{combined}\n\n"
            "Summary:"
        )
        summary = _call_gemini(prompt)
        current_app.logger.info(
            "Summary generation completed",
            extra={"video_id": video_id, "summary_length": len(summary)},
        )
        return summary
    except Exception:
        current_app.logger.exception(
            "Gemini summary generation failed; using fallback summary",
            extra={"video_id": video_id},
        )
        return generate_fallback_summary(comments)
    finally:
        lock.release()


def update_rolling_summary(existing_summary: str, new_comment: str) -> str:
    prompt = (
        "You are an AI assistant maintaining a rolling summary of viewer comments for a video.\n"
        "Here is the current summary:\n"
        f"{existing_summary}\n\n"
        "A new viewer comment has just been posted:\n"
        f"- {new_comment}\n\n"
        "Update the summary to incorporate any new themes or insights from this comment. "
        "Keep the summary concise (3-5 sentences). If the comment doesn't add new information, "
        "return the existing summary unchanged.\n\n"
        "Updated summary:"
    )
    try:
        return _call_gemini(prompt)
    except Exception:
        current_app.logger.exception("Rolling summary update failed; keeping existing summary")
        return existing_summary


def generate_fallback_answer(summary: str, question: str) -> str:
    """Return a deterministic answer when Gemini is unavailable."""
    trimmed_summary = (summary or "").strip()
    trimmed_question = (question or "").strip()

    if not trimmed_summary:
        return "The AI assistant is temporarily unavailable and there is no cached summary to answer from yet."

    return (
        "The AI assistant is temporarily rate-limited, so this answer is based on the cached video summary instead. "
        f"Question: {trimmed_question}. "
        f"Current summary context: {trimmed_summary}"
    )
