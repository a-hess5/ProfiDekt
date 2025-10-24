# ProfiDekt - MagiProf Card Search Application

ProfiDekt is a dual-stack web application for searching and browsing Magic: The Gathering-inspired professor cards. It consists of a Flask backend API and an Express.js frontend.

## Project Structure

```
ProfiDekt/
├── Backend/               # Flask API server
│   ├── app.py            # Main Flask application
│   ├── database.py       # Database connection and initialization
│   ├── instance/         # Database files (created automatically)
│   ├── card_csv/         # CSV files with card data
│   │   ├── cards22.csv
│   │   └── cardsMagi25.csv
│   ├── card_images/      # Card image files
│   ├── import_magiprof_initial.py  # Script to import MagiProf cards
│   └── import_pokidekt_initial.py  # Script to import PokiDekt cards
│
└── Frontend/             # Express.js web server
    ├── app.js           # Main Express application
    ├── routes/          # Route handlers
    │   ├── index.js     # Index/search page route
    │   ├── advanced_search.js
    │   ├── cards.js
    │   ├── full_view.js
    │   ├── home.js
    │   └── users.js
    ├── views/           # Pug templates
    │   ├── index.pug
    │   ├── home.pug
    │   ├── layout.pug
    │   └── ...
    ├── public/
    │   ├── stylesheets/ # CSS files
    │   ├── card_images/ # Card image files (mirror of Backend)
    │   └── images/      # Logo and UI images
    └── package.json
```

## Prerequisites

