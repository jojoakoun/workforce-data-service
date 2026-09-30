from data_checks import (
    print_date_quality,
    print_department_quality,
    print_fte_quality,
    print_headcount_quality,
    print_reference_quality,
    print_tenure_quality,
    print_workforce_duplicates,
)


def main():
    print_department_quality()
    print_tenure_quality()
    print_headcount_quality()
    print_fte_quality()
    print_date_quality()
    print_reference_quality()
    print_workforce_duplicates()


if __name__ == "__main__":
    main()