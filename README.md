Careflow Hybrid Agent
A desktop automation assistant designed to navigate Electronic Medical Record (EMR) interfaces using a "Hybrid" approach: Coordinate-based Navigation combined with GPT-4o Vision for data extraction.

This agent runs in a local GUI, clicks through patient tabs (Summary, Consultations, Medications), reads the screen using AI, and generates a medical summary report.

🌟 Features
GUI Chat Interface: A safe, topmost Tkinter window to interact with the agent.

Natural Language Commands: Understands commands like "find info for Diana Rossi" or "search for Elena".

Automated Navigation: Uses pyautogui to physically click tabs and buttons in the target application.

AI Vision Extraction: Takes screenshots of specific tabs and uses OpenAI's GPT-4o to read and structure the medical data.

Crash Protection: Includes custom "Safe Click" logic to handle edge-cases and prevent pyautogui FailSafe crashes during valid movements.
