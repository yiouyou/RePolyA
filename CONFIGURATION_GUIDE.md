# Configuration Guide for RePolyA (Research PolyAgents)

This configuration guide ensures you have a seamless experience with RePolyA. The process includes setting up the environment variables and configuring the OpenAI API key.

## Environment Variables

Many applications use environment variables to manage secrets, configurations, and settings. RePolyA uses `.env` files for this purpose. Make sure to never commit sensitive information directly into the source code.

1. **Setting Up .env File**

   In the root directory of the project, create a file named `.env`. This file will store our environment variables.

2. **OpenAI Key Setup**

   To set up the OpenAI key, you'd add the following line to the `.env` file:

   ```
   OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
   ```

   Replace `YOUR_OPENAI_API_KEY_HERE` with your actual OpenAI API key. 

   Note: Always ensure the `.env` file is added to your `.gitignore` to prevent accidentally pushing secrets to public repositories.

3. **Loading Environment Variables**

   You'll need a package to load these variables when the application starts. A commonly used package is `python-dotenv`. If it's not included in the project's `requirements.txt`, install it:

   ```bash
   pip install python-dotenv
   ```

   Then, in the main application file or initialization script, add:

   ```python
   from dotenv import load_dotenv

   load_dotenv()
   ```

   This ensures your environment variables from the `.env` file are loaded when the application starts.

## Additional Configuration

Based on RePolyA's functionalities, there might be other services or settings you need to configure. Ensure to consult the application's documentation or comments in the source code for additional specifics. 

## Troubleshooting

1. **Invalid API Key**: Ensure that the OpenAI API key is correctly copied without any trailing spaces or missing characters.
2. **Environment Variable Issues**: Make sure the `.env` file is in the root directory and that `load_dotenv()` is being called before any environment variable is accessed.

## Conclusion

Configuration is crucial to ensure smooth functioning. By following the steps above, you've equipped RePolyA to efficiently access the OpenAI API and any other services it integrates with. Dive into your research tasks, and if issues arise, refer back to this guide or consult the broader documentation.

---

Note: Always be cautious when dealing with API keys or any other credentials. Never expose them in public forums, repositories, or websites.
