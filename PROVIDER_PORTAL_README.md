# NepSewa Provider Portal

## Overview
The Provider Portal allows service providers to register, login, and manage their profiles on NepSewa.

## Features

### 1. Provider Registration (`/register-provider`)
- **Original registration form** with enhanced features
- Providers fill out:
  - Full Name
  - Phone Number
  - **Email Address** (new)
  - **Password** (new)
  - Service Type
  - Location
  - Years of Experience
  - Profile Image (optional)
  - Available Days
- After registration with email/password, providers are redirected to the **Provider Login Portal**

### 2. Provider Login Portal (`/provider/login`)
- Secure login with email and password
- Session-based authentication
- Redirects to provider dashboard after successful login

### 3. Provider Dashboard (`/provider/dashboard`)
- **Welcome message** with provider name
- **Verification Status Banner**:
  - Yellow banner if account is pending verification
  - Green banner if account is verified
- **Statistics Cards**:
  - Completed Jobs
  - Rating (out of 5)
  - Number of Reviews
  - Estimated Earnings (Rs.)
- **Profile Overview**:
  - Profile picture/avatar
  - Name, service type, location
  - Phone, email, experience
  - Bio (if provided)
- **Quick Actions**:
  - Edit Profile
  - View Website
  - Browse Services

### 4. Provider Profile Editor (`/provider/profile`)
- **Edit Basic Information**:
  - Full Name
  - Phone Number
  - Location (dropdown)
  - Years of Experience
  - Profile Image URL
  - Bio/About section
- **Update Availability**:
  - Select available days (Mon-Sun)
  - Visual checkbox interface
- **Restrictions**:
  - Email cannot be changed (contact admin)
  - Service type cannot be changed (contact admin)
- Real-time form validation
- Success/error messages

## Database Schema Updates

### New Columns in `service_providers` table:
```sql
email VARCHAR(180) UNIQUE  -- Provider email for login
password VARCHAR(256)       -- Hashed password
bio TEXT                    -- Provider bio/description
```

## API Endpoints

### Provider Authentication
- `POST /api/provider/register` - Register new provider (alternative endpoint)
- `POST /api/provider/login` - Login to provider portal
- `GET /api/provider/me` - Get current provider profile
- `PUT /api/provider/update` - Update provider profile
- `GET /api/provider/stats` - Get provider statistics
- `GET /provider/logout` - Logout from provider portal

### Original Registration (Enhanced)
- `POST /api/register-provider` - Register provider (now includes email/password)

## User Flow

### New Provider Registration:
1. Visit `/register-provider` (from "Become a Provider" link)
2. Fill out registration form including email and password
3. Submit form
4. Account created (unverified by default)
5. Redirected to `/provider/login`
6. Login with email and password
7. Access provider dashboard

### Existing Provider Login:
1. Visit `/provider/login`
2. Enter email and password
3. Access provider dashboard
4. View stats, edit profile, manage availability

### Provider Profile Management:
1. From dashboard, click "Edit Profile"
2. Update information (name, phone, location, experience, bio, image, availability)
3. Save changes
4. Redirected back to dashboard

## Verification System

- **New providers** are created with `is_verified = False`
- **Admin approval required** before providers can receive bookings
- Providers see their verification status on the dashboard
- Admin can approve providers from `/admin/approvals` page

## Security Features

- Passwords are hashed using `werkzeug.security.generate_password_hash`
- Session-based authentication
- Email uniqueness validation
- Phone number uniqueness validation
- Protected routes (redirect to login if not authenticated)

## Integration with Existing System

### Admin Panel Integration:
- Admin can view all providers (including those with portal accounts) at `/admin/workers`
- Admin can approve providers at `/admin/approvals`
- Admin can edit/delete providers
- Verification status is synced across both systems

### Customer-Facing Integration:
- Providers appear in service listings at `/services`
- Only **verified providers** are shown to customers
- Provider ratings, reviews, and stats are displayed
- Customers can book services from verified providers

## File Structure

```
NepSewa/
├── templates/
│   ├── register_provider.html      # Original registration (enhanced)
│   ├── provider_login.html         # Provider login page
│   ├── provider_register.html      # Alternative registration page
│   ├── provider_dashboard.html     # Provider dashboard
│   └── provider_profile.html       # Profile editor
├── main.py                         # Backend routes and API
└── PROVIDER_PORTAL_README.md       # This file
```

## Testing the System

### 1. Register a New Provider:
```
URL: http://127.0.0.1:8000/register-provider
Fill in:
- Name: Test Provider
- Phone: 9801234567
- Email: test@provider.com
- Password: test123
- Service: Home Cleaning
- Location: Kathmandu
- Experience: 2 years
```

### 2. Login to Provider Portal:
```
URL: http://127.0.0.1:8000/provider/login
Email: test@provider.com
Password: test123
```

### 3. View Dashboard:
```
URL: http://127.0.0.1:8000/provider/dashboard
See stats, profile, and quick actions
```

### 4. Edit Profile:
```
URL: http://127.0.0.1:8000/provider/profile
Update information and save
```

## Future Enhancements

Potential features to add:
- Password reset functionality
- Email verification
- Provider booking history
- Earnings tracking and reports
- Customer reviews management
- Availability calendar
- Push notifications for new bookings
- Provider ratings breakdown
- Performance analytics
- Multi-language support

## Notes

- The original registration form at `/register-provider` is **preserved** and **enhanced** with email/password fields
- Providers who register with email/password get access to the portal
- Providers who registered before (without email/password) can contact admin to set up portal access
- The system is backward compatible with existing providers in the database
