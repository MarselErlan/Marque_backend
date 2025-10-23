# 🚀 Start Server and Test

## The Issue

The server wasn't running when you tried to test! That's why you got "Connection refused".

## Solution: Start Server in One Terminal

### Terminal 1: Start Server

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
source venv/bin/activate
python3 -m uvicorn src.app_01.main:app --reload --port 8000
```

**Wait for this message:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Terminal 2: Run Test

Open a NEW terminal window:

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
source venv/bin/activate
python3 test_addresses_live.py
```

## Or Use Background Mode

If you want the server in background:

```bash
# Start server in background
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
source venv/bin/activate
python3 -m uvicorn src.app_01.main:app --reload --port 8000 > server.log 2>&1 &

# Wait 10 seconds
sleep 10

# Check if it's running
curl http://127.0.0.1:8000/health

# If you see JSON response, server is ready!
# Now run the test
python3 test_addresses_live.py
```

## Quick Check: Is Server Running?

```bash
curl http://127.0.0.1:8000/health
```

**Expected response:**

```json
{ "status": "healthy", "service": "marque-api" }
```

## Now Run the Address Test!

```bash
python3 test_addresses_live.py
```

You'll see:

1. Authentication step (enter SMS code)
2. Address creation
3. **DATABASE VERIFICATION** ✅
4. Address appears in GET request

This proves the API actually writes to the database!