- **Node.js** (v14 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn** (Node package manager)
- **pip** (Python package manager)

## Installation & Setup

### 1. Backend Setup (Flask)

Navigate to the backend directory:
```bash
cd Backend
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or manually install:
```bash
pip install flask flask-cors pandas sqlite3
```

### 2. Initialize the Database

The database is created automatically when the Flask app starts, but you need to import card data:

```bash
python import_magiprof_initial.py
```

When prompted, type `yes` to confirm importing cards from the CSV files. This will:
- Create/reset the `cards` table
- Import 38 cards from `cards22.csv`
- Import 64 cards from `cardsMagi25.csv`

### 3. Frontend Setup (Express)

Open a new terminal and navigate to the frontend directory:
```bash
cd Frontend
```

Install Node dependencies:
```bash
npm install
```

## Running the Application

### Start the Backend (Flask API)

From the `Backend/` directory:
```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

The Flask API is now running on `http://localhost:5000`

### Start the Frontend (Express)

From the `Frontend/` directory (in a new terminal):
```bash
npm start
```

Or if npm start isn't configured:
```bash
node app.js
```

The Express server will start on `http://localhost:3000`

### Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## Troubleshooting

### Problem: Index page shows "No cards found"

**Solution:**

1. **Verify Flask is running**
   - Check that Flask is running on `http://localhost:5000`
   - Visit `http://localhost:5000/` - you should see a welcome message

2. **Verify database has data**
   - Stop Flask if it's running
   - Delete the database files:
     ```bash
     cd Backend/instance
     rm magiprof_database.db pokidekt_database.db
     cd ..
     ```
   - Re-import the card data:
     ```bash
     python import_magiprof_initial.py
     ```
   - When prompted, type `yes` to confirm
   - You should see: `✓ Successfully imported 102 total cards into magiprof_database.db`

3. **Restart Flask**
   - Start Flask again:
     ```bash
     python app.py
     ```

4. **Clear Node cache and restart**
   - Stop Express (Ctrl+C)
   - Restart Express:
     ```bash
     npm start
     ```

5. **Visit `/index` again**
   - Go to `http://localhost:3000/index`
   - You should now see 12 cards displayed with "Showing 12 of 102 cards"

### Problem: Card images aren't loading

**Symptoms:** See errors like `GET http://card_images/... net::ERR_NAME_NOT_RESOLVED`

**Solution:**

1. **Ensure card images exist in both locations:**
   - `Backend/card_images/`
   - `Frontend/public/card_images/`

2. **Check that image file paths are correct:**
   - Go to `http://localhost:3000/card_images/24-25/` in your browser
   - You should see card images listed
   - If not, verify the files exist in `Frontend/public/card_images/`

3. **Clear browser cache:**
   - Press Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
   - Clear cached images and files
   - Refresh the page

### Problem: Flask API is returning empty results

**Solution:**

1. **Check if the database exists:**
   ```bash
   cd Backend/instance
   ls -la  # On Windows: dir
   ```
   - You should see `magiprof_database.db`
   - If it doesn't exist, run the import script again

2. **Check if cards were imported:**
   - Start Python shell:
     ```bash
     python
     ```
   - Run these commands:
     ```python
     import sqlite3
     conn = sqlite3.connect('instance/magiprof_database.db')
     cursor = conn.cursor()
     cursor.execute("SELECT COUNT(*) FROM cards")
     print(cursor.fetchone()[0])
     ```
   - Should output: `102`
   - If it shows `0`, re-run the import script

### Problem: Connection refused or ECONNREFUSED errors

**Symptoms:** "Unable to load cards. Flask API Error: connect ECONNREFUSED"

**Solution:**

1. **Verify Flask is actually running:**
   - Check the terminal where you started Flask
   - Should show: `Running on http://127.0.0.1:5000`

2. **Check the port:**
   - Ensure Flask is on port 5000
   - Ensure Express is on port 3000
   - If ports are in use, kill the process or change the port

3. **On Windows (kill process on port 5000):**
   ```bash
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   ```

4. **On Mac/Linux (kill process on port 5000):**
   ```bash
   lsof -ti:5000 | xargs kill -9
   ```

5. **Restart both servers** after confirming ports are free

### Problem: "MagiProf database already exists" but cards still don't load

**Full Database Reset:**

1. **Stop both Flask and Express**

2. **Delete all database files:**
   ```bash
   cd Backend/instance
   rm -f magiprof_database.db pokidekt_database.db
   ```

3. **Re-import cards:**
   ```bash
   cd ..
   python import_magiprof_initial.py
   # Type 'yes' when prompted
   ```

4. **Start Flask:**
   ```bash
   python app.py
   ```

5. **In a new terminal, start Express:**
   ```bash
   cd ../Frontend
   npm start
   ```

6. **Visit `http://localhost:3000/index`** and verify cards load

## API Endpoints

### Flask API (Backend)

- `GET /` - Welcome message
- `GET /api/magiprof/cards` - Get all cards with pagination and search
  - Query params: `page`, `per_page`, `search`
  - Example: `/api/magiprof/cards?page=1&per_page=12&search=Dean`
- `GET /api/magiprof/cards/<id>` - Get a specific card by ID
- `GET /api/magiprof/cards/search` - Advanced search with multiple filters
- `POST /api/magiprof/cards` - Add a new card

### Express Routes (Frontend)

- `GET /` - Home page
- `GET /index` - Card search page (main interface)
- `GET /advanced` - Advanced search page
- `GET /full` - Full card view page
- `POST /search` - Search form submission

## Development Notes

### Adding New Cards

To add new cards to the database, update the CSV files:
- `Backend/card_csv/cards22.csv`
- `Backend/card_csv/cardsMagi25.csv`

Then re-run the import script:
```bash
python Backend/import_magiprof_initial.py
```

### Debugging

Both servers output debug logs to the console:

**Flask Console:**
- Shows API requests and responses
- Database queries
- Errors and exceptions

**Express Console:**
- Shows `[DEBUG /index]` logs with card counts and pagination info
- Route requests
- Database connection issues

Check the console output when troubleshooting.

## Common Issues Checklist

- [ ] Flask is running on `http://localhost:5000`
- [ ] Express is running on `http://localhost:3000`
- [ ] Database file exists at `Backend/instance/magiprof_database.db`
- [ ] Database has 102 cards imported
- [ ] Card images exist in both `Backend/card_images/` and `Frontend/public/card_images/`
- [ ] No firewall blocking localhost connections
- [ ] No other services using ports 3000 or 5000

## Support

If issues persist after following the troubleshooting guide:

1. Check the console output from both Flask and Express for error messages
2. Verify all file paths and directories exist
3. Ensure CSV files contain data: `Backend/card_csv/cards22.csv` and `Backend/card_csv/cardsMagi25.csv`
4. Try a complete database reset (delete instance folder, re-run import script)
