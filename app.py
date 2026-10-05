from flask import Flask, jsonify, request, render_template
from scraper import scrape_circulars
from database import create_table, save_circulars, get_circulars
import json
import re
from pathlib import Path

app = Flask(__name__)
create_table()

KNOWLEDGE_FILE = Path(__file__).parent / "gmiu_knowledge.json"


def load_knowledge():
    try:
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def find_topic(message):
    topics = {
        "fees": ["fee", "fees", "payment", "tuition", "cost", "charges"],
        "admissions": ["admission", "enroll", "apply", "application", "eligibility"],
        "courses": ["course", "program", "degree", "diploma", "btech", "b.tech"],
        "scholarships": ["scholarship", "mysy", "nsp", "tfws", "financial aid"],
        "syllabus": ["syllabus", "curriculum", "subject", "semester"],
        "placements": ["placement", "recruiter", "internship", "job", "career"],
        "institutes": ["institute", "department", "faculty", "school", "academic units"],
        "facilities": ["facility", "campus", "library", "transport", "hostel", "sports"],
        "cells": ["cell", "nss", "startup", "international", "research"],
        "activities": ["activity", "activities", "event", "events", "club", "clubs", "competition"],
        "circulars": ["circular", "notice", "notices"]
    }

    for topic, words in topics.items():
        if any(word in message for word in words):
            return topic

    return None



def search_knowledge(message, topic=None):
    pages = load_knowledge()

    stop_words = {
        "the", "is", "are", "a", "an", "of", "in", "at", "to", "for",
        "me", "tell", "about", "what", "how", "many", "show", "please",
        "gmiu", "and", "with", "can", "you", "i", "want", "know", "do",
        "does", "which", "where", "when", "my", "your", "on", "that",
        "held", "happening", "give", "explain", "information", "please"
    }

    synonyms = {
        "activities": ["activity", "events", "event"],
        "activity": ["activities", "events", "event"],
        "events": ["event", "activities", "activity"],
        "event": ["events", "activities", "activity"],
        "computer": ["engineering"],
        "engineering": ["computer"],
        "students": ["student"],
        "student": ["students"],
        "fees": ["fee"],
        "fee": ["fees"],
        "scholarships": ["scholarship"],
        "scholarship": ["scholarships"]
    }

    query_words = {
        word for word in re.findall(r"[a-z0-9]+", message.lower())
        if word not in stop_words and len(word) > 1
    }

    expanded_words = set(query_words)
    for word in query_words:
        expanded_words.update(synonyms.get(word, []))

    results = []

    for page in pages:
        title = str(page.get("title", ""))
        content = str(page.get("content", ""))
        url = str(page.get("url", ""))

        title_lower = title.lower()
        content_lower = content.lower()

        title_score = sum(
            8 for word in expanded_words if word in title_lower
        )

        sentences = re.split(r"(?<=[.!?])\s+|[\n\r]+", content)
        relevant_sentences = []

        for sentence in sentences:
            sentence = re.sub(r"\s+", " ", sentence).strip()

            if len(sentence) < 35 or len(sentence) > 500:
                continue

            sentence_lower = sentence.lower()

            # Ignore common website navigation/menu text.
            if any(term in sentence_lower for term in [
                "menu home", "quick links", "sitemap", "apply now",
                "virtual counselling", "search results", "read more",
                "brochures", "contact us"
            ]):
                continue

            matched = [
                word for word in expanded_words
                if word in sentence_lower
            ]

            if not matched:
                continue

            sentence_score = len(matched) * 3

            # Give extra weight to sentences matching the actual question.
            sentence_score += sum(
                3 for word in query_words if word in sentence_lower
            )

            relevant_sentences.append((sentence_score, sentence))

        relevant_sentences.sort(key=lambda item: item[0], reverse=True)

        if relevant_sentences:
            best_sentences = [
                sentence for score, sentence in relevant_sentences[:3]
            ]

            results.append({
                "score": title_score + relevant_sentences[0][0],
                "title": title,
                "content": " ".join(best_sentences),
                "url": url
            })

    results.sort(key=lambda item: item["score"], reverse=True)

    # Return only the best matching page instead of dumping several pages.
    return results[:1]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/circulars")
def circulars():
    fresh_data = scrape_circulars()
    save_circulars(fresh_data)
    data = get_circulars()

    search = request.args.get("search", "").lower().strip()

    if search:
        data = [
            circular for circular in data
            if search in circular["title"].lower()
        ]

    return jsonify(data)


@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True) or {}
    user_message = str(body.get("message", "")).strip()
    message = user_message.lower()

    if not message:
        return jsonify({"reply": "Please enter a question."}), 400

    greetings = [
        "hi", "hello", "hey", "hii", "good morning", "good evening"
    ]

    if message in greetings:
        return jsonify({
            "reply": (
                "Hello! 👋 Welcome to GMIU Student Assistant. "
                "Ask me anything about GMIU, including courses, fees, "
                "admissions, scholarships, activities, events, placements, "
                "departments, student cells and campus facilities."
            )
        })

    topic = find_topic(message)

    # Search the knowledge base even when no predefined topic is detected.
    results = search_knowledge(message, topic)

    if not results:
        return jsonify({
            "reply": (
                "I couldn't find a relevant answer in my current GMIU "
                "knowledge base. You can try asking in a different way, "
                "or check the official GMIU website for verified details."
            )
        })

    item = results[0]
    content = re.sub(r"\s+", " ", item["content"]).strip()

    reply = f"📌 {item['title']}\n\n"

    if content:
        reply += content + "\n\n"
    else:
        reply += "I found a related GMIU page, but it does not contain a clear answer to your exact question.\n\n"

    if item["url"]:
        reply += f"🔗 Official page: {item['url']}"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
