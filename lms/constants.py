CREATE = "1"
READ = "2"
UPDATE = "3"
DELETE = "4"

WEEKDAYS = {
    0: ("Monday", "Mon"),
    1: ("Tuesday", "Tue"),
    2: ("Wednesday", "Wed"),
    3: ("Thursday", "Thu"),
    4: ("Friday", "Fri"),
    5: ("Saturday", "Sat"),
    6: ("Sunday", "Sun"),
}

TERM_CHOICES = [
    ("Fall", "Fall"),
    ("Winter", "Winter"),
    ("Spring", "Spring"),
    ("Summer", "Summer"),
    ("Annual", "Annual"),
]

STATUS_CHOICES = (
    (0, "Not Active"),
    (1, "Active"),
    (2, "Deleted"),
)
