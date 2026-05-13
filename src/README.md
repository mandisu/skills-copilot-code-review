# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- View live announcements from the database
- Manage announcements when signed in as a teacher

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get all announcements, including status metadata                    |
| GET    | `/announcements/active`                                           | Get only active announcements for the banner                        |
| POST   | `/announcements` (Authorization: Bearer token)                    | Create an announcement                                              |
| PUT    | `/announcements/{announcement_id}` (Authorization: Bearer token)  | Update an announcement                                              |
| DELETE | `/announcements/{announcement_id}` (Authorization: Bearer token)  | Delete an announcement                                              |
| POST   | `/auth/login?username={username}&password={password}`             | Login and receive a bearer token                                    |
| GET    | `/auth/check-session` (Authorization: Bearer token)              | Validate an existing teacher token                                  |
| POST   | `/auth/logout` (Authorization: Bearer token)                     | Invalidate the current teacher token                                |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

3. **Announcements** - Uses generated announcement identifiers:
   - Message text
   - Optional start date
   - Required expiration date
   - Created and updated timestamps

All data is stored in memory, which means data will be reset when the server restarts.
