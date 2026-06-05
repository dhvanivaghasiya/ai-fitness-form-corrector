"""
Rep Counter — state-machine based repetition counter.

A rep is counted when the stage transitions: down → up.
This is robust across all three exercises (squat, pushup, bicep curl).
"""


class RepCounter:
    """
    Counts repetitions using an up/down state machine.

    State transitions:
        waiting → down   (no rep counted)
        down    → up     (rep counted!)
        up      → down   (ready for next rep)
    """

    def __init__(self):
        self.reps: int = 0
        self._stage: str = 'waiting'

    def update(self, new_stage: str) -> bool:
        """
        Feed the current stage. Returns True if a rep was just counted.

        Args:
            new_stage: 'up' | 'down' | 'waiting'
        """
        rep_counted = False

        if new_stage == 'down' and self._stage in ('up', 'waiting'):
            self._stage = 'down'

        elif new_stage == 'up' and self._stage == 'down':
            self.reps += 1
            self._stage = 'up'
            rep_counted = True

        elif new_stage == 'waiting':
            pass  # Keep current stage — transient frames

        return rep_counted

    def reset(self):
        """Reset rep count and stage."""
        self.reps = 0
        self._stage = 'waiting'

    @property
    def stage(self) -> str:
        return self._stage

    def __repr__(self):
        return f'<RepCounter reps={self.reps} stage={self._stage}>'
