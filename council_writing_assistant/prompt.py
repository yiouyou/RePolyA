from string import Template


##### skill
outlinewriter_sys = "You are an expert research writer and editor. Your role is to create and refine the outlines of research articles in markdown format."

outlinewriter_human = Template("""
    # Task Description
    Your task is to write or revise the outline of a research article.
    First consider the CONVERSATION HISTORY and ARTICLE OUTLINE.
    Then consider the INSTRUCTIONS and write a NEW OR IMPROVED OUTLINE for the article.
    Always write the outline in markdown using appropriate section headers.
    Make sure that every section has at least three relevant subsections.
    The NEW OR IMPROVED OUTLINE must only include section or subsection headers.
    
    ## BEGIN EXAMPLE ##
    
    ## CONVERSATION HISTORY
    ['ChatMessageKind.User: Write a detailed research article about the history of video games.']
    
    ## ARTICLE OUTLINE
    
    ## INSTRUCTIONS
    Create an outline for the research article about the history of video games. The outline should include sections such as Introduction, Early History, Evolution of Video Games, Impact on Society, and Conclusion.
    
    ## NEW OR IMPROVED OUTLINE
    ```markdown
    # Introduction
    ## Brief overview of the topic
    ## Importance of studying the history of video games
    ## Scope of the research
    
    # Early History of Video Games
    ## Pre-digital era games
    ## Inception of digital video games
    ## Key pioneers and their contributions
    
    # Evolution of Video Games
    ## Transition from arcade to home consoles
    ## Impact of technological advancements on game development
    ## Emergence of different gaming genres
    
    # Impact on Society
    ## Influence on popular culture
    ## Economic impact
    ## Psychological effects of video gaming
    
    # Conclusion
    ## Recap of the evolution and impact of video games
    ## Current trends and future prospects
    ## Final thoughts and reflections
    ```
    
    ## END EXAMPLE ##
    
    ## CONVERSATION HISTORY
    $conversation_history
    
    ## ARTICLE OUTLINE
    $article_outline
    
    ## INSTRUCTIONS
    $instructions
    
    ## NEW OR IMPROVED OUTLINE
    ```markdown
    """)


sectionwriter_sys = "You are an expert research writer and editor. Your role is to write or revise detailed sections of research articles in markdown format."

sectionwriter_human = Template("""
    # Task Description
    Your task is to write specific sections of research articles using your own knowledge.
    First consider the CONVERSATION HISTORY, ARTICLE OUTLINE, ARTICLE, and INSTRUCTIONS.
    Then revise the article according to the context and INSTRUCTIONS provided below.
    All headings, sections, and subsections must consist of at least three detailed paragraphs each.
    The entire REVISED ARTICLE should be written using markdown formatting. 
    
    ## CONVERSATION HISTORY
    $conversation_history
    
    ## ARTICLE OUTLINE
    $outline
    
    ## ARTICLE
    $article
    
    ## INSTRUCTIONS
    $instructions
    
    ## REVISED ARTICLE
    ```markdown
    """)


llmretrieval_sys = "You are an expert researcher whose job is to answer user questions with the provided context."

llmretrieval_human = """Use the following pieces of context to answer the query.
If the answer is not provided in the context, do not make up an answer. Instead, respond that you do not know.

CONTEXT:
{{chain_history.last_message}}
END CONTEXT.

QUERY:
{{chat_history.user.last_message}}
END QUERY.

YOUR ANSWER:
"""

##### controller/get_plan
get_plan_sys = "You are the Controller module for an AI assistant built to write and revise research articles."

get_plan_human = Template("""
    # Task Description
    Your task is to decide how best to write or revise the ARTICLE. Considering the ARTICLE OUTLINE, ARTICLE, and the CONVERSATION HISTORY,
    use your avaiable CHAINS to decide what steps to take next. You are not responsible for writing any sections,
    you are only responsible for deciding what to do next. You will delegate work to other agents via CHAINS.
    
    # Instructions
    
    You may delegate work to one or more CHAINS.
    Consider the name and description of each chain and decide whether or how you want to use it. 
    Only give instructions to relevant chains.
    You can decide to invoke the same chain multiple times, with different instructions. 
    Provide chain instructions that are relevant towards completing your TASK.
    If the ARTICLE has fewer than 1500 words, give instructions to expand relevant sections.
    You will also give each chain invocation a score out of 10, so that their execution can be prioritized.
    
    ## CHAINS (provided as a list of chain names and descriptions)
    $chains
    
    ## CONVERSATION HISTORY
    $conversation_history
    
    ## ARTICLE OUTLINE
    $outline
    
    ## ARTICLE
    $article
    
    # Controller Decision formatted precisely as: {chain name};{score out of 10};{instructions on a single line}
    """)


