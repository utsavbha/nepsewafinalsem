# NepSewa - Trusted Home Services Platform

🏠 **NepSewa** is a comprehensive home services platform connecting customers with trusted service providers across Nepal.

## ✨ Features

### 🎯 For Customers
- **Service Booking**: Book trusted professionals for home services
- **Provider Search**: Find providers by service type, location, and rating
- **Real-time Filtering**: Filter by availability, rating, and location
- **Secure Payments**: Integrated eSewa payment system
- **Order Tracking**: Track your service requests and history

### 👷 For Service Providers
- **Provider Registration**: Easy signup process with profile creation
- **Provider Portal**: Dedicated dashboard for managing services
- **Profile Management**: Update availability, bio, and service details
- **Order Management**: View and manage customer bookings
- **Verification System**: Admin-approved provider verification

### 🛡️ For Administrators
- **Admin Dashboard**: Comprehensive management interface
- **Provider Approval**: Review and approve new providers
- **Order Management**: Monitor all platform transactions
- **Analytics**: View platform statistics and performance

## 🚀 Services Offered

- 🧹 **Home Cleaning** - Professional cleaning services
- 🔧 **Plumbing** - Pipe repairs, installations, and maintenance
- ⚡ **Electrical** - Wiring, repairs, and installations
- ❄️ **AC Service** - Air conditioning repair and maintenance
- 👩‍🍳 **Maid Service** - Household assistance and cooking
- 🔨 **Technician** - General repairs and maintenance
- ✂️ **Hair Cutting** - Professional barber services at home
- 🌱 **Gardening** - Lawn care and garden maintenance
- 💄 **Makeup Artist** - Beauty services for events
- 📸 **Photography** - Professional photography services

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: MySQL with PyMySQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with dark/light theme support
- **Payments**: eSewa integration
- **Authentication**: Session-based auth system

## 📱 Key Features

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme**: Toggle between themes
- **Gradient Animations**: Beautiful visual effects
- **Provider Dropdown**: Easy access to provider options

### 🔐 Security
- **Password Hashing**: Secure password storage
- **Session Management**: Secure user sessions
- **Input Validation**: Protection against malicious inputs
- **File Upload Security**: Safe image upload handling

### 📊 Smart Features
- **Provider Ranking Algorithm**: Intelligent provider matching
- **Real-time Search**: Instant filtering and sorting
- **Availability Tracking**: Provider schedule management
- **Rating System**: Customer feedback and ratings

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- MySQL 8.0+
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NepSewa
   ```

2. **Install dependencies**
   ```bash
   pip install flask pymysql werkzeug requests
   ```

3. **Setup MySQL Database**
   ```sql
   CREATE DATABASE nepsewa;
   CREATE USER 'root'@'localhost' IDENTIFIED BY 'nepsewa123';
   GRANT ALL PRIVILEGES ON nepsewa.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;
   ```

4. **Run the application**
   ```bash
   python3 run_server.py
   ```

5. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8001`

## 📁 Project Structure

```
NepSewa/
├── main.py                 # Main Flask application
├── run_server.py          # Development server
├── migrate_database.py    # Database migration script
├── orders.json           # Order data storage
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── uploads/         # User uploaded files
├── templates/           # HTML templates
│   ├── nepsewa.html    # Home page
│   ├── services.html   # Services page
│   ├── login.html      # User login
│   ├── provider_*.html # Provider portal pages
│   └── admin_*.html    # Admin dashboard pages
└── README.md           # This file
```

## 🌐 API Endpoints

### Public APIs
- `GET /` - Home page
- `GET /services` - Services listing
- `GET /login` - User login page
- `POST /api/login` - User authentication
- `POST /api/signup` - User registration

### Provider APIs
- `GET /provider/login` - Provider login page
- `POST /api/provider/login` - Provider authentication
- `GET /provider/dashboard` - Provider dashboard
- `GET /provider/profile` - Provider profile management

### Admin APIs
- `GET /admin` - Admin login
- `GET /admin/dashboard` - Admin dashboard
- `GET /orders` - Order management

## 💳 Payment Integration

NepSewa integrates with **eSewa** for secure payments:
- Real-time payment processing
- Automatic order confirmation
- Payment success/failure handling
- Secure transaction logging

## 🎯 Future Enhancements

- [ ] Mobile app development
- [ ] Real-time chat system
- [ ] GPS tracking for providers
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Push notifications
- [ ] Social media integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Developer**: Utsav Bhandari
- **Project**: NepSewa Platform
- **Year**: 2024

## 📞 Support

For support and queries:
- 📧 Email: support@nepsewa.com
- 📱 Phone: +977-9800000000
- 🌐 Website: [NepSewa.com](https://nepsewa.com)

---

**Made with ❤️ in Nepal**

*Connecting communities through trusted home services*# nepsewafinalsem
