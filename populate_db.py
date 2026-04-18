import os
import django
import pandas as pd


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DishCovery.settings')
django.setup()

from core.models import Restaurant

def populate():
    print("Mega Dataset is loading...")

    csv_file = 'final_mega_dataset.csv' 
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} नहीं मिली!")
        return

    df = pd.read_csv(csv_file)
    
    print("पुराना डेटा साफ़ किया जा रहा है...")
    Restaurant.objects.all().delete()

    restaurant_list = []
    for index, row in df.iterrows():
        res = Restaurant(
            name=row['name'],
            location=row['location'],
            locality=row.get('locality', ''),
            cuisine=row['cuisine'],
            rating=row['rating'],

            url=f"https://www.google.com/search?q={row['name'].replace(' ', '+')}+{row['location']}"
        )
        restaurant_list.append(res)

    
    Restaurant.objects.bulk_create(restaurant_list)
    print(f" Congratulations {len(restaurant_list)} restaurants successfully loaded!")

if __name__ == '__main__':
    populate()