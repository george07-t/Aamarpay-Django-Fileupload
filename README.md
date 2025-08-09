# aamarPay Project

Welcome to the aamarPay Project! This repository is the starting point for integrating and working with the aamarPay payment gateway.

## Overview

This project aims to provide a seamless integration with aamarPay, enabling secure and efficient payment processing for your application.

## Features

- Easy integration with aamarPay API
- Secure payment transactions
- Basic setup and configuration

## Getting Started

1. **Clone the repository:**
    ```bash
    git clone https://github.com/george07-t/Aamarpay-Django-Fileupload.git
    ```
2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Configure your credentials:**
    - Create a `.env` file in the project root.
    - Add your aamarPay API credentials and configuration settings to the `.env` file. For example:
      ```
      AAMARPAY_STORE_ID=your_store_id
      AAMARPAY_SIGNATURE_KEY=your_signature_key
      AAMARPAY_SANDBOX_MODE=True
      ```
    - The application will automatically load these settings from the `.env` file.
4. **Docker**
    ```
    celery -A aamarpay_file_upload worker --loglevel=info --pool=solo
    docker-compose down
    pip freeze > requirements.txt
    docker-compose build --no-cache
    docker-compose up -d
    docker-compose logs web
```

## Usage

Refer to the documentation or code comments for details on how to use the payment integration.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements.

## License

This project is licensed under the MIT License.

---

*This README will be updated as the project evolves.*