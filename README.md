# Fitness Studio Booking API
## Setup Instructions

1. Make sure Python 3.7+ installed.

2. Create and activate a virtual environment:

```bash
python -m venv venv # virtual environment
source venv\Scripts\activate  # On Windows
```

3. Install dependencies:

```bash
pip install Flask Flask-SQLAlchemy pytz
```

4. Run the Flask app:

```bash
python app.py
```

The API will be available at `http://127.0.0.1:5000/`.

## API Endpoints

### GET /classes

Returns a list of all upcoming fitness classes.

Query Parameters:

- `timezone` (optional): Timezone name (e.g., `Asia/Kolkata`, `UTC`, `America/New_York`). Defaults to `Asia/Kolkata`.

In terminal:

```bash
curl "http://127.0.0.1:5000/classes?timezone=UTC"
```

```bash
In command prompt

curl -s "http://127.0.0.1:5000/classes?timezone=UTC"

```

### POST /book

Book a spot in a fitness class.

Request Body (JSON):

```json
{
  "class_id": 1,
  "client_name": "Dakshath Prasad R",
  "client_email": "dakshathprasadr1@gmail.com"
}
```

In terminal:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"class_id":1,"client_name":"Dakshath Prasad R","client_email":"dakshathprasadr1@gmail.com"}' http://127.0.0.1:5000/book
```

or
```bash

In powershell

Invoke-RestMethod -Uri http://127.0.0.1:5000/book -Method POST -Body '{"class_id":1,"client_name":"Dakshath Prasad R","client_email":"dakshathprasadr1@gmail.com"}' -ContentType "application/json"
```




```bash
In command prompt

curl -X POST -H "Content-Type: application/json" -d "{\"class_id\":1,\"client_name\":\"Dakshath Prasad R\",\"client_email\":\"dakshathprasadr1@gmail.com\"}" http://127.0.0.1:5000/book

```




### GET /bookings

Get all bookings made by a specific email address.

Query Parameters:

- `email` (required): Client email address.

In terminal:

```bash

curl "http://127.0.0.1:5000/bookings?email=dakshathprasadr1@gmail.com"
```




```bash
in command prompt

curl "http://127.0.0.1:5000/bookings?email=dakshathprasadr1@gmail.com"

```

## Testing

Used tools cURL to test the API endpoints.


