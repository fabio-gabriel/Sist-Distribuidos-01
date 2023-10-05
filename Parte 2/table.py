# Example input
# data = [
#    ["Device", "Status", "Data"],
#    ["Device 1", "On", 5],
#    ["Device 2", "Standby", 17],
#    ["Device 3", "Off", 1],
# ]


def print_table(data):
    # Define your table-printing logic here (same as in the previous answer)
    def print_row(row):
        # Define the column widths
        col_widths = [max(len(str(item)) for item in col) for col in zip(*data)]

        # Create a format string with proper column widths
        format_string = "  ".join(["{{:<{}}}".format(width) for width in col_widths])

        # Print the row with the format string
        print(format_string.format(*row))

    # Print the table header
    print_row(data[0])

    # Print the data rows
    for row in data[1:]:
        print_row(row)
