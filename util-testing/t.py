import pandas as pd
from IPython.display import display, HTML

# Sample data with links
data = [
    {"Name": "Google", "Link": '<a href="http://www.google.com">Visit Google</a>'},
    {"Name": "OpenAI", "Link": '<a href="http://www.openai.com">Visit OpenAI</a>'},
]

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Display the DataFrame with HTML rendering
display(HTML(df.to_html(escape=False)))
