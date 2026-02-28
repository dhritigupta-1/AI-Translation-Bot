# AI-Translation-Bot
🔗 **Live Website:**  
👉 [AI-Translation](https://ai-translation-bot-kb0s.onrender.com)

# Language Translator and Quiz Web Application

This web application allows users to translate text between different languages and test their language skills with a simple quiz. Built using Flask and the Google Translate API.

## Features

* **User Authentication:** Secure registration and login for users.
* **Real-time Translation:** Translate text to a wide range of languages using the `translate` command in the chat interface.
* **Enhanced Meaning Retrieval:** Attempts to provide definitions and meanings for translated words.
* **Language Quiz:** Test your knowledge of basic translations with a randomized quiz.
* **Responsive Interface:** Designed to work on various screen sizes.

## Setup

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install Dependencies:**
    Make sure you have Python and pip installed on your system. Install the required Flask and googletrans libraries:
    ```bash
    pip install Flask googletrans
    ```

3.  **Set Secret Key:**
    The application uses a secret key for session management. While the provided code generates one on the fly, for a production environment, it's recommended to set a strong, persistent secret key as an environment variable or directly in the application configuration.

4.  **Run the Application:**
    ```bash
    python <your_script_name>.py
    ```
    (Replace `<your_script_name>.py` with the actual name of the Python file, e.g., `app.py`)

5.  **Access the Application:**
    Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Usage

1.  **Authentication:**
    * New users can register an account.
    * Existing users can log in.

2.  **Translation:**
    * Once logged in, you'll be taken to the chat interface.
    * To translate text, type `translate <text to translate> to <target language>`. For example: `translate hello to Spanish`.
    * The application will attempt to translate the text and provide a translation along with potential meanings or definitions.
    * You can also try simple greetings and farewells.

3.  **Quiz:**
    * Navigate to the `/quiz` route (e.g., `http://127.0.0.1:5000/quiz`).
    * You will be presented with a short quiz asking you to translate words into a specific language.
    * Select the correct option and submit your answers.
    * The results page will show your score and the correct answers.

4.  **Logout:**
    * Click the "Logout" link to end your session.

## Important Notes

* **Google Translate API:** This application relies on the unofficial `googletrans` library, which uses the public Google Translate API. Please be aware that the usage of this library might be subject to changes or limitations by Google. For production applications, consider using the official Google Cloud Translation API.
* **Security:** The password hashing implemented is basic. For production systems, consider using more robust libraries like `bcrypt` or `argon2` for password management.
* **Error Handling:** The application includes basic error handling, but more comprehensive error management and logging could be implemented for production use.
* **Quiz Data:** The quiz questions are currently hardcoded in the `quiz_data` list. For a more dynamic quiz, consider fetching questions from a database or external source.
* **Language Support:** The application supports a wide range of languages thanks to the `googletrans` library.

## Contributing

Contributions to this project are welcome. Feel free to submit issues or pull requests.

## License

[Specify your license here, e.g., MIT License]
