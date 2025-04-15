# 🚀 Search Engine 
The matching search engine to my [web crawler](https://github.com/SchBenedikt/web-crawler).

![Search · 4 31pm · 04-12](https://github.com/user-attachments/assets/88c0138a-77c5-440e-a1ce-ae4f583843a5)

## ✨ Features 
- 🌐 **Modern 3D Interactive Landing Page** with full-screen visualizations that dynamically adapt to different screen sizes 
- 🤖 **AI-Powered Answers** providing instant responses with verified sources 
- 📚 **Knowledge Panels** displaying relevant information from Wikipedia and trusted sources 
- ⚡ **Smart Search** with real-time search speed display 
- 📝 **Website Summaries** generated by AI to save reading time 
- 🔍 **Google Integration** for comprehensive search results 
- 🌙 **Dark Mode Support** for comfortable viewing in all lighting conditions 
- 📱 **Responsive Design** optimized for all devices 
- 🗄️ **MongoDB Backend** for efficient data operations 

## 📄 Detailed Feature Overview 
![Capture-2025-04-12-163138](https://github.com/user-attachments/assets/b70ec5c0-a7ea-4c12-8618-42e6ee9afc5a)

### 🌐 Modern 3D Landing Page 
The search engine features a stunning 3D visualization on the landing page created with Three.js. The visualization creates an immersive experience with:
- 🖱️ Dynamic node connections that respond to mouse movements 
- 📱 Responsive design that works across devices 

### 🤖 AI-Powered Features 
The search engine leverages AI for multiple features:
- 💡 **Smart Answers**: Get direct answers to questions without needing to visit multiple websites 
- 📝 **Content Summaries**: AI-generated summaries of web pages to quickly understand their content 
- 🔍 **Query Understanding**: Intelligent parsing of search queries to deliver more relevant results 
![Search](https://github.com/user-attachments/assets/4070ed36-128f-44b1-83f2-06796344a3fb)

### 📚 Knowledge Panels 
Knowledge panels provide quick access to key information about searched topics:
- 🌐 Information from Wikipedia and other trusted sources 
- 📸 Quick facts, images, and related links 
- 🔍 Context-aware information based on search query 

### ⚡ Search Interface 
The search interface is designed for maximum usability:
- 🧼 Clean, distraction-free design 
- 💬 Real-time search suggestions 
- ⏱️ Search speed display 
- 🔍 Filter options for refined results 

### 🛠️ Technical Specifications 
- 🖥️ Built with Flask and modern frontend technologies 
- 🗄️ MongoDB for efficient data storage and retrieval 
- 📱 Responsive Bootstrap-based UI with custom enhancements 
- 🌐 Three.js for 3D visualizations 
- 🌙 Dark mode implementation with CSS variables and prefers-color-scheme media queries 


![image](https://github.com/user-attachments/assets/bd1646eb-cece-4a97-9993-8c3ae4ce90f2)


## 🐳 Docker Instructions 

### 🛠️ Building the Docker Image 

To build the Docker image, run the following command in the root directory of the repository:

```sh
docker build -t ghcr.io/schbenedikt/search-engine:latest .
```

### 🚀 Running the Docker Container 

To run the Docker container, use the following command:

```sh
docker run -p 5560:5560 ghcr.io/schbenedikt/search-engine:latest
```

This will start the Flask application using Gunicorn as the WSGI server, and it will be accessible at `http://localhost:`.

### 📥 Pulling the Docker Image 

The Docker image is publicly accessible. To pull the Docker image from GitHub Container Registry, use the following command:

```sh
docker pull ghcr.io/schbenedikt/search-engine:latest
```

### 📝 Note 
Ensure that the `tags` field in the GitHub Actions workflow is correctly set to `ghcr.io/schbenedikt/search-engine:latest` to avoid multiple packages.

### 🐳 Running with Docker Compose 

To run both the search engine and MongoDB containers using Docker Compose, use the following command:

```sh
docker-compose up
```

This will start both containers and the Flask application will be accessible at `http://localhost:`.

### 📄 Docker Compose File 

The `docker-compose.yml` file is used to manage both the search engine and MongoDB containers. Here is an example of the `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  search-engine:
    image: ghcr.io/schbenedikt/search-engine:latest
    depends_on:
      - mongodb
    ports:
      - "5560:5560"

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
```

### 🗄️ Database Configuration 

The `db_config.json` file is used to store the database configuration. Here is an example of the `db_config.json` file:

```json
[
  {
    "url": "mongodb://localhost:27017",
    "name": "search_engine",
    "username": "your_username",
    "password": "your_password"
  }
]
```

### ⚙️ Settings Page 

The `settings.html` file has been updated to include fields for username and password. You can access the settings page at `http://localhost:5560/settings` to update the database configuration.

## 🛠️ Installation and Setup 

### 📋 Requirements 
- Python 3.10+
- MongoDB (local installation or remote access)
- Modern web browser with JavaScript enabled

### 🚀 Installation Steps 

1. Clone the repository
   ```sh
   git clone https://github.com/SchBenedikt/search-engine.git
   cd search-engine
   ```

2. Create and activate a virtual environment (optional but recommended)
   ```sh
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies
   ```sh
   pip install -r requirements.txt
   ```

4. Configure your database
   - Update the `db_config.json` with your MongoDB credentials
   - Ensure MongoDB is running and accessible

5. Start the application
   ```sh
   python3 app.py
   ```

6. Open your browser and navigate to `http://localhost:5560`

## 📖 Usage Guide 

### 🔍 Basic Search 
1. Enter your query in the search box on the homepage
2. Press Enter or click the search button
3. View the search results, including AI-powered answers and knowledge panels

### ⚙️ Advanced Features 
- **AI Assistance**: Prefix your query with "Ask AI:" to get more detailed AI-generated answers
- **Filter Results**: Use the filter options on the search results page to refine your search
- **Dark Mode**: Toggle dark mode in the settings or let it automatically adjust based on your system preferences
- **Settings Customization**: Visit the settings page to customize your search experience


## 🤝 Contributing 

Contributions are welcome! Please feel free to submit a Pull Request.
