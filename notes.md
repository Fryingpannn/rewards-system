# Notes

These are some notes I took during the development of the project.

## Requirements
### Functional reqs
- process a receipt (json)
    - store information
    - calculate points (? depends how fast) 
        - asynchronous (?)
    - generate id for it
        - ID must be unique, so we don't get the wrong points
- get points
    - retrieve receipt for given id
    - calculate points (? if fast, can just get here and cache)
    - return points

### Non functional reqs
- Scale
    - Processing receipt will probably happen more often than getting points
    - Need to be able to process a lot of receipts concurrently
- Availability > consistency
    - OK if someone doesn't see points immediately after processing
- Security: ok

## Entities
(both should perform input validation, return error if invalid)
- Receipt
- Item


## API
- `POST /receipts/process -> str`
    - Body: JSON of receipt
    - Store in "DB"
    - Returns: ID of new receipt
- `GET /receipts/{id}/points -> int`
    - Returns points


## Points calculation
- One point for every alphanumeric character in the retailer name.
    - O(N) n  being retailer name
- 50 points if the total is a round dollar amount with no cents.
    - O(N) n being length of price, shouldn't be that big.
    - Can split on the "." and check "00", if no ".", then is round dollar.
- 25 points if the total is a multiple of 0.25.
    - O(1): total % 0.25 == 0
- 5 points for every two items on the receipt.
    - O(1): total // 2
- If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned.
    - O(I * S) where I is number of items and S length of avg string. Checking multiple  and multiplying price is O(1)
- 6 points if the day in the purchase date is odd.
    - O(1): just check last 2 numbers % 2 != 0
- 10 points if the time of purchase is after 2:00pm and before 4:00pm.
    - assuming excludes 2pm and excludes 4pm since did not mention equality
    - O(1) since length of time is constant. Just compare numbers

## Conclusion

All operations for points calculation are fairly fast. Only retailer name and items multiple of 3 are the 2 that can be slow. But even so, retailer names should mostly be < 1000 characters, and same thing for number of items bought if user facing.

-> Calculate points during getPoints, then cache it. I would guess that most people probably don't look at points in all their reward apps. But those who do are more likely to look at it often. If the way the points are calculated changes, we can simply update the cache and not recalculate every single receipt.