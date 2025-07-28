# Voice Agent for Twiddles E-commerce Platform

A LiveKit-powered voice assistant for Twiddles, a premium healthy snacking brand. This agent provides customer service, product recommendations, order processing, and feedback collection through natural voice interactions.

## 🚀 Features

- **Voice Interaction**: Real-time speech-to-text and text-to-speech
- **E-commerce Integration**: Product catalog, orders, wishlist management
- **Customer Service**: Personalized recommendations and feedback collection
- **Database Integration**: MongoDB for data persistence
- **Token Server**: FastAPI-based token generation for frontend integration

## 🏗️ Architecture

```
Voice-Agent/
├── main.py              # LiveKit agent entry point
├── token_server.py      # FastAPI token server for frontend
├── tools.py             # E-commerce function tools
├── database.py          # MongoDB database operations
├── prompts.py           # Agent instructions and prompts
├── pyproject.toml       # Project dependencies
└── Dockerfile          # Container configuration
```

## 📋 Prerequisites

- Python 3.12+
- MongoDB database
- LiveKit Cloud account
- Groq API key
- Cartesia API key (for TTS)

## 🛠️ Installation

1. **Clone and setup environment:**
```bash
cd Voice-Agent
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
uv pip install -e .
```

3. **Environment Variables:**
Create a `.env` file with:
```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# AI Services
GROQ_API_KEY=your_groq_api_key
CARTESIA_API_KEY=your_cartesia_api_key

# MongoDB Configuration
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
MONGODB_URL=your_mongodb_cluster_url
```

## 🚀 Running the Application

### 1. Start the Token Server
```bash
python token_server.py
```
Server runs on `http://localhost:8000`

### 2. Start the Voice Agent
```bash
python main.py dev
```

### 3. Frontend Integration
Use the token server to get access tokens for your frontend:

```javascript
// Example frontend integration
const response = await fetch('http://localhost:8000/get-token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'user123',
    email: 'user@example.com'
  })
});

const { token, room_id } = await response.json();
// Use token with LiveKit client
```

## 🔧 API Endpoints

### Token Server (`token_server.py`)

- `POST /get-token` - Generate LiveKit access token
- `GET /health` - Health check
- `GET /` - API information

### Request Format:
```json
{
  "name": "user_id",
  "email": "user@example.com",
  "room_id": "optional_room_id"
}
```

## 🗄️ Database Schema

The application uses MongoDB with the following collections:

- **products**: Product catalog with details, pricing, stock
- **orders**: Customer orders and order history
- **wishlists**: User wishlist items
- **feedback**: Product reviews and ratings
- **users**: Customer profiles and preferences

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t voice-agent .

# Run the container
docker run -p 8080:8080 -p 8000:8000 --env-file .env voice-agent
```

## 🔍 Troubleshooting

### Common Issues:

1. **401 Unauthorized Error**: Check LiveKit API credentials
2. **Database Connection Failed**: Verify MongoDB connection string
3. **Missing Dependencies**: Run `uv pip install -e .` to install all dependencies

### Logs:
- Check application logs for detailed error messages
- Use `python main.py dev` for development mode with verbose logging

## 📝 Development

### Adding New Tools:
1. Add function to `tools.py` with `@function_tool` decorator
2. Update `prompts.py` to include tool usage instructions
3. Add tool to `Assistant` class in `main.py`

### Testing:
```bash
# Run tests (when implemented)
pytest

# Code formatting
black .

# Linting
flake8
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary to Twiddles. All rights reserved.

## 🆘 Support

For technical support or questions, please contact the development team.
