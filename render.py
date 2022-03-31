from csv import DictReader
from datetime import datetime as dt

raw = """
.row.project
  .col-md-2.col-3
    h3.mb-0 %%%DAY%%%
    h5.month.mb-0 %%%MONTH%%%
    p 15:00-16:00
  .col-md-8.col-9
    p.author #[span.me %%%AUTHOR%%%]
    h4.title.mb-1
      | %%%TITLE%%%"""

raw_upcoming = """
.row.next
  .col-md-8.col-8
    p.author #[span.me %%%AUTHOR%%%]
    h2.title.mb-0.mt-1
      | %%%TITLE%%%
  .col-md-2.col-4
    h1.day %%%DAY%%%
    h4.month.mb-0 %%%MONTH%%%
    p 15:00-16:00
  .col-md-9.col-12.mt-sm-3.mt-lg-1
      p
        | %%%ABSTRACT%%%
      """


def render_talk(talk, upcoming=False):
    if upcoming:
        template = raw_upcoming
    else:
        template = raw

    # Parse date
    date = dt.strptime(talk['Date'], '%d/%m/%Y')

    # Get month name
    month = date.strftime('%B')

    # Get cardinal day without leading zero
    day = str(int(date.strftime('%d')))

    # Add suffix to day
    day += suffix(int(day))

    # Build the output
    output = template.replace('%%%DAY%%%', day)
    output = output.replace('%%%MONTH%%%', month)
    output = output.replace('%%%AUTHOR%%%', talk['Name'])
    output = output.replace('%%%TITLE%%%', talk['Title'])

    # Eventually add abstract
    if talk['Abstract'] and upcoming:
        output = output.replace('%%%ABSTRACT%%%', talk['Abstract'])
    else:
        output = output.replace('%%%ABSTRACT%%%', 'No abstract available')

    return output


def suffix(d):
    return 'th' if 11 <= d <= 13 \
            else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


if __name__ == '__main__':
    import argparse

    # Parse arguments
    parser = argparse.ArgumentParser(description='Render talks')
    parser.add_argument('-n', '--number', type=int, default=5,
                        help='Number of talks to render')
    parser.add_argument('-d', '--date', type=str,
                        help='Render page for a specific date '
                             '(format: DD/MM/YYYY)')
    parser.add_argument('csv_filename', type=str,
                        help='CSV file containing talks')
    args = parser.parse_args()

    # Parse CSV file into a dictionary
    with open(args.csv_filename, 'r') as fp:
        csv_reader = DictReader(fp)
        talks = list(csv_reader)

    # Get current datetime
    if not args.date:
        now = dt.now()
    else:
        now = dt.strptime(args.date, '%d/%m/%Y')

    # Filter talks
    talks = [talk for talk in talks if talk['Name']]
    future = [talk for talk in talks if dt.strptime(talk['Date'],
                                                    '%d/%m/%Y') > now]

    # Assign upcoming
    upcoming, future = future[0], future[1:]

    # Render upcoming
    with open('src/upcoming.pug', 'w') as f:
        f.write('.row.mt-4.mb-2\n')
        f.write('  h1 #[span.emoji 🚀] Upcoming\n')
        f.write(render_talk(upcoming, True))

    # Render future talks
    with open('src/next.pug', 'w') as f:
        if future:
            f.write('.row.mt-4.mb-4\n')
            f.write('  h1 #[span.emoji 🔮] Next Talks\n')
            # Write the next n talks
            for talk in future[:args.number]:
                f.write(render_talk(talk))
        else:
            f.write('')
