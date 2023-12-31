import requests
import csv
from bs4 import BeautifulSoup
import re

# Headers with a different user-agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}


# Create a CSV file to store the data
csv_file = open('products.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Product Name', 'Product URL', 'Product Price', 'Rating', 'Number of Reviews'])

# Function to filter elements with aria-label attribute
def has_aria_label(tag):
    return tag.has_attr('aria-label') and tag.name == 'span'

# Loop through multiple pages
for page in range(1, 21 ):  # Change the range based on the number of pages you want to extract
    # URL for the page with products
    url = f'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{page}'

    # Send an HTTP GET request to the URL
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        print(f"Request for page {page} successful")
    else:
        print(f"Request for page {page} failed")
        continue  # Skip to the next page if request fails

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all product containers
    product_containers = soup.find_all('div', class_='s-card-container')

    # Loop through each product container and extract information
    for container in product_containers:
        # Extract product name
        product_name_element = container.find('span', class_='a-size-medium a-color-base a-text-normal')
        if product_name_element:
            product_name = product_name_element.text.strip()
            # Extract product URL
            product_url_element = container.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')
            if product_url_element:
                product_url = product_url_element['href']
                if not product_url.startswith('https://'):
                    product_url = 'https://www.amazon.in' + product_url
            else:
                product_url = "N/A"

            # Extract product price
            product_price_element = container.find('span', class_='a-price-whole')
            if product_price_element:
                product_price = product_price_element.text.strip()
            else:
                product_price = "N/A"

            # Extract product rating
            rating_element = container.find('i', class_='a-icon-star-small')
            if rating_element:
                rating = rating_element.span.text.strip()
            else:
                rating = "N/A"

            # Extract number of reviews using the custom function
            num_reviews_element = container.find('div', class_='a-row a-size-small')
            if num_reviews_element:
                num_reviews_span = num_reviews_element.find_all(has_aria_label)
                if len(num_reviews_span) >= 2:
                    num_reviews = num_reviews_span[1]['aria-label']
                else:
                    num_reviews = "N/A"
            else:
                num_reviews = "N/A"

            # Check if any of the values are "N/A" before writing to the CSV file
            if product_name != "N/A" and product_url != "N/A" and product_price != "N/A" and rating != "N/A" and num_reviews != "N/A":
                csv_writer.writerow([product_name, product_url, product_price, rating, num_reviews])

# Close the CSV file
csv_file.close()

print("Data extracted and saved to product_data.csv")

# Create a CSV file to store the updated data
csv_file_updated = open('Each-product-with-their-data.csv', 'w', newline='', encoding='utf-8')
csv_writer_updated = csv.writer(csv_file_updated)
csv_writer_updated.writerow(['Product Name', 'Product URL', 'Product Price', 'Rating', 'Number of Reviews', 'Description', 'ASIN', 'Product Description', 'Manufacturer'])

# Read the CSV file containing the product data
with open('products.csv', 'r', encoding='utf-8') as input_csv:
    csv_reader = csv.reader(input_csv)
    next(csv_reader)  # Skip the header row

    for row in csv_reader:
        product_name, product_url, product_price, rating, num_reviews = row

        # Send an HTTP GET request to the product URL
        response_product = requests.get(product_url, headers=headers)
        soup_product = BeautifulSoup(response_product.content, 'html.parser')

        # Extract manufacturer from the ul
        manufacturer = "N/A"
        ul_element = soup_product.find('ul', class_='a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list')
        if ul_element:
            li_elements = ul_element.find_all('li')
            for li in li_elements:
                span_elements = li.find_all('span')
                for i in range(len(span_elements) - 1):
                    if "Manufacturer" in span_elements[i].text:
                        manufacturer = span_elements[i + 2].text.strip()
                        break

        # Extract ASIN from the ul
        asin = "N/A"
        if ul_element:
            li_elements = ul_element.find_all('li')
            for li in li_elements:
                span_elements = li.find_all('span')
                for i in range(len(span_elements) - 1):
                    if "ASIN" in span_elements[i].text:
                        asin = span_elements[i + 2].text.strip()
                        break

        # Extract product description from the productDescription div
        product_description_element = soup_product.find('div', id='productDescription_feature_div')
        if product_description_element:
           # Skip h2 elements within the product description
          for h2_element in product_description_element.find_all('h2'):
              h2_element.decompose()  # Remove the h2 element from the HTML

         # Get the text content of the remaining elements
        product_description = product_description_element.get_text(strip=True)

        # Extract description from the feature-bullets div
        feature_bullets_element = soup_product.find('div', id='feature-bullets')
        if feature_bullets_element:
            description_elements = feature_bullets_element.find_all(['span', 'li'], class_='a-list-item')
            description = '\n'.join(item.get_text(strip=True) for item in description_elements)
        else:
            description = "N/A"

        # Write the updated data to the CSV file
        csv_writer_updated.writerow([product_name, product_url, product_price, rating, num_reviews, description, asin, product_description, manufacturer])


# Close the CSV file
csv_file_updated.close()

print("Each-product-with-their-data.csv")