# Web Application for HR Management with RAG Chatbot Integration

This repository contains the source code and documentation for a web-based Human Resource Management System (HRMS) developed during a six-week internship at **MARSA MAROC**. The project digitizes and enhances HR processes, including leave management, event scheduling, and employee interaction, with the integration of an intelligent chatbot powered by Retrieval-Augmented Generation (RAG).

---

## Features

### Core Functionalities
- **Leave Management**:
  - Add, approve, and track leave requests.
  - Automatic calculation of leave balances.
  - Detailed history and report generation.
    ![](https://utfs.io/f/VjzBOjvt3gYi0VrW9jLLOvR7Nfq8boE4VXJCQrBP1YiMds6w)
- **User Management**:
  - Add and manage employee profiles.
  - Import/export employee data using Excel.
  - Role-based access control.
    ![](https://utfs.io/f/VjzBOjvt3gYiGYt9QsRTko5y0j9EMlgvXhA2VY6L3xifwHba)
- **Event Management**:
  - Schedule and manage HR events.
  - Interactive calendar with drag-and-drop functionality.
    ![](https://utfs.io/f/VjzBOjvt3gYicQDOd9k6grJnADvEbS7eo5wPxZXC4tdpi8Hj)

### Chatbot Integration
- **Intelligent Assistance**:
  - A chatbot integrated using Ollama, leveraging RAG for precise, real-time responses.
  - Answers common HR-related queries based on SQL database data.

### User-Friendly Interface
- Developed using:
  - **Flask** for backend development.
  - **HTML, CSS, Bootstrap**, and **JavaScript** for a responsive and accessible frontend.
- Interactive dashboards and animations for enhanced user experience.

---

## Technologies Used
- **Flask**: Lightweight Python web framework.
- **SQLAlchemy**: Database ORM for managing SQL operations.
- **Pandas**: For data manipulation and import/export functionalities.
- **Ollama**: Augmented chatbot service with SQL-based retrieval.
- **Bootstrap**: Frontend framework for responsive design.

---

## Repository Structure
- **Frontend**: HTML, CSS, JavaScript, and Bootstrap-based templates.
- **Backend**: Flask application with modular routes and ORM-based database interactions.
- **Data Management**: Scripts for Excel import/export and database setup.

---

## Deployment
The application is designed to be deployed on any modern server with minimal dependencies. 

---

## Future Enhancements
- Expand chatbot capabilities with advanced NLP features.
- Integrate additional HR modules (e.g., performance tracking).
- Enable multi-language support for diverse teams.

---

## License
This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments
Special thanks to the team at **MARSA MAROC**, particularly the HR department, for their guidance and support during the development of this application.

---

## Installation

1. Clone this repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   pip install -r requirements.txt
   python app.py
   flask run

---

## Contact
For more details or questions, feel free to contact:
- **Author**: Achraf El Bachra
- **LinkedIn**: [Achraf El Bachra](https://www.linkedin.com/in/achraf-el-bachra-8b4aa8139)

