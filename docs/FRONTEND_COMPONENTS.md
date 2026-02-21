# Frontend Components Documentation

## Overview

This document describes the React components that make up the FractureDetect AI frontend application.

## Component Structure

```
src/
├── App.js              # Main application component
├── App.css             # Global styles
├── components/
│   ├── Login.js        # User login component
│   ├── Signup.js       # User registration component
│   ├── History.js      # Report history component
│   ├── Auth.css        # Authentication styles
│   └── History.css     # History styles
```

## Main Application Component

### App.js

The main application component manages the overall state and routing between different views.

**State Management:**
- `file`: Currently selected image file
- `preview`: Base64 preview of selected image
- `result`: Fracture detection results
- `loading`: Loading state during processing
- `showChat`: Visibility of medical assistant chat
- `chatHistory`: Conversation history with AI assistant
- `chatInput`: Current chat message input
- `user`: Authenticated user details
- `currentView`: Current application view ('login', 'signup', 'history', 'app')

**Key Functions:**
- `handleLoginSuccess()`: Handles successful authentication
- `handleSignupSuccess()`: Handles successful registration
- `handleLogout()`: Clears user session
- `handleFileChange()`: Processes image file selection
- `handleUploadAnother()`: Resets for new image upload
- `handleDownloadPDF()`: Generates and downloads PDF report
- `handleSubmit()`: Sends image for fracture detection
- `handleChatSubmit()`: Processes chat messages
- `handleFindHospitals()`: Opens hospital finder

## Authentication Components

### Login Component (Login.js)

**Features:**
- Traditional email/password login
- OTP-based login flow
- Form validation
- Error handling
- Loading states

**Props:**
- `onLoginSuccess`: Callback function for successful login

**State:**
- `email`: User email input
- `password`: User password input
- `isLoading`: Loading state
- `error`: Error message
- `showOTP`: Toggle for OTP flow
- `otp`: OTP input

**Functions:**
- `handleLogin()`: Process email/password authentication
- `handleSendOTP()`: Request OTP via email
- `handleVerifyOTP()`: Verify entered OTP

### Signup Component (Signup.js)

**Features:**
- User registration form
- Patient information collection
- Form validation
- Success feedback
- Navigation to login

**Props:**
- `onSignupSuccess`: Callback function for successful signup

**State:**
- `name`: User full name
- `email`: User email
- `password`: User password
- `phone`: User phone number (optional)
- `age`: User age (optional)
- `isLoading`: Loading state
- `error`: Error message
- `success`: Success state

**Functions:**
- `handleSignup()`: Process user registration

## History Component

### History Component (History.js)

**Features:**
- Display user's report history
- Image previews
- Report filtering and sorting
- Detailed report viewing
- Responsive design

**Props:**
- `user`: Authenticated user details

**State:**
- `reports`: Array of user reports
- `loading`: Loading state
- `error`: Error message

**Functions:**
- `fetchUserReports()`: Retrieve user's reports
- `formatDate()`: Format timestamps for display
- `getStatusBadge()`: Render status indicators

## Styling

### App.css

Global application styles including:
- Dark theme design
- Responsive layouts
- Animation effects
- Typography
- Color scheme

### Auth.css

Styles for authentication components:
- Login/signup cards
- Form elements
- Buttons and links
- Error messages
- Responsive adjustments

### History.css

Styles for report history:
- Report cards
- Grid layout
- Image display
- Status badges
- Responsive design

## Routing

The application uses hash-based routing:
- `#login`: Login view
- `#signup`: Signup view
- `#history`: Report history view
- No hash: Main application view

## Data Flow

1. **Authentication Flow:**
   - User navigates to login/signup
   - Credentials submitted to backend
   - JWT token received and stored
   - User details fetched
   - Main application view loaded

2. **Image Processing Flow:**
   - User selects image file
   - Preview generated
   - File sent to backend for analysis
   - Results displayed
   - Chat and hospital finder enabled

3. **Report Generation Flow:**
   - Results formatted
   - PDF generated with jsPDF
   - File downloaded to user

4. **History Flow:**
   - Reports fetched from backend
   - Displayed in grid layout
   - Images retrieved by ID
   - Reports sorted by date

## Error Handling

Components implement comprehensive error handling:
- Network error detection
- User-friendly error messages
- Form validation
- Graceful degradation
- Loading states

## Performance Considerations

- Lazy loading of images
- Efficient state management
- Memoization of expensive calculations
- Cleanup of event listeners
- Optimized re-renders

## Accessibility

- Semantic HTML structure
- Proper labeling of form elements
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance

## Mobile Responsiveness

- Flexible grid layouts
- Media queries for different screen sizes
- Touch-friendly controls
- Optimized font sizing
- Adaptive image handling

## Future Enhancements

### Planned Improvements
1. **Component Splitting**: Further modularization
2. **State Management**: Redux or Context API integration
3. **Testing**: Unit and integration tests
4. **Animations**: Enhanced micro-interactions
5. **Localization**: Multi-language support