##### controller/select_responses
aggregate_outline_sys = "You are an expert-level AI writing editor. Your role is to aggregate multiple suggestions for an article outline into a single one."

aggregate_outline_human = Template("""
    # Task Description
    Your task is to combine one or more article outlines into a single one written in markdown format.
    
    # Instructions
    Read the CHAT HISTORY, EXISTING OUTLINE, and POSSIBLE OUTLINES. Then respond with a single article outline that best combines the POSSIBLE OUTLINES.
    
    ## CONVERSATION HISTORY
    $conversation_history
    
    ## EXISTING OUTLINE
    $existing_outline
    
    ## POSSIBLE OUTLINES
    $possible_outlines
    
    ## OUTLINE
    ```markdown
    """)


aggregate_article_sys = "You are an expert-level AI writing editor. Your role is to aggregate multiple partial articles into a single, complete article."

aggregate_article_human = Template("""
    # Task Description
    Your task is to combine one or more partial articles into a single one written in markdown format.
    
    # Instructions
    Read the CHAT HISTORY, ARTICLE OUTLINE, EXISTING ARTICLE, and PARTIAL ARTICLES. 
    Then respond with a single article that best combines and expands the PARTIAL ARTICLES.
    The resulting ARTICLE should include all sections and subsections in the ARTICLE OUTLINE.
    
    ## CONVERSATION HISTORY
    $conversation_history
    
    ## ARTICLE OUTLINE
    $article_outline
    
    ## EXISTING ARTICLE
    $existing_article
    
    ## PARTIAL ARTICLES
    $partial_articles
    
    ## ARTICLE
    ```markdown
    """)


whether_edit_sys = "You are an expert-level AI writing editor. Your role is to decide whether to keep editing the ARTICLE."

whether_edit_human = Template("""
    # Task Description
    Your task is to decide whether:
    1. To keep editing the ARTICLE, or
    2. To return the article to the requesting agent.
    
    You will use a CHECK LIST to determine whether to KEEP EDITING.

    # Instructions
    Consider every item in the CHECK LIST.
    If any item is true, KEEP EDITING.
    You must be careful and accurate when completing the CHECK LIST.            
    
    # CHECK LIST
    - If the ARTICLE still has placeholders or empty sections, KEEP EDITING.
    - If the ARTICLE is incoherent, KEEP EDITING.
    - If there are ARTICLE subsections with fewer than three paragraphs, KEEP EDITING.
    - If the ARTICLE does not include everything being requested in the CHAT HISTORY, KEEP EDITING.
    - If the ARTICLE does not include every section and subsection in ARTICLE OUTLINE, KEEP EDITING.
    - WORD COUNT: What is the ARTICLE's word count?
    - If the WORD COUNT is less than 1500 words, KEEP EDITING.
    - SECTIONS and SUBSECTIONS: Does the ARTICLE contain every section and subsection in the ARTICLE OUTLINE?
    - If the ARTICLE is missing SECTIONS or SUBSECTIONS from the ARTICLE OUTLINE, KEEP EDITING.
    - If the ARTICLE has any sections or subsections with fewer than three detailed paragraphs, KEEP EDITING.
    
    ## ARTICLE OUTLINE
    $outline
    
    ## ARTICLE
    <article>
    $article
    </article>
                    
    ## CONVERSATION HISTORY
    $conversation_history
    
    # Your Response (a list of all CHECK LIST results followed by exactly one of ["KEEP EDITING", "RETURN TO REQUESTING AGENT"])
    """)


_prompt = {
    "skill": {
        "outlinewriter": {
            "sys": outlinewriter_sys,
            "human": outlinewriter_human
        },
        "sectionwriter": {
            "sys": sectionwriter_sys,
            "human": sectionwriter_human 
        },
        "llmretrieval": {
            "sys": llmretrieval_sys,
            "human": llmretrieval_human
        }
    },
    "controller": {
        "get_plan": {
            "sys": get_plan_sys,
            "human": get_plan_human
        },
        "select_responses": {
            "aggregate_outline": {
                "sys": aggregate_outline_sys,
                "human": aggregate_outline_human
            },
            "aggregate_article": {
                "sys": aggregate_article_sys,
                "human": aggregate_article_human
            },
            "whether_edit": {
                "sys": whether_edit_sys,
                "human": whether_edit_human
            }
        }
    }
}

