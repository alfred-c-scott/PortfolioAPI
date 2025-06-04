import random
from datetime import datetime
from datetime import timedelta


import pdf417gen
from PIL import Image


def generate_license_string():
    # Lists for randomizing first, middle, and last names
    first_names = ['JAMES', 'EMILY', 'MICHAEL', 'SARAH',
                   'ROBERT', 'JENNIFER', 'DAVID', 'LAURA']
    middle_names = ['LEE', 'ANN', 'EDWARD', 'MARIE',
                    'THOMAS', 'ELIZABETH', 'CHARLES', 'ROSE']
    last_names = ['JOHNSON', 'BROWN', 'DAVIS', 'WILSON',
                  'CLARK', 'LEWIS', 'WALKER', 'HALL']
    eye_colors = ['BLU', 'BRN', 'GRN', 'HAZ', 'BLK', 'GRY']
    street_names = ['MAIN ST', 'PARK AVE', 'ELM ST', 'OAK DR',
                    'CEDAR LN', 'MAPLE RD', 'PINE ST', 'GROVE ST']
    city_zip_map = {
        'LEXINGTON': ['40508', '40502', '40503'],
        'BIRMINGHAM': ['35203', '35204', '35205'],
        'PHOENIX': ['85001', '85002', '85003'],
        'DENVER': ['80202', '80203', '80204'],
        'BOSTON': ['02108', '02109', '02110'],
        'SEATTLE': ['98101', '98102', '98103'],
        'MIAMI': ['33101', '33102', '33125'],
        'PORTLAND': ['97201', '97202', '97203']
    }
    states = ['KY', 'AL', 'AZ', 'CO', 'MA', 'WA', 'FL', 'OR']

    # Random selection of first, middle, and last names
    first_name = random.choice(first_names)
    middle_name = random.choice(middle_names)
    last_name = random.choice(last_names)

    # Customer ID: Starts with random letter, followed by 7 digits (same length as S07641612)
    customer_id = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ''.join(random.choices('0123456789', k=8))

    # Dates
    def random_date(start_date, end_date):
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return start_date + timedelta(days=random_days)

    issue_date = random_date(datetime(2016, 1, 1), datetime.now()).strftime('%m%d%Y')
    birth_date = random_date(datetime(1900, 1, 1), datetime.now() - timedelta(days=365*18)).strftime('%m%d%Y')
    expiration_date = random_date(datetime.now(), datetime.now() + timedelta(days=365*4)).strftime('%m%d%Y')
    last_update_date = random_date(datetime(2018, 1, 1), datetime.now()).strftime('%m%d%Y')

    sex = random.choice([1, 2])
    height = f'{random.randint(60, 84)} IN'
    eye_color = random.choice(eye_colors)

    # Address components
    street_number = random.randint(10, 9999)
    street_name = random.choice(street_names)
    street_address = f'{street_number} {street_name}'

    # City, state, and ZIP (consistent with each other)
    city = random.choice(list(city_zip_map.keys()))
    state = states[list(city_zip_map.keys()).index(city)]
    zip_code = random.choice(city_zip_map[city]) + '0000'  # Pad to 9 digits

    # Generate document discriminator and inventory control number (placeholders, random digits)
    document_discriminator = datetime.now().strftime('%Y%m%d%H%M%S') + ' ' + ''.join(random.choices('0123456789', k=5))
    inventory_control_number = '046' + ''.join(random.choices('0123456789', k=14))

    # Build the string with AAMVA tags and literal <LF>, <RS>, <CR> placeholders
    fields = [
        f"@<LF><RS><CR>ANSI 636046090002DL00410267ZK03080009DL",  # noqa: F541
        f'DAQ{customer_id}<LF>',
        f'DCS{last_name}<LF>',
        f'DDEN<LF>',  # noqa: F541
        f'DAC{first_name}<LF>',
        f'DDFN<LF>',  # noqa: F541
        f'DAD{middle_name}<LF>',
        f'DDGN<LF>',  # noqa: F541
        f'DCAD<LF>',  # noqa: F541
        f'DCBNONE<LF>',  # noqa: F541
        f'DCDNONE<LF>',  # noqa: F541
        f'DBD{issue_date}<LF>',
        f'DBB{birth_date}<LF>',
        f'DBA{expiration_date}<LF>',
        f'DBC{sex}<LF>',
        f'DAU{height}<LF>',
        f'DAY{eye_color}<LF>',
        f'DAG{street_address}<LF>',
        f'DAI{city}<LF>',
        f'DAJ{state}<LF>',
        f'DAK{zip_code}  <LF>',
        f'DCF{document_discriminator}<LF>',
        f'DCGUSA<LF>',  # noqa: F541
        f'DCK{inventory_control_number}<LF>',
        f'DDAN<LF>',  # noqa: F541
        f'DDB{last_update_date}<CR>',
        f'ZKZKADUP<CR>'  # noqa: F541
    ]

    # Join fields without adding actual ASCII delimiters here; they'll be replaced in generate_pdf417_barcode
    return ''.join(fields)


def generate_fake_dl_back(data):
    canvas_width = 1006
    canvas_height = 635
    barcode_position = None
    path = 'dev/images/id_card/jpeg'

    output_file = "fake_dl_back.jpeg"

    try:
        formatted_data = data.replace("<LF>", chr(10)).replace("<RS>", chr(30)).replace("<CR>", chr(13))

        barcode = pdf417gen.encode(
            formatted_data,
            columns=20,
            security_level=5
        )

        barcode_image = pdf417gen.render_image(
            barcode,
            scale=2,
            ratio=2,
            padding=5
        )

        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')

        if barcode_position is None:
            barcode_width, barcode_height = barcode_image.size
            x = (canvas_width - barcode_width) // 2
            y = (canvas_height - barcode_height) // 2

        else:
            x, y = barcode_position

        if x < 0 or y < 0 or (x + barcode_width > canvas_width) or (y + barcode_height > canvas_height):
            print(f"Warning: Barcode dimensions {barcode_width}x{barcode_height} at position ({x}, {y}) "
                  f"do not fit within canvas {canvas_width}x{canvas_height}. Adjusting position or size may be needed.")

        canvas.paste(barcode_image, (x, y))

        canvas.save(f"{path}/{output_file}", "JPEG", quality=100)

        print(f"Barcode image saved as: {output_file}")

    except Exception as e:
        print(f"Barcode generation failed: {e}")


def generate():
    data = generate_license_string()
    print(data)
    generate_fake_dl_back(data)
