import csv
from datetime import datetime
from typing import Any

class DeterministicRAGEngine:
    def __init__(self, notes_path: str):
        with open(notes_path, newline='', encoding='utf-8-sig') as notes_file:
            self.notes_df = list(csv.DictReader(notes_file))

        # Standardize date dimensions if contained in schema
        for col in ['start_date', 'end_date', 'date']:
            for row in self.notes_df:
                value = row.get(col)
                if value:
                    try:
                        row[col] = datetime.fromisoformat(value)
                    except ValueError:
                        pass

    def retrieve_context(self, origin: str, destination: str, week_of: Any) -> str:
        """Filters disruptions down to clear spatial intersections."""
        possible_notes = [
            row for row in self.notes_df
            if ((row.get('origin') == origin and row.get('destination') == destination)
                or row.get('scope') in {'global', 'macro', 'national'})
        ]
        
        context_blocks = []
        for row in possible_notes:
            block = f"Note ID: {row.get('note_id', 'UNKNOWN')}\n" \
                    f"Details: {row.get('event_description', row.get('note_text', ''))}\n"
            context_blocks.append(block)
            
        if not context_blocks:
            return "No contextual disruption records found for this location or timeframe."
            
        return "\n---\n".join(context_blocks)
