from typing import List, Tuple

# Equipment choices used across models
EQUIPMENT_CHOICES: List[Tuple[str, str]] = [
    ('barbell', 'Barbell'),
    ('bench', 'Bench'),
    ('bodyweight', 'Bodyweight Only'),
    ('dumbbells', 'Dumbbells'),
    ('full_gym_access', 'Full Gym Access'),
    ('kettlebells', 'Kettlebells'),
    ('pool', 'Pool'),
    ('pull_up_bar', 'Pull-up Bar'),
    ('resistance_bands', 'Resistance Bands'),
    ('running_trails', 'Running Trails'),
    ('squat_rack', 'Squat Rack'),
    ('yoga_mat', 'Yoga Mat'),
]

# Difficulty levels for exercises
DIFFICULTY_CHOICES: List[Tuple[int, str]] = [
    (1, 'Beginner'),
    (2, 'Intermediate'),
    (3, 'Advanced'),
    (4, 'Expert'),
    (5, 'Master')
]

# Fitness goals
GOAL_CHOICES: List[Tuple[str, str]] = [
    ('strength', 'Strength'),
    ('endurance', 'Endurance'),
    ('flexibility', 'Flexibility'),
    ('weight_loss', 'Weight Loss'),
    ('general_fitness', 'General Fitness'),
] 