
# Website Online Shop

## E-commerce Platform

Website Online Shop is an e-commerce platform built using the Django framework. It allows users to browse and purchase products from the site, with the option to access and buy products even without logging in. Users can also like products to save them for later.

Additionally, users have the convenience of logging in using their Google accounts for a seamless shopping experience.

## Screenshots

<img src="https://github.com/user-attachments/assets/9f713233-87ee-40a1-80e7-3effbe5766db" alt="Storefront">
<p>Home Page</p>

<img src="https://github.com/user-attachments/assets/09f6db90-5f64-49e6-a4ec-43acf5a2fb06" alt="Product Listing">
<p>Product Listing Page</p>

<img src="https://github.com/user-attachments/assets/22f420d1-0fad-49cf-9bbe-6eba0dd88ff0" alt="Shopping Cart">
<p>Modal View</p>

<img src="https://github.com/user-attachments/assets/72902a02-007b-4545-820d-a15579a32377" alt="Checkout">
<p>Product Detail</p>

<img src="https://github.com/user-attachments/assets/45c1dc29-882e-4784-8ba9-701c7b4deda4" alt="Order Confirmation">
<p>Product Detail</p>

<img src="https://github.com/user-attachments/assets/ab898458-35b7-46c3-a549-eebf690a1532" alt="User Profile">
<p>Product Detail</p>

## Installation

To set up and run the Website Online Shop project, follow these steps:

1. **Create a .env File:**
   Create a `.env` file in the project's root directory and configure the following environment variables:

   ```plaintext
   DOCKER_COMPOSE_DJANGO_SECRET_KEY=your-secret-key
   DOCKER_COMPOSE_DJANGO_DEBUG=debug-value
   ```

2. **Run Docker Compose:**
   Start the Docker containers using Docker Compose:

   ```bash
   docker-compose up
   ```

3. **Apply Migrations:**

   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

4. **Run the Server:**
   The project should now be accessible at `http://localhost:8000/`. You can explore the website and begin your online shopping experience.

## Main Third-Party Apps

Website Online Shop utilizes the following third-party apps:

- `allauth`: Provides authentication and account management functionality.
- `axes`: Protects the application from brute-force attacks by monitoring failed login attempts and locking out users after a specified number of unsuccessful tries.
- `django_filters`: Offers a simple way to filter querysets dynamically based on user input.
- `mptt`: Manages hierarchical data structures efficiently, such as categories or threaded comments.
- `rosetta`: Facilitates translations and multilingual support for the site.

