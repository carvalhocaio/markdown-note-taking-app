import argparse
import random
import re
from collections.abc import Callable

from faker import Faker

from markdown_note_taking_app.config import settings
from markdown_note_taking_app.services.storage_service import StorageService


def slugify(text: str) -> str:
    """Convert a human-readable title into a safe filename slug."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:50] or "note"


def generate_meeting_note(fake: Faker) -> tuple[str, str]:
    topic = fake.catch_phrase()
    slug = f"meeting-{slugify(topic)}"
    date_str = fake.date()
    attendees = [fake.name() for _ in range(random.randint(3, 5))]
    attendees_md = "\n".join(f"- {name}" for name in attendees)

    action_items = [fake.sentence() for _ in range(random.randint(3, 4))]
    checklist_md = "\n".join(
        f"- [{'x' if random.random() > 0.5 else ' '}] {item}" for item in action_items
    )

    content = f"""# Meeting: {topic}

- **Date:** {date_str}
- **Facilitator:** {fake.name()}

## Attendees
{attendees_md}

## Agenda & Discussion
{fake.paragraph(nb_sentences=4)}

> {fake.sentence()}

{fake.paragraph(nb_sentences=3)}

## Action Items
{checklist_md}
"""
    return slug, content


def generate_technical_doc(fake: Faker) -> tuple[str, str]:
    service_name = fake.bs().title()
    slug = f"architecture-{slugify(service_name)}"

    content = f"""# System Architecture: {service_name}

## 1. Overview
{fake.paragraph(nb_sentences=4)}

## 2. API Definition
```json
{{
  "service": "{slug}",
  "version": "1.0.0",
  "endpoint": "/api/v1/{slugify(fake.word())}",
  "status": "healthy"
}}
```

## 3. Key Dependencies
- **Database:** PostgreSQL 16
- **Cache:** Redis 7.2
- **Message Broker:** RabbitMQ

## 4. Operational Notes
{fake.paragraph(nb_sentences=3)}
"""
    return slug, content


def generate_task_list(fake: Faker) -> tuple[str, str]:
    project = fake.catch_phrase()
    slug = f"tasks-{slugify(project)}"

    tasks = [fake.sentence() for _ in range(5)]
    tasks_md = "\n".join(
        f"- [{'x' if i < 2 else ' '}] **Step {i + 1}:** {task}"
        for i, task in enumerate(tasks)
    )

    content = f"""# Sprint Checklist: {project}

Target completion: {fake.future_date()}

## Priorities
{tasks_md}

## Notes
{fake.paragraph(nb_sentences=3)}
"""
    return slug, content


def generate_knowledge_base_article(fake: Faker) -> tuple[str, str]:
    concept = fake.catch_phrase()
    slug = f"kb-{slugify(concept)}"

    content = f"""# How-To: {concept}

*Author: {fake.name()} | Last updated: {fake.date()}*

## Introduction
{fake.paragraph(nb_sentences=3)}

## Step-by-Step Guide
1. **Prepare the environment:** {fake.sentence()}
2. **Execute configuration:** {fake.sentence()}
3. **Verify functionality:** {fake.sentence()}

## Best Practices
{fake.paragraph(nb_sentences=4)}
"""
    return slug, content


def generate_journal_entry(fake: Faker) -> tuple[str, str]:
    date_str = fake.date_this_year().isoformat()
    slug = f"log-{date_str}"

    content = f"""# Engineering Log - {date_str}

## What got done today
- {fake.sentence()}
- {fake.sentence()}
- {fake.sentence()}

## What was learned
{fake.paragraph(nb_sentences=3)}

## Blockers & Next Steps
{fake.paragraph(nb_sentences=2)}
"""
    return slug, content


GENERATORS: list[Callable[[Faker], tuple[str, str]]] = [
    generate_meeting_note,
    generate_technical_doc,
    generate_task_list,
    generate_knowledge_base_article,
    generate_journal_entry,
]


def seed_notes(
    storage: StorageService,
    count: int = 5,
    clear: bool = False,
    locale: str = "en_US",
) -> list[str]:
    """Generate and persist realistic Markdown notes using Faker."""
    fake = Faker(locale)

    if clear:
        for existing in storage.list_notes():
            file_path = storage.base_dir / existing.filename
            if file_path.is_file():
                file_path.unlink()

    created: list[str] = []
    for i in range(count):
        generator = GENERATORS[i % len(GENERATORS)]
        slug, content = generator(fake)
        # Ensure unique name if collision occurs
        filename = f"{slug}-{i + 1}.md" if count > len(GENERATORS) else f"{slug}.md"
        saved = storage.save_note(filename, content)
        created.append(saved.filename)

    return created


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed sample markdown notes using Faker",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of notes to generate (default: 5)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Remove existing notes before seeding",
    )
    parser.add_argument(
        "--locale",
        type=str,
        default="en_US",
        help="Faker locale (default: en_US, e.g. pt_BR)",
    )

    args = parser.parse_args()
    storage = StorageService(settings.storage_dir)
    created = seed_notes(
        storage=storage,
        count=args.count,
        clear=args.clear,
        locale=args.locale,
    )

    print(f"Successfully seeded {len(created)} note(s) into '{storage.base_dir}':")
    for name in created:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
