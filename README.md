
# Website Online Shop

## E-commerce Platform

Website Online Shop is an e-commerce platform built using the Django framework. It allows users to browse and purchase products from the site, with the option to access and buy products even without logging in. Users can also like products to save them for later.

Additionally, users have the convenience of logging in using their Google accounts for a seamless shopping experience.


## Accessing the Online Shop

**Note:** The server is not running continuously. If you wish to access the online shop for testing or exploration, please contact the developer in advance and request server activation. Once the server is up and running, you will be provided with access to the Website Online Shop, and you can visit it by clicking the following link: 

🔗 https://django-online-shop.liara.run/


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

