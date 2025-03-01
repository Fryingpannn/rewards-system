# Receipt Processor Service

A web service that processes receipts and awards points based on specific rules. The service provides two main endpoints: one for submitting receipts, and another for retrieving points awarded for a specific receipt.

## How To Run

### With Docker

1. Clone repository
2. `chmod +x docker-entrypoint.sh`
3. `docker build -t receipt-processor .` (or directly pull from [Dockerhub](https://hub.docker.com/r/fryingpannn/receipt-processor) `docker pull fryingpannn/receipt-processor `)
4. `docker run -p 8080:8080 receipt-processor`

Run tests: `docker run receipt-processor test`

### Or without Docker
1. Clone the repository
2. Install dependencies:
   `pip install -r requirements.txt`
3. `python main.py`

Run tests: `python -m unittest discover tests` or `pytest tests/test_routes.py -v` 

Example query:

```
curl localhost:8080/receipts/process -H "Content-Type: application/json" -X POST -d '{
  "retailer": "Target",
  "purchaseDate": "2022-01-01",
  "purchaseTime": "13:01",
  "items": [
    {
      "shortDescription": "Mountain Dew 12PK",
      "price": "6.49"
    },{
      "shortDescription": "Emils Cheese Pizza",
      "price": "12.25"
    },{
      "shortDescription": "Knorr Creamy Chicken",
      "price": "1.26"
    },{
      "shortDescription": "Doritos Nacho Cheese",
      "price": "3.35"
    },{
      "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
      "price": "12.00"
    }
  ],
  "total": "35.35"
}'
```

Then take the generated ID to run the following query:

```
curl localhost:8080/receipts/{generated_id_here}/points 
```

## Architecture Overview

The service is built using Python Flask.

### Key Components

- **Route Handlers**: Implemented in `api/routes.py`, handles HTTP requests and responses
- **Storage**: Uses two main storage components:
  - In-Memory Cache: Stores calculated points for receipts
  - Database: Stores receipt data (the DB is simulated with an in-memory hashmap)

### Design Decisions & Tradeoffs

1. **Points Calculation Strategy**
   - Points are calculated on-demand when requested rather than at receipt submission
   - Benefits:
     - Reduced initial processing time for receipt submission
     - Points calculation rules can be updated without needing to recalculate all historical receipts
     - Only calculate points for receipts that are actually queried
   - Tradeoffs:
     - Slightly longer response time for first points query
     - Additional in-memory usage for caching

2. **Storage Implementation**
   - Persistent database is simulated with an in-memory hashmap since we're not using 3rd party databases.

3. **Error Handling**
   - Input validation: receipts that have wrongly formatted texts/prices will be refused.
     - In a real app, depending on the use case, could prompt user to enter manually if a field doesn't fit the schema.
   - Clear error messages for invalid receipts.

4. **Performance Considerations**
   - Points calculation time complexity will be O(N) where N is the length of names and number of items. But these are < 1000 chars/items most of the time so it's fairly insignificant. For more details on time considerations see `nodes.md`.
   - Space complexity (without counting the simulated database) would be O(N) where N is the number of receipts. In the worse case every receipt has points retrieved and is all stored in cache. This can be pretty bad since we can have a lot of receipts. We would want to have an external cache like Redis.

## API Endpoints

### 1. Process Receipt
- **POST** `/receipts/process`
- Accepts receipt JSON data
- Returns unique ID for the receipt
- Performs validation on input data
- Status codes: 200 (success), 400 (invalid input)

### 2. Get Points
- **GET** `/receipts/{id}/points`
- Returns points calculated for given receipt ID
- Calculates points on first request and caches result
- Status codes: 200 (success), 404 (not found)

## Testing

The project includes test cases covering:
- Happy path scenarios with various receipt examples
- Input validation
- Error cases
